import json
import subprocess
import sys
from pathlib import Path

import ansible_runner
import pandas as pd
import yaml
from colorama import Fore, Style
from cookiecutter.main import cookiecutter
from loguru import logger
from pydantic import ValidationError
from tabulate import tabulate

from .models import AppConfig, MaestroConfig

logger_format = "<level>{message}</level>"
logger.configure(extra={"ip": "", "user": ""})  # Default values
logger.remove()
logger.add(sys.stderr, format=logger_format)

CONFIG_NAME = "maestro.yaml"
CONFIG_DIR = "."
APPLICATIONS_DIR = "applications"
DOCKER_COMPOSE_FILES = ["docker-compose.yaml", "docker-compose.yml"]
SHOW_STATUS_COLUMNS = [
    "priority",
    "enable",
    "status",
    "application",
    "container",
    "tags",
    "hosts",
]
NO_STATUS_COLUMNS = ["priority", "enable", "application", "tags", "hosts"]

STATUS_COLOR_MAP = {
    "created": Fore.BLUE,
    "started": Fore.CYAN,
    "restarting": Fore.RED,
    "exited": Fore.RED,
    "running": Fore.GREEN,
    "not running": Fore.LIGHTBLACK_EX,
}

ENABLED_COLOR_MAP = {True: Fore.GREEN, False: Fore.RED}


def format_color(state: str, color_map: dict):
    return color_map[state] + str(state) + Style.RESET_ALL


def load_maestro_config(
    root_dir: Path, config_name: str = CONFIG_NAME
) -> MaestroConfig:
    params_path = root_dir / config_name
    params_yaml = yaml.safe_load(params_path.read_text())
    return MaestroConfig(**params_yaml)


def load_app_config(app_dir: Path) -> AppConfig:
    for compose_file in DOCKER_COMPOSE_FILES:
        try:
            config_path = app_dir / compose_file
            compose_yaml = yaml.safe_load(config_path.read_text())
            maestro_labels = get_maestro_labels(compose_yaml=compose_yaml)
            if maestro_labels:
                try:
                    return AppConfig(
                        **maestro_labels,
                        application=app_dir.name,
                        application_dir=str(app_dir),
                    )
                except ValidationError as e:
                    logger.error(f"Validation error in {app_dir}/{compose_file}: {e}")
                    return None
        except FileNotFoundError:
            pass
    logger.info(f"No docker-compose file with maestro tags found in {app_dir}")
    return None


def get_applications(
    base_dir: Path, maestro_config: MaestroConfig, show_all: bool = False
):
    apps = []
    for app_dir in base_dir.iterdir():
        if app_dir.is_dir():
            config = load_app_config(app_dir)
            if config:
                apps.append(config.dict())
    apps_df = pd.DataFrame(apps)
    if not show_all:
        apps_df = apps_df[apps_df["enable"]]
        apps_df = filter_dataframe(
            df=apps_df,
            column_name="hosts",
            include=maestro_config.hosts.include,
            exclude=maestro_config.hosts.exclude,
        )
        apps_df = filter_dataframe(
            df=apps_df,
            column_name="tags",
            include=maestro_config.tags.include,
            exclude=maestro_config.tags.exclude,
        )
    if not apps_df.empty:
        apps_df = apps_df.sort_values(
            ["priority", "application"], ascending=[True, True]
        )
    return apps_df


def get_containers_status():
    docker_command = ["docker", "ps", "--format", "json"]
    result = subprocess.run(docker_command, capture_output=True, text=True, check=True)

    if result.stdout.startswith("["):
        containers = json.loads(result.stdout)
    else:
        containers = [json.loads(s) for s in result.stdout.splitlines()]

    all_labels = []
    for container in containers:
        formatted_labels = {}
        labels = container["Labels"].split(",")
        for l in labels:
            if "=" in l:
                try:
                    k, v = l.split("=")
                    formatted_labels[k] = v
                except:
                    pass
        all_labels.append(
            {
                "application": formatted_labels["com.docker.compose.project"],
                "container": container["Names"],
                "status": format_color(container["State"], STATUS_COLOR_MAP),
            }
        )
    return pd.DataFrame(all_labels, columns=["application", "container", "status"])


def filter_dataframe(df, column_name, include, exclude):
    if df.empty:
        return df

    def should_include(row):
        # If include is empty or contains '*', include the row
        if not include or "*" in include:
            return True
        # Include if any element in the row is in the include list
        return any(item in include for item in row)

    def should_exclude(row):
        # Exclude if any element in the row is in the exclude list
        return any(item in exclude for item in row)

    # Apply the inclusion and exclusion filters
    df_filtered = df[df[column_name].apply(should_include)]
    df_filtered = df_filtered[~df_filtered[column_name].apply(should_exclude)]

    return df_filtered


