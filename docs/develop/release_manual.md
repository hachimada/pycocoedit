# Release Manual

## Prerequisites

- directly push to the main branch: prohibited (must be merged via PR)
- development branch name: `feature/xxx`, `fix/xxx`, ...
- **Release Branch**: `release/X.Y.Z` (not `release/vX.Y.Z`)
- **Version**: `X.Y.Zrc1` → `X.Y.Zrc2` → ... → `X.Y.Z` (do not use vX.Y.Z)
- **Deployment**: Deploy to Test PyPI / PyPI when pushing a tag (push) via GitHub Actions

---

## Release Process

### 0. check the main branch

- tests should be passed in the main branch
- all feature branches should be merged

### 1. create branch & update version

- create a new `release/X.Y.Z` branch from `main` branch
    - Don't use `release/vX.Y.Z`
- run the following command to update the version in `pyproject.toml` or just edit it manually.

```bash
poetry version X.Y.Zrc1
```

### 2. commit & push

- push the changes to the `release/X.Y.Z` branch

```bash
git add pyproject.toml
git commit -m "chore: update version to X.Y.Zrc1"
git push origin feature/XXX
```

- create a pull request to the `main` branch. Then tests will be run automatically.
- All tests should be passed before merging the pull request.

### 3. Deploy to Test PyPI

- create a tag for the release candidate version
- tag name must be the same as the version in `pyproject.toml`

```bash
git tag X.Y.Zrc1
git push origin X.Y.Zrc1
````

- this will trigger the GitHub Actions to deploy the package to Test PyPI

### 4. install the package from Test PyPI

- install the package from Test PyPI to check if it works correctly

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pycocoedit==X.Y.Zrc1
```

- if there are any issues, fix them in the `release/X.Y.Z` branch and increment the version to `X.Y.Zrc2` or `X.Y.Zrc3`
  and push the tag again.

### 5. Deploy to PyPI

- once everything is confirmed to be working correctly, change the version in `pyproject.toml` to `X.Y.Z` and push the
  changes.

```bash
poetry version X.Y.Z
git add pyproject.toml
git commit -m "chore: update version to X.Y.Z"
git push origin release/X.Y.Z
git tag X.Y.Z
git push origin X.Y.Z
```
