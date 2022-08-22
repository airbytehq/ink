# Ink: a CLI to build Airbyte Connectors

[![Tests Status](https://github.com/michel-tricot/ink/workflows/build/badge.svg?branch=master&event=push)](https://github.com/michel-tricot/ink/workflows/build/badge.svg?branch=master&event=push)

`Ink` create, build, test and manage your Airbyte connector.

is your companion CLI for building Airbyte connectors. 

## Introduction

```
CONNECTOR_NAME=my-amazing-connector
mkdir source-$CONNECTOR_NAME
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
