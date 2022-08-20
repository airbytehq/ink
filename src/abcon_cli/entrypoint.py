import logging
import os.path
import subprocess

import click

from abcon_cli.const import PROJECT_FILENAME, PROJECT_PATH
from abcon_cli.tools import (
    build_connector,
    get_connector_info,
    install_airbyte_repo,
    patch_connector,
    run_generator,
    run_pip,
)


@click.group()
@click.option("-d", "--debug", is_flag=True)
def cli(debug):
    """CLI to assist in Airbyte Connector development lifecycle"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)


@cli.command(name="init")
def _init():
    """Initialize Airbyte Connector project"""

    if os.path.isfile(PROJECT_FILENAME):
        raise Exception("Project already initialized")

    install_airbyte_repo()
    patch_connector()

    with open(PROJECT_FILENAME, "w") as f:
        f.writelines(["{}"])


@cli.command(name="generate")
def _generate():
    """Generate Airbyte Connector from template"""

    install_airbyte_repo()
    run_generator()
    patch_connector()


@cli.command(name="install")
def _install():
    """Install Airbyte Connector dependencies"""

    run_pip("install", "-r", "requirements.txt")

    run_pip("install", "pyproject-flake8==0.0.1a5")
    run_pip("install", "black==22.3.0")
    run_pip("install", "mypy==0.930")
    run_pip("install", "isort==5.6.4")


@cli.command(name="check")
@click.option("--warn", is_flag=True, help="Doesn't fail in one check doesn't succeed")
@click.option("--mypy-fails", is_flag=True, help="Fails if mypy doesn't succeed")
def _check(warn, mypy_fails):
    """Run code checks (code style...)"""

    res = subprocess.run(["black", "--config", "pyproject.toml", "--diff", "--quiet", "--check", "."])
    if not warn and res.returncode:
        raise Exception("`black` check failed")

    res = subprocess.run(["pflake8", "--config", "pyproject.toml", "--quiet", "."])
    if not warn and res.returncode:
        raise Exception("`pflake8` check failed")

    res = subprocess.run(["isort", "--settings-file", "pyproject.toml", "--diff", "--quiet", "--check", "."])
    if not warn and res.returncode:
        raise Exception("`isort` check failed")

    res = subprocess.run(["python", "-m", "mypy", "--config-file", "pyproject.toml", "."])
    if not warn and mypy_fails and res.returncode:
        raise Exception("`isort` check failed")


@cli.command(name="format")
def _format():
    """Run code checks (code style...)"""

    res = subprocess.run(["black", "--config", "pyproject.toml", "."])
    if res.returncode:
        raise Exception("`black` formatting failed")
    subprocess.run(["isort", "--settings-file", "pyproject.toml", "."])
    if res.returncode:
        raise Exception("`isort` formatting failed")


@cli.command(name="build")
@click.option("--image-name", help="Image name [default: airbyte/<connector_name>]")
@click.option("--tag", help="Image tag", default="dev", show_default=True)
def _build(image_name, tag):
    """Build Airbyte Connector artifacts (docker img...)"""

    image_name = image_name or f"airbyte/{get_connector_info().connector_name}"
    build_connector(image_name, tag)


@cli.command(name="test")
@click.argument("test_args", nargs=-1)
def _test(test_args):
    """Run Airbyte Connector unit tests"""

    if os.path.isdir("unit_tests"):
        cmd = ["pytest", "-s", "unit_tests"]
        cmd.extend(test_args)
        subprocess.run(cmd)
    else:
        print("No tests found in `unit_tests` 😭")


@cli.command(name="run")
@click.argument("args", nargs=-1)
def _run(args):
    """Run Airbyte Connector"""

    cmd = ["python", "main.py"]
    cmd.extend(args)
    subprocess.run(cmd)


@cli.command(name="container_run")
@click.argument("args", nargs=-1)
def _container_run(args):
    """Run Airbyte Connector from a container"""

    image_name = f"airbyte/{get_connector_info().connector_name}"
    build_connector(image_name, "dev")
    tagged_image = f"{image_name}:dev"

    # allow proper mounting of sample_files & secrets, so it is not necessary to prepend '/'
    res = subprocess.run(["docker", "run", "--rm", "--entrypoint", "pwd", tagged_image], capture_output=True, text=True)
    if res.returncode:
        raise Exception("Unable to fetch image working directory")

    workdir = res.stdout

    mounts = []
    for known_dir in ["secrets", "sample_files", "integration_tests"]:
        mounts.extend(["-v", f"{PROJECT_PATH}/{known_dir}:{workdir}/{known_dir}"])

    cmd = ["docker", "run", "--rm"]
    cmd.extend(mounts)
    cmd.append(tagged_image)
    cmd.extend(args)
    subprocess.run(cmd)


@cli.command(name="sat")
@click.argument("sat_args", nargs=-1)
def _sat(sat_args):
    """Run Standard Acceptance Tests"""

    image_name = f"airbyte/{get_connector_info().connector_name}"
    build_connector(image_name, "dev")

    cmd = ["pytest", "-p", "integration_tests.acceptance"]
    cmd.extend(sat_args)
    subprocess.run(cmd)


@cli.command(name="publish")
def _publish():
    """Publish Airbyte Connector"""
    pass


@cli.group(name="secrets")
def _secrets():
    """Manages secrets in the project"""
    pass


@_secrets.command(name="encrypt")
@click.option("--passphrase", help="Passphrase to use for encryption", required=True, show_envvar=True, envvar="AB_SECRETS_PASSPHRASE")
def _encrypt(passphrase):
    """Encrypt secrets in the `secrets` directory"""

    secrets = os.listdir("secrets") if os.path.isdir("secrets") else []

    if not secrets:
        print("No secrets to encrypt")
        return

    os.makedirs("safe_secrets", exist_ok=True)

    for secret in secrets:
        cmd = [
            "gpg",
            "--passphrase-fd",
            "0",
            "--batch",
            "--yes",
            "-o",
            f"safe_secrets/{secret}.gpg",
            "--symmetric",
            "--cipher-algo",
            "AES256",
            f"secrets/{secret}",
        ]
        subprocess.run(cmd, input=passphrase, encoding="ascii")


@_secrets.command(name="decrypt")
@click.option("--passphrase", help="Passphrase to use for encryption", required=True, show_envvar=True, envvar="AB_SECRETS_PASSPHRASE")
def decrypt(passphrase):
    """Decrypt secrets from the `safe_secrets` directory"""

    safe_secrets = os.listdir("safe_secrets") if os.path.isdir("safe_secrets") else []

    if not safe_secrets:
        print("No secrets to decrypt")
        return

    os.makedirs("secrets", exist_ok=True)

    for safe_secret in safe_secrets:
        cmd = [
            "gpg",
            "--passphrase-fd",
            "0",
            "--batch",
            "--yes",
            "-o",
            f"secrets/{safe_secret.removesuffix('.gpg')}",
            "--decrypt",
            f"safe_secrets/{safe_secret}",
        ]
        subprocess.run(cmd, input=passphrase, encoding="ascii")


@cli.group(name="zdev")
def _dev():
    """Experimental commands"""
    pass


@_dev.command(name="patch-connector")
def _patch_connector():
    """Patch connector"""
    patch_connector()


def main():
    try:
        cli()
    except Exception as e:
        click.echo(e)
        return 1

    return 0
