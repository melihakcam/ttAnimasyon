@echo off
cd /d "%~dp0"
set "TEMP=%~dp0work"
set "TMP=%~dp0work"
set "PYTHONDONTWRITEBYTECODE=1"
set "PIP_CACHE_DIR=%~dp0runtime\pip-cache"
if not exist "work" mkdir work
if not exist ".venv\Scripts\python.exe" python -B -m venv .venv
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -B -m pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
if errorlevel 1 goto fail
echo Kurulum tamam. BASLAT.cmd dosyasini acin.
pause
exit /b 0
:fail
echo Kurulum basarisiz. Python 3.10 veya ustu ve internet baglantisini kontrol edin.
pause
exit /b 1
