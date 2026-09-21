@echo off
rem movie-system - start backend + public tunnel for a remote demo,
rem then rewrite miniprogram\app.js so the mini program can reach this PC.
rem Pure ASCII + CRLF on purpose: cmd.exe mis-parses LF-only or non-ASCII files.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\start_remote.ps1"
pause
