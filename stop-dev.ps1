# stop-dev.ps1 - Tat MySQL (local) + Backend (FastAPI) + Frontend (Vite)
# Chay: powershell -ExecutionPolicy Bypass -File .\stop-dev.ps1

function Stop-ByPort($port, $label) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "[$label] Khong co gi dang chay tren port $port." -ForegroundColor DarkGray
        return
    }
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $pids) {
        try {
            Stop-Process -Id $p -Force -ErrorAction Stop
            Write-Host "[$label] Da tat process $p (port $port)." -ForegroundColor Green
        } catch {
            Write-Host "[$label] Khong tat duoc process $p : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Stop-ByPort 3306 "MySQL"
Stop-ByPort 8080 "Backend"
Stop-ByPort 5173 "Frontend"
