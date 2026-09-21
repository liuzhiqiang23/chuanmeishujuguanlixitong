# movie-system - one-click remote demo starter
#
#   1) make sure the backend is listening on port 8000 (start it if it is down)
#   2) start the cloudflared quick tunnel via tools\tunnel.cmd
#   3) read the public URL out of tools\tunnel.log and write it into miniprogram\app.js
#   4) print the next steps
#
# Pure ASCII on purpose: PowerShell 5.1 and cmd.exe mis-parse non-ASCII script files.

$ErrorActionPreference = 'Continue'

$Root  = 'D:\movie-system'
$Tools = Join-Path $Root 'tools'
$AppJs = Join-Path $Root 'miniprogram\app.js'
$TLog  = Join-Path $Tools 'tunnel.log'

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
$oldUrl = ''
$m = [Regex]::Match((Get-Content $AppJs -Raw -Encoding UTF8), 'https://[a-z0-9-]+\.trycloudflare\.com')
if ($m.Success) { $oldUrl = $m.Value }

if (Test-Path $TLog) { Remove-Item $TLog -Force -ErrorAction SilentlyContinue }
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', 'tunnel.cmd' -WorkingDirectory $Tools -WindowStyle Minimized

$url = $null
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 2
    if (Test-Path $TLog) {
        $hit = Select-String -Path $TLog -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' -AllMatches |
               ForEach-Object { $_.Matches } | ForEach-Object { $_.Value } |
               Where-Object { $_ -notmatch 'api\.trycloudflare\.com' -and $_ -ne $oldUrl } |
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
Write-Host ('      tunnel ready: ' + $url)

# --- 3) point the mini program at it ---------------------------------------
$src = Get-Content $AppJs -Raw -Encoding UTF8

# LAN address: the interface that actually has the default route (the phone
# hotspot hands out a new one every so often, so never hardcode it).
$lanIp = $null
$conf = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null } | Select-Object -First 1
if ($conf) {
    $lanIp = ($conf.IPv4Address | Select-Object -First 1).IPAddress
}

$changed = $false
if ($lanIp) {
    $newSrc = [Regex]::Replace($src, 'http://(?!127\.0\.0\.1)\d+\.\d+\.\d+\.\d+:8000', 'http://' + $lanIp + ':8000')
    if ($newSrc -ne $src) { $changed = $true; $src = $newSrc }
    Write-Host ('[3/3] LAN address set to ' + $lanIp)
}

$found = [Regex]::Match($src, 'https://[a-z0-9-]+\.trycloudflare\.com')
if (-not $found.Success) {
    Write-Host '      [WARN] no trycloudflare URL found in app.js - edit API_BASES by hand' -ForegroundColor Yellow
} elseif ($found.Value -ne $url) {
    $src = [Regex]::Replace($src, 'https://[a-z0-9-]+\.trycloudflare\.com', $url)
    $changed = $true
    Write-Host ('      tunnel address updated: ' + $found.Value)
}

if ($changed) {
    [IO.File]::WriteAllText($AppJs, $src, (New-Object Text.UTF8Encoding($false)))
    Write-Host '      app.js written - press Ctrl+B in DevTools to pick it up'
} else {
    Write-Host '      app.js already up to date'
}

# --- done -------------------------------------------------------------------
Write-Host ''
Write-Host '------------------------------------------------------------'
Write-Host ' Next steps'
Write-Host '   1. WeChat DevTools -> press Ctrl+B to rebuild'
Write-Host '   2. Click "Preview", then send the QR code to your classmate'
Write-Host '   3. Classmate scans it - the mini program now reaches this PC'
Write-Host ''
Write-Host ' Keep in mind'
Write-Host '   - The public URL changes every time the tunnel restarts.'
Write-Host '     Re-run this script (it rewrites app.js), then Ctrl+B again.'
Write-Host '   - Speed is limited by the phone hotspot and by Cloudflare'
Write-Host '     routing this line to the US (about 260 ms round trip).'
Write-Host '     Movie posters can take several seconds to show up.'
Write-Host '   - Stay on 127.0.0.1 / the LAN IP while you develop; app.js'
Write-Host '     probes all three addresses and picks the fastest reachable one.'
Write-Host '------------------------------------------------------------'
Write-Host ''
