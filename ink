#!/bin/bash

set -eo pipefail

# Export all env variables
set -a
INK_ENV=${INK_ENV:-.env}
[[ -f "${INK_ENV}" ]] && source "${INK_ENV}"
set +a

[[ -z "$INK_DEBUG" ]] || set -x

# Constants
INK_VERSION_FEED=https://api.github.com/repos/airbytehq/ink/releases/latest
INK_BUILD_DIR="build"
INK_CMD="$INK_BUILD_DIR/_ink"
INK_CMDW="ink"

# Figure out version & tools URLs
INK_VERSION=${INK_VERSION:-latest}
if [[ "$INK_VERSION" = latest ]]; then
  INK_VERSION=$(curl -sL "${INK_VERSION_FEED}" | jq -r .tag_name)
fi
export INK_VERSION
INK_BASE_URL=${INK_BASE_URL:-https://tools.airbyte.com/ink/${INK_VERSION}}
INK_CMDW_URL=${INK_CMDW_URL:-${INK_BASE_URL}/ink}
INK_CMD_URL=${INK_CMD_URL:-${INK_BASE_URL}/_ink}

_error() {
    echo "$@" 1>&2 && exit 1
}

_download_inkw() {
  curl -fsSL "${INK_CMDW_URL}" -o "${INK_CMDW}" || _error "Invalid URL: ${INK_CMDW_URL}"
  chmod +x "${INK_CMDW}"

  echo "Self-Upgraded ($INK_CMDW_URL)"
}

_download_ink() {
    mkdir -p $INK_BUILD_DIR
    curl -fsSL "${INK_CMD_URL}" -o "${INK_CMD}" || _error "Invalid URL: ${INK_CMD_URL}"
    chmod +x "${INK_CMD}"

    echo "Upgraded ($INK_CMD_URL)"
}

main() {
    [[ -z "$INK_SELF_UPGRADE" ]] || { _download_inkw; exit 1; }

    [[ -f "${INK_CMD}" && -z "$INK_UPGRADE" ]] || _download_ink 1>&2

    "${INK_CMD}" "$@"
}

main "$@"
