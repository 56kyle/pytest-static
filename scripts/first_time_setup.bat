:: Make sure to create the repo prior to running
git init
git add .
git commit -m "Initial commit."

:: Create main branch
git branch -M main
git remote add origin https://github.com/56kyle/pytest-static.git
git push -u origin main

:: Install poetry
poetry env use %PYTHON39%
poetry run .\scripts\first_time_branches_setup.bat
