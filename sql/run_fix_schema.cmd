@echo off
rem =====================================================================
rem  run_fix_schema.cmd
rem  Execute fix_schema.sql with utf8mb4 charset (avoid ERROR 1366 on Windows).
rem  Usage: double-click this file, then input MySQL root password.
rem  NOTE: if your database name is not vidio_mangage_db, edit the line
rem  "set DBNAME=vidio_mangage_db" below.
rem =====================================================================
chcp 65001 >nul
cd /d "%~dp0"
set DBNAME=vidio_mangage_db
mysql --default-character-set=utf8mb4 -uroot -p %DBNAME% < fix_schema.sql
echo.
echo =====================================================================
if %errorlevel%==0 (
    echo [OK] Schema fix completed.
    echo Please restart the backend service, then refresh the web page.
) else (
    echo [FAILED] error code %errorlevel%. Please check the message above.
)
echo =====================================================================
pause
