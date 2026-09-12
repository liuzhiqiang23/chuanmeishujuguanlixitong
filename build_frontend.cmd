@echo off
rem ============================================================================
rem  movie-system - frontend one-click build & deploy (Windows)
rem
rem  Usage : double-click this file, or run it in the project root (movie-system):
rem            build_frontend.cmd [-restart] [-nopause]
rem          -restart : after a successful copy, also call restart_backend.cmd
rem                     (it pauses at its own end, that is normal behavior)
rem          -nopause : skip the final pause of THIS script, for chained calls
rem                     or automation
rem
rem  Steps : 1 build frontend (npm run build, artifacts -> frontend\admin)
rem          -> 2 mirror frontend\admin into backend\src\main\resources\static\admin
rem          -> 3 done message, remind the Ctrl+F5 browser hard refresh
rem          -> 4 optional backend restart when "-restart" is given
rem
rem  Note  : robocopy exit codes 0-7 mean SUCCESS and 8+ mean failure, so the
rem          check below MUST be "if errorlevel 8", not "errorlevel 1".
rem          /MIR mirrors the tree: it also DELETES stale content-hashed files
rem          in the backend static dir that no longer exist in frontend\admin
rem          (old hashes pile up on every rebuild), keeping the two trees
rem          strictly identical.
rem ============================================================================
setlocal

cd /d "%~dp0"

echo ============================================================
echo  movie-system frontend build ^& deploy
echo  project dir: %CD%
echo ============================================================

echo.
echo [1/4] Building frontend: npm run build, artifacts -> frontend\admin ...
pushd frontend
call npm run build
set "BUILD_RC=%errorlevel%"
popd
if not "%BUILD_RC%"=="0" (
  echo   [FAIL] npm run build failed, exit code %BUILD_RC%. Nothing was copied.
  goto :fail
)
echo   Build OK.

echo.
echo [2/4] Mirroring frontend\admin -> backend\src\main\resources\static\admin ...
rem /MIR deletes backend-side files that no longer exist in frontend\admin,
rem so the served artifacts stay exactly in sync with the fresh build.
robocopy "frontend\admin" "backend\src\main\resources\static\admin" /MIR /NFL /NDL /NJH /NJS /NP
if errorlevel 8 (
  echo   [FAIL] robocopy failed, exit code %errorlevel% - 8 or higher means error.
  goto :fail
)
echo   Copy OK. robocopy codes 0-7 all mean success.

echo.
echo [2b/4] Mirroring into backend\target\classes\static\admin (live classpath) ...
rem The backend runs via spring-boot:run and serves static files from
rem target\classes, NOT from src\main\resources. Without this mirror a
rem fresh build would never show up until the next full backend restart.
if exist "backend\target\classes\static\admin" (
  robocopy "frontend\admin" "backend\target\classes\static\admin" /MIR /NFL /NDL /NJH /NJS /NP
  if errorlevel 8 (
    echo   [FAIL] robocopy to target\classes failed.
    goto :fail
  )
  echo   Live classpath synced. No backend restart needed for static files.
) else (
  echo   backend\target\classes\static\admin not found - backend not built yet, skipped.
)

echo.
echo [3/4] Done. Hard-refresh the browser with Ctrl+F5 to see the new version:
echo   index.html is served with no-store, js/css names carry content hashes.

echo.
echo [4/4] Optional backend restart ...
if /i "%~1"=="-restart" (
  echo   "-restart" given - calling restart_backend.cmd now.
  echo   It pauses at its own end, that is normal behavior.
  call restart_backend.cmd
) else (
  echo   Skipped. Run "build_frontend.cmd -restart" to restart the backend too.
)

echo.
echo ------------------------------------------------------------
echo  Frontend build ^& deploy finished.
echo  Open http://localhost:8000/admin  then press Ctrl+F5.
echo ------------------------------------------------------------

endlocal
if /i "%~2"=="-nopause" exit /b 0
pause
exit /b 0

:fail
echo.
echo  [FAIL] build_frontend.cmd aborted - fix the error above and run it again.
endlocal
if /i "%~2"=="-nopause" exit /b 1
pause
exit /b 1
