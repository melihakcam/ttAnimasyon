@echo off
cd /d "%~dp0"
set "TEMP=%~dp0work"
set "TMP=%~dp0work"
set "PYTHONDONTWRITEBYTECODE=1"
if not exist "work" mkdir work
".venv\Scripts\python.exe" -B -m pip install --disable-pip-version-check --no-cache-dir -r requirements-tiktok.txt
if errorlevel 1 echo TikTok kurulumu basarisiz.
pause
