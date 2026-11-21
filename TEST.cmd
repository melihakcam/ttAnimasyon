@echo off
cd /d "%~dp0"
set "TEMP=%~dp0work"
set "TMP=%~dp0work"
set "PYTHONDONTWRITEBYTECODE=1"
set "PLAYWRIGHT_BROWSERS_PATH=%~dp0runtime\browsers"
echo BASLAT.cmd kapali olmali. Testler sahneyi sifirlar.
".venv\Scripts\python.exe" -B tests\run_all.py
pause
