:: Installs and builds project
poetry install --with dev
poetry build

:: Install pre-commit hooks
nox -s pre-commit -- install

:: Update poetry.lock
poetry update
git add .
git commit --message="Runs poetry update."
git push

:: Creates first release
git switch --create release main
poetry version patch
git commit --message="pytest-static 0.0.1" pyproject.toml
git push origin release

:: Switch back to main
git checkout main

:: Create develop branch
git switch -c develop
git push -u origin develop
