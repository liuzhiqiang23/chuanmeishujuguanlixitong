# movie-system - one-click remote demo starter
#
#   1) make sure the backend is listening on port 8000 (start it if it is down)
#   2) start the cloudflared quick tunnel via tools\tunnel.cmd
#   3) save the temporary public URL in the ignored tools\tunnel_url.txt file
#   4) print the next steps without exposing the URL in console logs
#
# Pure ASCII on purpose: PowerShell 5.1 and cmd.exe mis-parse non-ASCII script files.

$ErrorActionPreference = 'Continue'

$Root  = Split-Path -Parent $PSScriptRoot
$Tools = Join-Path $Root 'tools'
$TLog  = Join-Path $Tools 'tunnel.log'
$UrlFile = Join-Path $Tools 'tunnel_url.txt'

function Test-Port([int]$Port) {
    try {
        $c = New-Object Net.Sockets.TcpClient
        $c.Connect('127.0.0.1', $Port)
        $c.Close()
        return $true
    } catch {
        return $false
    }
}

Write-Host ''
Write-Host '=== movie-system remote demo ===' -ForegroundColor Cyan

# --- 1) backend -------------------------------------------------------------
if (Test-Port 8000) {
    Write-Host '[1/3] backend already up on port 8000'
} else {
    Write-Host '[1/3] backend is down, starting it (this takes about a minute) ...'
    Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', 'restart_backend.cmd' -WorkingDirectory $Root -WindowStyle Minimized
    $up = $false
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 3
        if (Test-Port 8000) { $up = $true; break }
    }
    if ($up) {
        Write-Host '      backend is up'
    } else {
        Write-Host '      [FAIL] backend did not come up within 3 min - see _boot.log' -ForegroundColor Red
        exit 1
    }
}

# --- 2) tunnel --------------------------------------------------------------
# Order matters: bring the new tunnel up and get its URL FIRST, kill the old one only
# after that succeeds. Doing it the other way round means a Cloudflare rate-limit on
# provisioning leaves you with no tunnel at all (hit exactly this on 2026-09-18).
Write-Host '[2/3] starting cloudflared tunnel ...'
$oldProcs = @(Get-Process cloudflared -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
if (Test-Path $TLog) { Remove-Item $TLog -Force -ErrorAction SilentlyContinue }
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', 'tunnel.cmd' -WorkingDirectory $Tools -WindowStyle Minimized

$url = $null
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 2
    if (Test-Path $TLog) {
        $hit = Select-String -Path $TLog -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' -AllMatches |
               ForEach-Object { $_.Matches } | ForEach-Object { $_.Value } |
               Where-Object { $_ -notmatch 'api\.trycloudflare\.com' } |
               Select-Object -First 1
        if ($hit) { $url = $hit; break }
    }
}
if (-not $url) {
    Write-Host '      [FAIL] Cloudflare did not hand out a URL within 120s.' -ForegroundColor Red
    Write-Host '             The old tunnel was deliberately left running - nothing was killed.' -ForegroundColor Yellow
    Write-Host '             Wait a minute or two (quick tunnels get rate limited) and re-run.' -ForegroundColor Yellow
    exit 1
}
foreach ($p in $oldProcs) {
    Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
}
 [IO.File]::WriteAllText($UrlFile, $url + [Environment]::NewLine, (New-Object Text.UTF8Encoding($false)))
Write-Host '[3/3] temporary URL saved in tools\tunnel_url.txt (ignored by Git)'

# --- done -------------------------------------------------------------------
Write-Host ''
Write-Host '------------------------------------------------------------'
Write-Host ' Next steps'
Write-Host '   1. For a temporary preview, configure the local Mini Program API base in DevTools.'
Write-Host '      Read it from tools\tunnel_url.txt; do not commit it into app.js.'
Write-Host '   2. Rebuild and preview in WeChat DevTools.'
Write-Host ''
Write-Host ' Keep in mind'
Write-Host '   - The public URL changes every time the tunnel restarts.'
Write-Host '     Re-run this script and update the local DevTools API base.'
Write-Host '   - Speed is limited by the phone hotspot and by Cloudflare'
Write-Host '     routing this line to the US (about 260 ms round trip).'
Write-Host '     Movie posters can take several seconds to show up.'
Write-Host '   - Keep the tunnel URL out of tracked source and issue comments.'
Write-Host '------------------------------------------------------------'
Write-Host ''
