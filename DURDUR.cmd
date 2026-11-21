@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "TEMP=%~dp0work"
set "TMP=%~dp0work"
set "PYTHONDONTWRITEBYTECODE=1"
".venv\Scripts\python.exe" -B launcher.py --stop
if errorlevel 1 pause
