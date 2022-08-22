#!/bin/bash

set -eo pipefail

set -a
INK_ENV=${INK_ENV:-.env}
[[ -f "${INK_ENV}" ]] && source "${INK_ENV}"
set +a

[[ -z "$INK_DEBUG" ]] || set -x

INK_VERSION=${INK_VERSION:-latest}
INK_URL=${INK_URL:-https://tools.airbyte.com/${INK_VERSION}/ink}

INK_BUILD_DIR="build"
INK_CMD="$INK_BUILD_DIR/_ink"

_error() {
    echo "$@" 1>&2 && exit 1
}

_download_con() {
    mkdir -p $INK_BUILD_DIR
    curl -fsSL "$INK_URL" -o "${INK_CMD}" || _error "Invalid URL: ${INK_URL}"
    chmod +x "${INK_CMD}"
    echo "Upgraded ($INK_URL)"
}

main() {
    [[ -f "${INK_CMD}" && -z "$INK_UPGRADE" ]] || _download_con 1>&2

    "${INK_CMD}" "$@"
}

main "$@"
