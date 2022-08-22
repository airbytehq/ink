# Ink: a CLI to build Airbyte Connectors

[![Tests Status](https://img.shields.io/github/workflow/status/michel-tricot/ink/build)](https://github.com/michel-tricot/ink/workflows/build/badge.svg?branch=master&event=push)
[![Join Our Slack](https://img.shields.io/static/v1?message=Join%20our%20Slack&logo=slack&color=blueviolet&labelColor=grey&label=)](https://slack.airbyte.com)

`Ink` create, build, test and manage your Airbyte connector.

## Introduction

```
CONNECTOR_NAME=my-amazing-connector
mkdir source-$CONNECTOR_NAME
cd source-$CONNECTOR_NAME
curl -fsSLO https://tools.airbyte.com/ink && chmod +x ink
./ink init $CONNECTOR_NAME
./ink generate --type source-declarative
./ink install
./ink run spec
```

Happy Coding!!


## Release new version
1. Bump version: `poetry version [type of version bump]`
2. Create a new branch: `release-$(poetry version -s)`
3. Commit & Push bump changes
4. Create a pull request with the title `Release [version_name]`
5. Once PR is merged:
   1. `git checkout master && git pull`
   2. find the PR merge commit digest
   3. Tag digest: `git tag $(poetry version -s) [digest]`
   4. Push Tag: `git push --tags` 
