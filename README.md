# Ink



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
