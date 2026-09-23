@echo off
rem ============================================================================
rem  movie-system - ONE-CLICK START (Windows)
rem
rem  Usage : double-click this file in the project root (movie-system).
rem
rem  What it does:
rem    [0/3] environment checks  - MySQL 3306, Redis 6379, Python venv,
rem                                best model file, database movie_analytics_db
rem    [1/3] start backend       - delegates to restart_backend.cmd (port 8000,
rem                                loads local_env.cmd secrets, health check)
rem    [2/3] open the browser    - http://localhost:8000/admin
rem    [3/3] print login accounts
rem
rem  Notes:
rem    - Missing pieces are only WARNED about, never auto-installed:
rem        venv missing        -> run setup_venv.cmd
rem        model missing       -> run:
rem            .venv\Scripts\python.exe algorithm\boxoffice_prediction\train_all.py
rem        database missing    -> see the "fresh machine" section of the user manual
rem    - ASCII only on purpose: keeps console output readable on any Windows
rem      codepage (a UTF-8 batch file with LF endings makes cmd.exe misparse).
rem ============================================================================
setlocal
cd /d "%~dp0"

echo ============================================================
echo  movie-system - one-click start
echo  project dir: %CD%
echo ============================================================

echo.
echo [0/3] Environment checks ...
netstat -ano | findstr :3306 | findstr LISTENING >nul
if errorlevel 1 (echo   [WARN] MySQL 3306 is NOT listening - start MySQL first) else (echo   MySQL 3306 OK)
netstat -ano | findstr :6379 | findstr LISTENING >nul
if errorlevel 1 (echo   [WARN] Redis 6379 is NOT listening - start Memurai/Redis first) else (echo   Redis 6379 OK)

if exist ".venv\Scripts\python.exe" (
  echo   Python venv OK  .venv\Scripts\python.exe
) else (
  echo   [WARN] .venv not found - double-click setup_venv.cmd to build it
)

if exist "algorithm\boxoffice_prediction\models\best_model.joblib" (
  echo   Best model OK  algorithm\boxoffice_prediction\models\best_model.joblib
) else (
  echo   [WARN] best_model.joblib not found - online prediction fails until trained:
  echo          .venv\Scripts\python.exe algorithm\boxoffice_prediction\train_all.py
)

rem Database check: only when a mysql client is found on PATH or in the usual place.
set "MYSQL_BIN="
where mysql >nul 2>nul && set "MYSQL_BIN=mysql"
if not defined MYSQL_BIN if exist "D:\ruanjian\MySQL\bin\mysql.exe" set "MYSQL_BIN=D:\ruanjian\MySQL\bin\mysql.exe"
if defined MYSQL_BIN (
  "%MYSQL_BIN%" -uroot -p123456 -N -e "SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='movie_analytics_db';" 2>nul | findstr 1 >nul
  if errorlevel 1 (
    echo   [WARN] database movie_analytics_db not found - see user manual section 4.2
  ) else (
    echo   Database movie_analytics_db OK
  )
) else (
  echo   [SKIP] mysql client not found on PATH - database check skipped
)

echo.
echo [1/3] Starting backend (port 8000, log: _boot.log) ...
call "%~dp0restart_backend.cmd" -nopause

echo.
echo [2/3] Opening browser: http://localhost:8000/admin
start "" "http://localhost:8000/admin"

echo.
echo [3/3] Login accounts:
echo   admin   : see user manual section 3 / DB table t_user
echo   student : student / 123456
echo.
echo ------------------------------------------------------------
echo  Started. Stop the backend by closing the minimized Maven window
echo  or by running restart_backend.cmd again.
echo ------------------------------------------------------------

endlocal
pause
