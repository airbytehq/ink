import logging

import click

from ink.operations import (
    build_project,
    check_project,
    container_run_connector,
    decrypt_secrets,
    encrypt_secrets,
    format_project,
    generate_connector,
    initialize_project,
    install_dependencies,
    publish_connector,
    run_connector,
    run_standard_acceptance_tests,
    test_project,
)
from ink.tools import patch_connector


@click.group()
@click.option("-d", "--debug", is_flag=True, show_envvar=True, envvar="INK_DEBUG")
def cli(debug):
    """CLI to assist in Airbyte Connector development lifecycle"""

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug flag activated")


@cli.command(name="init")
def _init():
    """Initialize Airbyte Connector project"""

    initialize_project()


@cli.command(name="generate")
def _generate():
    """Generate Airbyte Connector from template"""

    generate_connector()


@cli.command(name="install")
def _install():
    """Install Airbyte Connector dependencies"""

    install_dependencies()


@cli.command(name="check")
@click.option("--warn", is_flag=True, help="Doesn't fail in one check doesn't succeed")
@click.option("--mypy-fails", is_flag=True, help="Fails if mypy doesn't succeed")
def _check(warn, mypy_fails):
    """Run code checks (code style...)"""

    check_project(mypy_fails, warn)


@cli.command(name="format")
def _format():
    """Run code checks (code style...)"""

    format_project()


@cli.command(name="build")
@click.option("--image-name", help="Image name [default: airbyte/<connector_name>]")
@click.option("--tag", help="Image tag", default="dev", show_default=True)
def _build(image_name, tag):
    """Build Airbyte Connector artifacts (docker img...)"""

    build_project(image_name, tag)


@cli.command(name="test")
@click.argument("test_args", nargs=-1)
def _test(test_args):
    """Run Airbyte Connector unit tests"""

    test_project(test_args)


@cli.command(name="run")
@click.argument("args", nargs=-1)
def _run(args):
    """Run Airbyte Connector"""

    run_connector(args)


@cli.command(name="container_run")
@click.argument("args", nargs=-1)
def _container_run(args):
    """Run Airbyte Connector from a container"""

    container_run_connector(args)


@cli.command(name="sat")
@click.argument("sat_args", nargs=-1)
def _sat(sat_args):
    """Run Standard Acceptance Tests"""

    run_standard_acceptance_tests(sat_args)


@cli.command(name="publish")
def _publish():
    """Publish Airbyte Connector"""

    publish_connector()


@cli.group(name="secrets")
def _secrets():
    """Manages secrets in the project"""
    pass


@_secrets.command(name="encrypt")
@click.option("--passphrase", help="Passphrase to use for encryption", required=True, show_envvar=True, envvar="AB_SECRETS_PASSPHRASE")
def _encrypt(passphrase):
    """Encrypt secrets in the `secrets` directory"""

    encrypt_secrets(passphrase)


@_secrets.command(name="decrypt")
@click.option("--passphrase", help="Passphrase to use for encryption", required=True, show_envvar=True, envvar="AB_SECRETS_PASSPHRASE")
def decrypt(passphrase):
    """Decrypt secrets from the `safe_secrets` directory"""

    decrypt_secrets(passphrase)


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
