import subprocess
import os

from ink.const import PROJECT_FILENAME, PROJECT_PATH
from ink.tools import install_airbyte_repo, patch_connector, run_generator, run_pip, get_connector_info, build_connector


def initialize_project():
    if os.path.isfile(PROJECT_FILENAME):
        raise Exception("Project already initialized")
    install_airbyte_repo()
    patch_connector()
    with open(PROJECT_FILENAME, "w") as f:
        f.writelines(["{}"])


def generate_connector():
    install_airbyte_repo()
    run_generator()
    patch_connector()


def install_dependencies():
    run_pip("install", "-r", "requirements.txt")
    run_pip("install", "pyproject-flake8==0.0.1a5")
    run_pip("install", "black==22.3.0")
    run_pip("install", "mypy==0.930")
    run_pip("install", "isort==5.6.4")


def check_project(mypy_fails, warn):
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


def format_project():
    res = subprocess.run(["black", "--config", "pyproject.toml", "."])
    if res.returncode:
        raise Exception("`black` formatting failed")
    subprocess.run(["isort", "--settings-file", "pyproject.toml", "."])
    if res.returncode:
        raise Exception("`isort` formatting failed")


def build_project(image_name, tag):
    image_name = image_name or f"airbyte/{get_connector_info().connector_name}"
    build_connector(image_name, tag)


def test_project(test_args):
    if os.path.isdir("unit_tests"):
        cmd = ["pytest", "-s", "unit_tests"]
        cmd.extend(test_args)
        subprocess.run(cmd)
    else:
        print("No tests found in `unit_tests` 😭")


def run_connector(args):
    cmd = ["python", "main.py"]
    cmd.extend(args)
    subprocess.run(cmd)


def container_run_connector(args):
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


def run_standard_acceptance_tests(sat_args):
    image_name = f"airbyte/{get_connector_info().connector_name}"
    build_connector(image_name, "dev")
    cmd = ["pytest", "-p", "integration_tests.acceptance"]
    cmd.extend(sat_args)
    subprocess.run(cmd)


def publish_connector():
    pass


def encrypt_secrets(passphrase):
    secrets = os.listdir("secrets") if os.path.isdir("secrets") else []
    if not secrets:
        print("No secrets to encrypt")
    else:
        os.makedirs("safe_secrets", exist_ok=True)

        for secret in secrets:
            print(f"🔒 Encrypting secrets/{secret}")
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


def decrypt_secrets(passphrase):
    safe_secrets = os.listdir("safe_secrets") if os.path.isdir("safe_secrets") else []
    if not safe_secrets:
        print("No secrets to decrypt")
    else:
        os.makedirs("secrets", exist_ok=True)

        for safe_secret in safe_secrets:
            print(f"🔓 Decrypting safe_secrets/{safe_secret}")
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
