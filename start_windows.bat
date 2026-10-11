@echo off
rem Starts Umbrathyn with Python. The first run installs what the game needs (about a minute).
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
if not exist ".venv\Scripts\pythonw.exe" (
    echo Eerste keer opstarten: benodigdheden installeren...
    %PY% -m venv .venv || goto :nopython
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)
start "" ".venv\Scripts\pythonw.exe" main.py
exit /b 0
:nopython
echo.
echo Python is niet gevonden. Installeer Python 3.10 of nieuwer van python.org
echo en vink tijdens de installatie "Add python.exe to PATH" aan.
pause
exit /b 1
:error
echo.
echo Installeren mislukt. Controleer je internetverbinding en probeer het opnieuw.
pause
exit /b 1
