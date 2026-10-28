@echo off
title CastCheck AI setup
setlocal
echo ================================================
echo   CastCheck AI - one-click setup on D: drive
echo ================================================
echo.

rem ---- already inside the project folder (e.g. a git clone)? set up in place ----
if exist "%~dp0app.py" (
  cd /d "%~dp0"
  echo Project found in %~dp0 - setting up in place.
  python --version >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python was not found. Reinstall Python and tick "Add python.exe to PATH".
    goto :end
  )
  goto :venv
)

rem ---- find the project zip next to this file (browsers may rename it) ----
set "ZIP="
for %%F in ("%~dp0CastCheck_AI*.zip") do set "ZIP=%%~fF"
if not defined ZIP (
  echo [ERROR] CastCheck_AI.zip was not found in this folder:
  echo         %~dp0
  echo Put this setup file and CastCheck_AI.zip in the same folder, then run again.
  goto :end
)
echo Found: %ZIP%

if not exist D:\ (
  echo [ERROR] No D: drive found.
  goto :end
)

python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python was not found. Reinstall Python and tick "Add python.exe to PATH".
  goto :end
)

echo.
echo [1/5] Creating D:\Projects and extracting the project...
if not exist D:\Projects mkdir D:\Projects
powershell -NoProfile -Command "Expand-Archive -LiteralPath '%ZIP%' -DestinationPath 'D:\Projects' -Force"
if not exist D:\Projects\castcheck\app.py (
  echo [ERROR] Extraction failed.
  goto :end
)
cd /d D:\Projects\castcheck

:venv
echo [2/5] Creating the Python environment on D: ...
if not exist .venv\Scripts\python.exe python -m venv .venv
call .venv\Scripts\activate.bat

echo [3/5] Installing packages on D: (a few minutes, needs internet)...
python -m pip install --no-cache-dir --upgrade pip >nul
python -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Package installation failed. Take a screenshot of the text above.
  goto :end
)

echo.
echo [4/5] Running the tests...
python -m pytest -q

echo.
echo [5/5] Starting CastCheck AI in your browser...
echo Keep this window open while you use the app. Close it to stop the app.
echo Next time, just double-click "%CD%\run_castcheck.bat"
echo.
streamlit run app.py

:end
echo.
pause
