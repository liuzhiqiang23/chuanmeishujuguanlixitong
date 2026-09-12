@echo off
REM =====================================================================
REM  movie-system - Python virtual env one-click setup script
REM  Usage: after copying the whole movie-system folder to a new machine,
REM         double-click this file in movie-system root directory.
REM  Prerequisite: Python 3.10 ~ 3.13 installed on the target machine
REM                (https://www.python.org/downloads/, check "Add to PATH")
REM =====================================================================
cd /d "%~dp0"
set VENV=.venv

if exist "%VENV%\Scripts\python.exe" (
  echo [SKIP] %VENV% already exists.
  echo         If you need to rebuild it, delete the .venv folder and rerun this script.
) else (
  echo [1/3] Creating virtual env with Python 3.10-3.13 ...
  py -3.12 -m venv %VENV%
  if errorlevel 1 py -3.11 -m venv %VENV%
  if errorlevel 1 py -3.10 -m venv %VENV%
  if errorlevel 1 py -3.13 -m venv %VENV%
  if errorlevel 1 py -3 -m venv %VENV%
  if errorlevel 1 goto :NO_PY
)

echo [2/3] Upgrading pip ...
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --disable-pip-version-check

echo [3/3] Installing algorithm dependencies (pandas/surprise/lightgbm ...) ...
"%VENV%\Scripts\python.exe" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --disable-pip-version-check
if errorlevel 1 goto :PIP_ERR

echo.
echo [OK] Done! Virtual env is ready at movie-system\.venv
echo      Smoke test: %VENV%\Scripts\python.exe algorithm\recommendation\recommend_api.py --algo demographic
pause
exit /b 0

:NO_PY
echo [ERROR] Python 3.10 / 3.11 / 3.12 / 3.13 not found.
echo         Install one from https://www.python.org/downloads/ (check "Add python.exe to PATH"), then rerun.
pause
exit /b 1

:PIP_ERR
echo [ERROR] pip install failed. Please check network, then rerun this script.
pause
exit /b 1
