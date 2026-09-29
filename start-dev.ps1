# start-dev.ps1 - Khoi dong MySQL (local) + Backend (FastAPI) + Frontend (Vite)
# Chay: powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
#
# MySQL o day la instance rieng chay duoi quyen user hien tai (KHONG phai
# service Windows MySQL84), du lieu luu trong backend\data\mysql-data.
# Neu chua co du lieu, xem huong dan khoi tao o phan cuoi file README hoac
# hoi lai Claude Code.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$mysqld       = "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe"
$mysqlDataDir = Join-Path $root "backend\data\mysql-data"
$mysqlBaseDir = "C:\Program Files\MySQL\MySQL Server 8.4"
$backendDir   = Join-Path $root "backend"
$frontendDir  = Join-Path $root "frontend"

function Test-PortOpen($port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect("127.0.0.1", $port)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

# --- 1. MySQL ---------------------------------------------------------
if (Test-PortOpen 3306) {
    Write-Host "[MySQL] Da co gi do dang chay tren port 3306, bo qua buoc khoi dong." -ForegroundColor Yellow
} elseif (-not (Test-Path $mysqlDataDir)) {
    Write-Host "[MySQL] Khong tim thay du lieu tai $mysqlDataDir" -ForegroundColor Red
    Write-Host "        Chua duoc khoi tao - nho Claude Code khoi tao lai truoc." -ForegroundColor Red
} else {
    Write-Host "[MySQL] Dang khoi dong (port 3306)..." -ForegroundColor Cyan
    Start-Process powershell -WindowStyle Normal -ArgumentList @(
        "-NoExit", "-Command",
        "& '$mysqld' --datadir='$mysqlDataDir' --basedir='$mysqlBaseDir' --port=3306 --console"
    )

    $tries = 0
    while (-not (Test-PortOpen 3306) -and $tries -lt 30) {
        Start-Sleep -Seconds 1
        $tries++
    }
    if (Test-PortOpen 3306) {
        Write-Host "[MySQL] San sang." -ForegroundColor Green
    } else {
        Write-Host "[MySQL] Van chua san sang sau 30s - kiem tra cua so MySQL vua mo." -ForegroundColor Red
    }
}

# --- 2. Backend (FastAPI) ---------------------------------------------
Write-Host "[Backend] Dang khoi dong (http://127.0.0.1:8080)..." -ForegroundColor Cyan
Start-Process powershell -WindowStyle Normal -WorkingDirectory $backendDir -ArgumentList @(
    "-NoExit", "-Command",
    ".\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload"
)

# --- 3. Frontend (Vite) -------------------------------------------------
Write-Host "[Frontend] Dang khoi dong (http://localhost:5173)..." -ForegroundColor Cyan
Start-Process powershell -WindowStyle Normal -WorkingDirectory $frontendDir -ArgumentList @(
    "-NoExit", "-Command",
    "npm run dev"
)

Write-Host ""
Write-Host "Da mo 3 cua so PowerShell:" -ForegroundColor Green
Write-Host "  - MySQL    : 127.0.0.1:3306"
Write-Host "  - Backend  : http://127.0.0.1:8080  (Swagger: /docs)"
Write-Host "  - Frontend : http://localhost:5173"
Write-Host ""
Write-Host "Dong cua so tuong ung (hoac Ctrl+C ben trong) de tat tung dich vu." -ForegroundColor DarkGray
