import os

AIRBYTE_GIT_REPOSITORY = os.environ.get("AIRBYTE_REPOSITORY", "https://github.com/airbytehq/airbyte.git")

PROJECT_PATH = os.getcwd()

PROJECT_FILENAME = "airbyte.yaml"
BUILD_DIRNAME = "build"

BUILD_PATH = os.path.join(PROJECT_PATH, BUILD_DIRNAME)
AIRBYTE_PROJECT_PATH = os.environ.get("AIRBYTE_PROJECT_PATH", os.path.join(BUILD_PATH, "airbyte"))
