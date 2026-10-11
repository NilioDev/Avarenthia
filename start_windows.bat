@echo off
rem Starts Avarenthia with Python. The first run installs what the game needs (about a minute).
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
if not exist ".venv\Scripts\pythonw.exe" (
    echo First start: installing what the game needs...
    %PY% -m venv .venv || goto :nopython
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)
start "" ".venv\Scripts\pythonw.exe" main.py
exit /b 0
:nopython
echo.
echo Python was not found. Install Python 3.10 or newer from python.org
echo and tick "Add python.exe to PATH" during the installation.
pause
exit /b 1
:error
echo.
echo Installation failed. Check your internet connection and try again.
pause
exit /b 1
