@echo off
cd /d "%~dp0"
set "TEMP=%~dp0work"
set "TMP=%~dp0work"
set "PYTHONDONTWRITEBYTECODE=1"
echo Once BASLAT.cmd acik olmali.
set /p "TIKTOK_USER=TikTok kullanici adi (@ olmadan da olur): "
if not defined TIKTOK_USER exit /b 1
".venv\Scripts\python.exe" -B tiktok_listener.py "%TIKTOK_USER%"
pause
