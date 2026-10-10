@echo off
rem Builds dist\CursedVale.exe - a single file you can run without Python.
cd /d "%~dp0"
python -m venv .build-venv || goto :error
call .build-venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller || goto :error
pyinstaller --noconfirm --clean --onefile --windowed --name CursedVale --add-data "assets;assets" main.py || goto :error
echo.
echo Klaar: dist\CursedVale.exe
pause
exit /b 0
:error
echo.
echo Bouwen mislukt. Staat Python 3.10+ in je PATH?
pause
exit /b 1
