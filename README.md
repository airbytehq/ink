# Ink: a CLI to build Airbyte Connectors

[![MIT License](https://img.shields.io/badge/license-MIT-brightgreen)](https://github.com/michel-tricot/ink)
[![Tests Status](https://img.shields.io/github/workflow/status/michel-tricot/ink/build)](https://github.com/michel-tricot/ink/workflows/build/badge.svg?branch=master&event=push)
[![Join Our Slack](https://img.shields.io/static/v1?message=Join%20our%20Slack&logo=slack&color=blueviolet&labelColor=grey&label=)](https://slack.airbyte.com)
[![Latest Version](https://img.shields.io/github/v/release/michel-tricot/ink)](https://github.com/michel-tricot/ink)


`ink` creates, builds, tests and manages your Airbyte connector.

## Introduction

To install `ink`: 
```
CONNECTOR_NAME=my-amazing-connector
mkdir source-$CONNECTOR_NAME 
cd source-$CONNECTOR_NAME
curl -fsSLO https://tools.airbyte.com/ink && chmod +x ink
```

Start using `ink`:
```
./ink init $CONNECTOR_NAME
./ink generate --type source-declarative
./ink install
./ink run spec
./ink --help
```

Happy Coding!!

## For maintainers
### Release a new version
1. Create release PR: `./tools/tag.sh pr (major|minor|patch)`
2. After the PR is merged, grab the release PR merge id
3. Tag the merge: `./tools/tag.sh tag [merge id]`