def get_maestro_labels(compose_yaml: dict, maestro_key: str = "maestro."):
    maestro_labels = {}
    for data in compose_yaml["services"].values():
        if "labels" in data.keys():
            for label in data["labels"]:
                if isinstance(label, dict):
                    if any(maestro_key in k for k in label.keys()):
                        maestro_labels.update(label)
                elif isinstance(label, str):
                    k, v = label.split("=")
                    if maestro_key in k:
                        maestro_labels[k] = v
                else:
                    raise ValueError(f"Label {label} in unsupported format")
    maestro_labels = {k.replace(maestro_key, ""): v for k, v in maestro_labels.items()}
    if "tags" in maestro_labels:
        maestro_labels["tags"] = maestro_labels["tags"].split(",")
    if "hosts" in maestro_labels:
        maestro_labels["hosts"] = maestro_labels["hosts"].split(",")
    return maestro_labels


def execute_make(app_dir: Path, command: str):
    subprocess.run(["make", command], cwd=app_dir)


def up_command(applications_dir: str, config_file: str, dry_run: bool):
    apps_df = get_applications(
        base_dir=Path(applications_dir),
        maestro_config=load_maestro_config(
            root_dir=Path(CONFIG_DIR), config_name=config_file
        ),
    )
    for _, row in apps_df.iterrows():
        logger.info(Fore.BLUE + f"Starting {row.application}".upper() + Style.RESET_ALL)
        if not dry_run:
            execute_make(row.application_dir, "up")


def down_command(applications_dir: str, config_file: str, dry_run: bool):
    apps_df = get_applications(
        base_dir=Path(applications_dir),
        maestro_config=load_maestro_config(
            root_dir=Path(CONFIG_DIR), config_name=config_file
        ),
    )
    apps_df = apps_df[::-1]
    for _, row in apps_df.iterrows():
        logger.info(Fore.BLUE + f"Stopping {row.application}".upper() + Style.RESET_ALL)
        if not dry_run:
            execute_make(row.application_dir, "down")


def list_command(
    applications_dir: str,
    config_file: str,
    show_status: bool,
    show_all: bool,
):
    columns = SHOW_STATUS_COLUMNS if show_status else NO_STATUS_COLUMNS
    maestro_config = load_maestro_config(
        root_dir=Path(CONFIG_DIR), config_name=config_file
    )
    apps_df = get_applications(
        base_dir=Path(applications_dir),
        maestro_config=maestro_config,
        show_all=show_all,
    )
    merged = apps_df.copy()
    if show_status:
        join_how = "outer" if show_all else "left"
        status_df = get_containers_status()
        merged = status_df.merge(merged, on="application", how=join_how)
        merged[["container"]] = merged[["container"]].fillna(value="")
        merged[["status"]] = merged[["status"]].fillna(
            value=format_color("not running", STATUS_COLOR_MAP)
        )
        merged = merged.dropna()
        if merged.empty:
            merged = apps_df
            if show_status:
                merged["status"] = format_color("not running", STATUS_COLOR_MAP)
                merged["container"] = ""

    if not show_all:
        merged = merged[merged["enable"]]
    merged["enable"] = merged.enable.apply(
        lambda x: format_color(state=x, color_map=ENABLED_COLOR_MAP)
    )
    merged = merged[columns]
    merged = merged.sort_values(["priority", "application"], ascending=[True, True])
    formatted = merged.to_dict(orient="records")

    logger.info(Fore.BLUE + "HOSTS CONFIG" + Style.RESET_ALL)
    logger.info(tabulate(maestro_config.hosts.dict(), headers="keys"))
    logger.info("\n")
    logger.info(Fore.BLUE + "TAGS CONFIG" + Style.RESET_ALL)
    logger.info(tabulate(maestro_config.tags.dict(), headers="keys"))
    logger.info("\n")
    logger.info(Fore.BLUE + "SERVICES" + Style.RESET_ALL)
    logger.info(tabulate(formatted, headers="keys"))


def new_command(
    config_file: str,
    service_name: str,
    local_service: bool,
    public_service: bool,
    pyservice: bool,
):
    maestro_config = load_maestro_config(
        root_dir=Path(CONFIG_DIR), config_name=config_file
    )
    maestro_config.service.config.service_name = service_name.replace("_", "-")
    maestro_config.service.config.local = local_service
    maestro_config.service.config.public = public_service
    maestro_config.service.config.pyservice = pyservice

    logger.info("Cloning template")
    cookiecutter(
        template=maestro_config.service.cookiecutter.source,
        directory=maestro_config.service.cookiecutter.directory,
        no_input=True,
        extra_context=maestro_config.service.config.dict(),
        output_dir=maestro_config.service.config.output_dir,
    )

    with open(maestro_config.service.ansible.playbook, "r") as f:
        playbook = yaml.safe_load(f)

    with open(maestro_config.service.ansible.inventory, "r") as f:
        inventory = yaml.safe_load(f)

    logger.info("Running ansible playbook")
    ansible_runner.run(
        playbook=playbook,
        inventory=inventory,
        extravars=maestro_config.service.config.dict(),
    )
