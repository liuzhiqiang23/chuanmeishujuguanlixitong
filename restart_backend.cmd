@echo off
rem ============================================================================
rem  movie-system - backend one-click restart (Windows)
rem
rem  Usage : double-click this file, or run "restart_backend.cmd" in the
rem          project root (movie-system).
rem  Steps : 0 check MySQL/Redis -> 1 find process on port 8000 and kill it
rem          -> 2 start backend in background (log: _boot.log)
rem          -> 3 wait until port 8000 is listening
rem          -> 4 health check (HTTP page + recommend API)
rem
rem  Note  : -Dmaven.test.skip=true is REQUIRED: src/test still uses JUnit4
rem          annotations while Spring Boot 3.5 ships JUnit5, so test-compile
rem          would fail and abort spring-boot:run.
rem ============================================================================
setlocal

cd /d "%~dp0"

rem Load local secrets (DB password, PWD_KEY_* RSA pair) if present.
if exist "%~dp0local_env.cmd" call "%~dp0local_env.cmd"

echo ============================================================
echo  movie-system backend restart
echo  project dir: %CD%
echo ============================================================

echo.
echo [0/4] Checking middleware ...
netstat -ano | findstr :3306 | findstr LISTENING >nul
if errorlevel 1 (echo   [WARN] MySQL 3306 is NOT listening) else (echo   MySQL 3306 OK)
netstat -ano | findstr :6379 | findstr LISTENING >nul
if errorlevel 1 (echo   [WARN] Redis 6379 is NOT listening) else (echo   Redis 6379 OK)

echo.
echo [1/4] Looking for the process holding port 8000 ...
set "PID="
for /f "delims=" %%p in ('powershell -NoProfile -Command "$c = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue ^| Select-Object -First 1; if ($c) { $c.OwningProcess }"') do set "PID=%%p"
if defined PID (
  echo   Found PID=%PID% - terminating ...
  taskkill /PID %PID% /F
  timeout /t 2 >nul
) else (
  echo   No process is listening on port 8000.
)

echo.
echo [2/4] Starting backend in background (log: _boot.log, JVM heap capped at 512m) ...
rem application-dev.yml reads the DB password from env (sanitized repo); set it here.
set "DB_PASSWORD=123456"
start "" /MIN cmd /c "cd /d backend && set DB_PASSWORD=123456&& mvn -q -Dmaven.test.skip=true compile spring-boot:run -Dspring-boot.run.jvmArguments=-Xmx512m 1> ..\_boot.log 2>&1"

echo.
echo [3/4] Waiting for port 8000 (max ~180s) ...
set "UP=0"
for /L %%i in (1,1,60) do (
  netstat -ano | findstr :8000 | findstr LISTENING >nul
  if not errorlevel 1 (
    set "UP=1"
    echo   Backend is UP.
    goto :health
  )
  timeout /t 3 >nul
)

:health
if "%UP%"=="0" (
  echo   [FAIL] Timeout. Last 30 lines of _boot.log:
  powershell -NoProfile -Command "Get-Content '_boot.log' -Tail 30"
  goto :done
)

echo.
echo [4/4] Health check ...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/admin/index.html' -UseBasicParsing -TimeoutSec 25; Write-Host ('  HTTP /admin/index.html = ' + $r.StatusCode) } catch { Write-Host '  HTTP check FAILED' }"
powershell -NoProfile -Command "try { $x = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/recommend' -Method Post -ContentType 'application/json' -Body '{\"algo\":\"demographic\",\"top\":3}'; Write-Host ('  API /api/recommend code = ' + $x.code) } catch { Write-Host '  API check FAILED' }"

echo.
echo ------------------------------------------------------------
echo  Done. Open http://localhost:8000/admin  (login account: see lab report / DB t_user)
echo  Log file: _boot.log
echo ------------------------------------------------------------

:done
endlocal
pause
