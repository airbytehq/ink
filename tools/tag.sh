#!/bin/bash

set -eo pipefail



_error() {
    echo "$@" 1>&2 && exit 1
}

_ensure_branch() {
  local expected_branch=$1
  local current_branch=$(git rev-parse --abbrev-ref HEAD)
  [[ "$current_branch" = "$expected_branch" ]] || _error "Must be on $expected_branch"
}

_ensure_clean_tree() {
  local current_tree=$(git status --porcelain)
  [[ -z "$current_tree" ]] || _error "Project tree is not clean\n$current_tree"
}

cmd_pr() {
  _ensure_branch "master"

  git pull
  _ensure_clean_tree

  local bump_type=$1; shift || _error "Missing version bump type"

  poetry version "${bump_type}"

  local version=$(poetry version -s)
  local release_branch=release-$version

  git checkout "$release_branch"
  git commit -am "Bump version"
  git push -u origin "$release_branch"
  gh pr create --title "Release $version" --body ""
}

cmd_tag() {
  echo toto
}

main() {


  local cmd=$1; shift || _error "Missing cmd: [pr, tag]"

  cmd_"$cmd" "$@"

}

main "$@"