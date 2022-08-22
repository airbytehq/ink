import os


AIRBYTE_GIT_REPOSITORY = os.environ.get("INK_AIRBYTE_REPOSITORY", "https://github.com/airbytehq/airbyte.git")
AIRBYTE_GIT_BRANCH = os.environ.get("INK_AIRBYTE_BRANCH", None)

PROJECT_PATH = os.getcwd()

PROJECT_FILENAME = "airbyte.yaml"
BUILD_DIRNAME = os.environ.get("INK_BUILD_DIR", "build")

BUILD_PATH = os.path.join(PROJECT_PATH, BUILD_DIRNAME)
AIRBYTE_PROJECT_PATH = os.environ.get("INK_AIRBYTE_PROJECT_PATH", os.path.join(BUILD_PATH, "airbyte"))
