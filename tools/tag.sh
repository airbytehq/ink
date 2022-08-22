#!/bin/bash

set -eo pipefail

_error() {
    echo -e "$@" 1>&2 && exit 1
}

_ensure_branch() {
  local expected_branch=$1
  local current_branch=$(git rev-parse --abbrev-ref HEAD)
  [[ "$current_branch" = "$expected_branch" ]] || _error "Must be on $expected_branch"
}

_ensure_clean_tree() {
  local current_tree=$(git status --porcelain | grep -v tag)
  [[ -z "$current_tree" ]] || _error "Project tree is not clean\n$current_tree"
}

_prepare() {
  git checkout master
  _ensure_branch master
  git pull
  _ensure_clean_tree
}

cmd_pr() {
  local bump_type=$1; shift || _error "Missing version bump type"

  poetry version "${bump_type}"

  local version=$(poetry version -s)
  local release_branch=release-$version

  git checkout -b "$release_branch"
  git commit -am "Bump version"
  git push -u origin "$release_branch"
  gh pr create --title "Release $version" --body "Releasing $version"
}

cmd_tag() {
  local commit_id=$1; shift || _error "Missing commit id to tag"

  git tag $(poetry version -s) "$commit_id"
  git push --tags
}

main() {
  _prepare

  local cmd=$1; shift || _error "Missing cmd: [pr, tag]"

  cmd_"$cmd" "$@"

}

main "$@"