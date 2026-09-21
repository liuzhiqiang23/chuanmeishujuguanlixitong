@echo off
rem movie-system - cloudflared quick tunnel (localhost:8000 -> public https URL)
rem Pure ASCII + CRLF on purpose: cmd.exe mis-parses LF-only or non-ASCII files.
cd /d D:\movie-system\tools
cloudflared.exe tunnel --url http://localhost:8000 --no-autoupdate --edge-ip-version 4 --protocol http2 --logfile D:\movie-system\tools\tunnel.log --loglevel info
