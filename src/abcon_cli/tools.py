import fileinput
import logging
import os
import shutil
import subprocess

from dataclasses import dataclass

import yaml

from abcon_cli.const import (
    AIRBYTE_GIT_REPOSITORY,
    AIRBYTE_PROJECT_PATH,
    BUILD_DIRNAME,
    BUILD_PATH,
    PROJECT_FILENAME,
    PROJECT_PATH,
)


@dataclass
class ConnectorInfo:
    connector_name: str


def get_connector_info() -> ConnectorInfo:
    with open(PROJECT_FILENAME, "r") as f:
        info = yaml.safe_load(f)
    return ConnectorInfo(**info)


def patch_connector():
    print("Patching connector")

    for f in ["build.gradle", "acceptance-test-docker.sh", "__init__.py"]:
        if os.path.exists(f):
            os.remove(f)

    with open(".python-version", "w") as f:
        f.writelines(["3.9.0"])

    shutil.copy(os.path.join(AIRBYTE_PROJECT_PATH, "pyproject.toml"), "")

    if os.path.exists("requirements.txt"):
        with fileinput.input(files=["requirements.txt"], inplace=True) as f:
            for line in f:
                rel_path = os.path.relpath(AIRBYTE_PROJECT_PATH, PROJECT_PATH)
                line = line.replace("../../..", rel_path)
                line = line.replace("../..", os.path.join(rel_path, "airbyte-integrations"))
                line = line.replace("..", os.path.join(rel_path, "airbyte-integrations", "connectors"))
                print(line, end="")

    if os.path.exists("acceptance-test-config.yml") and os.path.exists(PROJECT_FILENAME):
        with open("acceptance-test-config.yml", "r") as atc, open(PROJECT_FILENAME, "r") as prj:
            yaml_atc = yaml.safe_load(atc)
            yaml_prj = yaml.safe_load(prj) or {}

        with open(PROJECT_FILENAME, "w") as prj:
            yaml_prj["connector_name"] = yaml_atc["connector_image"].split("/")[1].split(":")[0]
            yaml.safe_dump(yaml_prj, prj)


def run_generator():
    generator_path = os.path.join(AIRBYTE_PROJECT_PATH, "airbyte-integrations", "connector-templates", "generator")
    res = subprocess.run(["./generate.sh"], cwd=generator_path)
    if res.returncode > 0:
        raise Exception(f"Failed to use connector generator")

    res = subprocess.run(["git", "status", "--porcelain"], cwd=AIRBYTE_PROJECT_PATH, capture_output=True, text=True)
    if res.returncode > 0:
        raise Exception(f"Failed identify generated connector")
    raw_paths = [os.path.join(AIRBYTE_PROJECT_PATH, os.path.normpath(p[3:])) for p in res.stdout.splitlines()]
    filtered_paths = []
    for p in raw_paths:
        parent = os.path.dirname(p)
        if os.path.isdir(p) and os.path.basename(parent) == "connectors":
            filtered_paths.append(p)

    if len(filtered_paths) != 1:
        raise Exception(f"Airbyte project is not in a good state, found following paths: {filtered_paths}")

    generated_path = filtered_paths.pop()
    logging.debug(f"Generated connector path: {generated_path}")
    for f in os.listdir(generated_path):
        p = os.path.join(generated_path, f)
        shutil.move(p, PROJECT_PATH)


def install_airbyte_repo():
    os.makedirs(BUILD_DIRNAME, exist_ok=True)

    if not os.path.isdir(AIRBYTE_PROJECT_PATH):
        logging.debug(f"Cloning git repo: {AIRBYTE_GIT_REPOSITORY}")
        res = subprocess.run(["git", "clone", AIRBYTE_GIT_REPOSITORY], cwd=BUILD_PATH)
        logging.debug(f"Cloning git repo complete: {res}")
        if res.returncode > 0:
            raise Exception(f"Failed to install Airbyte project: {AIRBYTE_GIT_REPOSITORY}")

    logging.debug(f"Refreshing git repo: {AIRBYTE_PROJECT_PATH}")
    res = subprocess.run(["git", "pull"], cwd=AIRBYTE_PROJECT_PATH)
    logging.debug(f"Refreshing git repo complete: {res}")
    if res.returncode > 0:
        raise Exception(f"Failed to refresh Airbyte project: {AIRBYTE_PROJECT_PATH}")


def run_pip(*args):
    cmd = ["pip"]
    cmd.extend(args)
    res = subprocess.run(cmd)
    if res.returncode > 0:
        raise Exception(f"Failed run pip")


def build_connector(image_name, tag):
    res = subprocess.run(["docker", "build", ".", "-t", f"{image_name}:{tag}"])
    if res.returncode:
        raise Exception("Failed to build connector")
