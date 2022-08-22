#!/bin/bash

set -eo pipefail

set -a
INK_ENV=${INK_ENV:-.env}
[[ -f "${INK_ENV}" ]] && source "${INK_ENV}"
set +a

[[ -z "$INK_DEBUG" ]] || set -x

INK_VERSION_FEED=https://api.github.com/repos/michel-tricot/ink/releases/latest
INK_BUILD_DIR="build"
INK_CMD="$INK_BUILD_DIR/_ink"
INK_CMDW="ink"

INK_VERSION=${INK_VERSION:-latest}
if [[ "$INK_VERSION" = latest ]]; then
  INK_VERSION=$(curl -sL "${INK_VERSION_FEED}" | jq -r .tag_name)
fi
export INK_VERSION
INK_BASE_URL=${INK_BASE_URL:-https://tools.airbyte.com/${INK_VERSION}}

INK_WRAPPER_URL=${INK_WRAPPER_URL:-${INK_BASE_URL}/ink}
INK_URL=${INK_URL:-${INK_BASE_URL}/_ink}



_error() {
    echo "$@" 1>&2 && exit 1
}

_download_inkw() {
  curl -fsSL "${INK_WRAPPER_URL}" -o "${INK_CMDW}" || _error "Invalid URL: ${INK_WRAPPER_URL}"

  echo "Self-Upgraded ($INK_WRAPPER_URL)"
}

_download_ink() {
    mkdir -p $INK_BUILD_DIR
    curl -fsSL "${INK_URL}" -o "${INK_CMD}" || _error "Invalid URL: ${INK_URL}"
    chmod +x "${INK_CMD}"

    echo "Upgraded ($INK_URL)"
}

main() {
    [[ -z "$INK_SELF_UPGRADE" ]] || { _download_inkw; exit 1; }

    [[ -f "${INK_CMD}" && -z "$INK_UPGRADE" ]] || _download_ink 1>&2

    "${INK_CMD}" "$@"
}

main "$@"
