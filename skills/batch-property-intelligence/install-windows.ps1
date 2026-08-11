# BPI launcher — one-shot Windows installer.
#
# Usage: right-click this file in Explorer → "Run with PowerShell".
# Or from PowerShell: powershell -ExecutionPolicy Bypass -File install-windows.ps1
#
# What it does:
#   1. Confirms it's running from the bpi-launcher project folder
#   2. Installs Python deps via pip (uses your current Python — needs 3.11+)
#   3. Runs the test suite (sanity check)
#   4. Builds dist\bpi-launcher.exe via PyInstaller
#   5. Creates a "BPI Launcher" shortcut in your Local-Tools folder
#   6. Optionally creates a Desktop shortcut

$ErrorActionPreference = "Stop"

# Always run from the script's own folder, regardless of where it was launched.
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

function Write-Step($n, $msg) {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
    Write-Host "  Step $n — $msg" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
}

function Fail($msg) {
    Write-Host ""
    Write-Host "✗ $msg" -ForegroundColor Red
    Write-Host "Installation aborted." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

# ─── Step 1 — sanity check ────────────────────────────────────────────────

Write-Step 1 "Verifying project layout in $projectRoot"

foreach ($required in @("SKILL.md", "pyproject.toml", "src\main.py", "build\bpi-launcher.spec")) {
    if (-not (Test-Path "$projectRoot\$required")) {
        Fail "Missing $required. Are you running this from inside the bpi-launcher folder?"
    }
}
Write-Host "✓ Project layout looks correct" -ForegroundColor Green

# ─── Step 2 — Python deps ─────────────────────────────────────────────────

Write-Step 2 "Checking Python and installing dependencies"

try {
    $pyVersion = (python --version) 2>&1
    Write-Host "Found: $pyVersion"
}
catch {
    Fail "Python is not on your PATH. Install Python 3.11+ from https://www.python.org/downloads/ (tick 'Add Python to PATH' during install)."
}

Write-Host "Installing project + dev dependencies (pandas, watchdog, pyinstaller, …)…"
python -m pip install --upgrade pip --quiet
python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    Fail "pip install failed. Scroll up for the error."
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# ─── Step 3 — tests ───────────────────────────────────────────────────────

Write-Step 3 "Running the test suite"

python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) {
    Fail "Tests failed. Scroll up for which test broke."
}
Write-Host "✓ All tests pass" -ForegroundColor Green

# ─── Step 4 — build the .exe ──────────────────────────────────────────────

Write-Step 4 "Building dist\bpi-launcher.exe (this takes ~1 minute)"

# Clean prior artefacts
if (Test-Path "$projectRoot\build\bpi-launcher") {
    Remove-Item -Recurse -Force "$projectRoot\build\bpi-launcher"
}
if (Test-Path "$projectRoot\dist") {
    Remove-Item -Recurse -Force "$projectRoot\dist"
}

pyinstaller "$projectRoot\build\bpi-launcher.spec" `
    --distpath "$projectRoot\dist" `
    --workpath "$projectRoot\build\bpi-launcher" `
    --noconfirm

if (-not (Test-Path "$projectRoot\dist\bpi-launcher.exe")) {
    Fail "PyInstaller did not produce bpi-launcher.exe. Scroll up for the error."
}

$sizeMB = [math]::Round((Get-Item "$projectRoot\dist\bpi-launcher.exe").Length / 1MB, 1)
Write-Host "✓ Built dist\bpi-launcher.exe ($sizeMB MB)" -ForegroundColor Green

# ─── Step 5 — shortcut in Local-Tools ─────────────────────────────────────

Write-Step 5 "Creating shortcuts"

$exePath = "$projectRoot\dist\bpi-launcher.exe"
$workDir = $projectRoot

$localToolsDir = "E:\OneDrive - Elite Lifestyle Properties\Claude\Projects\ELITE-Project-System\09_Local-Tools\Skills\batch-intelliegence"
try {
    New-Item -ItemType Directory -Force -Path $localToolsDir | Out-Null
    $wsh = New-Object -ComObject WScript.Shell
    $sc = $wsh.CreateShortcut("$localToolsDir\BPI Launcher.lnk")
    $sc.TargetPath = $exePath
    $sc.WorkingDirectory = $workDir
    $sc.Description = "Batch Property Intelligence — ELP Hub"
    $sc.Save()
    Write-Host "✓ Shortcut: $localToolsDir\BPI Launcher.lnk" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Could not create Local-Tools shortcut: $_" -ForegroundColor Yellow
    Write-Host "  You can launch directly from $exePath instead." -ForegroundColor Yellow
}

# Desktop shortcut (optional)
$answer = Read-Host "Also put a shortcut on your Desktop? [Y/n]"
if ($answer -eq "" -or $answer -match "^[Yy]") {
    try {
        $wsh = New-Object -ComObject WScript.Shell
        $sc = $wsh.CreateShortcut("$HOME\Desktop\BPI Launcher.lnk")
        $sc.TargetPath = $exePath
        $sc.WorkingDirectory = $workDir
        $sc.Description = "Batch Property Intelligence — ELP Hub"
        $sc.Save()
        Write-Host "✓ Desktop shortcut created" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠ Could not create Desktop shortcut: $_" -ForegroundColor Yellow
    }
}

# ─── Done ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "  ✓ BPI Launcher installed" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Working folder : $projectRoot" -ForegroundColor Gray
Write-Host "Launcher .exe  : $exePath" -ForegroundColor Gray
Write-Host "Drop CSVs into : $projectRoot\inputs\" -ForegroundColor Gray
Write-Host "Dashboards land: $projectRoot\outputs\" -ForegroundColor Gray
Write-Host ""
Write-Host "Next: double-click the 'BPI Launcher' shortcut (Local-Tools or Desktop)." -ForegroundColor Cyan
Write-Host "      Click Start Watcher, then Pick CSV…, then Open Dashboard." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close"
