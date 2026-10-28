@echo off
title CastCheck AI setup
cd /d "%~dp0"
echo Creating the Python environment...
python -m venv .venv || (echo Python 3.10+ is required. & pause & exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Setup finished. Double-click run_castcheck.bat to start the app.
pause
