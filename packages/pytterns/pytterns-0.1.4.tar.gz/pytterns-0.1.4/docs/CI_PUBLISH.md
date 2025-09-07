GitHub Actions: CI and automatic PyPI publish

What I added
- `.github/workflows/ci.yml` - runs pytest on PRs and pushes to `main` on Python 3.11/3.12.
- `.github/workflows/publish.yml` - publishes to PyPI when `main` is pushed.

Secrets
- Create a repository secret named `PYPI_API_TOKEN` containing a PyPI API token with publish rights.
  - Generate token at https://pypi.org/manage/account/token/
  - Add it under repository Settings -> Secrets and variables -> Actions -> New repository secret

Branch protection
- To require tests pass before merge, enable branch protection on `main` and require status checks to pass.
  - Settings -> Branches -> Add rule for `main`
  - Check "Require status checks to pass before merging" and select the workflow run checks (they appear after first run)

Notes
- `publish.yml` uses `pypa/gh-action-pypi-publish` which builds a distribution and uploads it using the token.
- Adjust Python versions and matrix as needed.
