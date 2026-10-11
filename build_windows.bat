@echo off
rem Builds dist\Avarenthia.exe - a single file you can run without Python.
cd /d "%~dp0"
python -m venv .build-venv || goto :error
call .build-venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller || goto :error
pyinstaller --noconfirm --clean --onefile --windowed --name Avarenthia --add-data "assets;assets" main.py || goto :error
echo.
echo Done: dist\Avarenthia.exe
pause
exit /b 0
:error
echo.
echo Build failed. Is Python 3.10+ on your PATH?
pause
exit /b 1
