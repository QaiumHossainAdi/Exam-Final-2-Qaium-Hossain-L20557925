@echo off
title CastCheck AI
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo The environment is missing. Run setup_castcheck.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
echo Starting CastCheck AI... keep this window open while you use the app.
streamlit run app.py
pause
