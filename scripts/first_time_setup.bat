:: Make sure to create the repo prior to running
git init
git add .
git commit -m "feat: initial project structure"

:: Create main branch
git branch -M main
git remote add origin https://github.com/56kyle/pytest-static.git
git push -u origin main

:: Install with uv
uv python install 3.9
uv python pin 3.9
uv run .\scripts\first_time_branches_setup.bat
