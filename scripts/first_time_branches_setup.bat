:: Installs and builds project
uv sync
uv build

:: Install pre-commit hooks
nox -s pre-commit -- install

:: Update uv.lock
uv update
git add .
git commit --message="chore: run uv update"
git push

:: Creates first release
git switch --create release main
uvx bump-my-version patch
git commit --message="pytest-static 0.0.1" pyproject.toml
git push origin release

:: Switch back to main
git checkout main

:: Create develop branch
git switch -c develop
git push -u origin develop
