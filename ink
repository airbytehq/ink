#!/bin/bash

set -eo pipefail

set -a
ENV_PATH=${ENV_PATH:-.env}
[[ -f "${ENV_PATH}" ]] && source "${ENV_PATH}"
set +a

[[ -z "$DEBUG" ]] || set -x

DEV_VERSION=${DEV_VERSION:-latest}
INK_URL=${INK_URL:-https://tools.airbyte.com/${DEV_VERSION}/ink}

BUILD_DIR="build"
INK_CMD="$BUILD_DIR/_ink"

_error() {
    echo "$@" 1>&2 && exit 1
}

_download_con() {
    mkdir -p $BUILD_DIR
    curl -fsSL "$INK_URL" -o "${INK_CMD}" || _error "Invalid URL: ${INK_URL}"
    chmod +x "${INK_CMD}"
    echo "Upgraded ($INK_URL)"
}

main() {
    [[ -f "${INK_CMD}" && -z "$INK_UPGRADE" ]] || _download_con 1>&2

    "${INK_CMD}" "$@"
}

main "$@"
