@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "TEMP=%~dp0work"
set "TMP=%~dp0work"
set "PYTHONDONTWRITEBYTECODE=1"
if not exist "work" mkdir work
if not exist ".venv\Scripts\python.exe" (
 echo Once KUR.cmd dosyasini calistirin.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -B launcher.py
if errorlevel 1 pause
