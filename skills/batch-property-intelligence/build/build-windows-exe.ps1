# Build the BPI launcher into a single-file Windows .exe.
# Run from the project root on a Windows host with Python 3.11+ installed.
#
# Prerequisites:
#   pip install -e ".[dev]"   # installs pyinstaller alongside the runtime deps
#
# Output:
#   dist/bpi-launcher.exe     (~30 MB, no Python install needed on target machines)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Building BPI launcher from $projectRoot" -ForegroundColor Cyan

# Clean prior build artefacts (keep our spec file)
if (Test-Path "$projectRoot\build\bpi-launcher") {
    Remove-Item -Recurse -Force "$projectRoot\build\bpi-launcher"
}
if (Test-Path "$projectRoot\dist") {
    Remove-Item -Recurse -Force "$projectRoot\dist"
}

# Build
pyinstaller "$projectRoot\build\bpi-launcher.spec" `
    --distpath "$projectRoot\dist" `
    --workpath "$projectRoot\build\bpi-launcher"

if (-not (Test-Path "$projectRoot\dist\bpi-launcher.exe")) {
    Write-Host "Build failed — bpi-launcher.exe not produced." -ForegroundColor Red
    exit 1
}

$size = (Get-Item "$projectRoot\dist\bpi-launcher.exe").Length / 1MB
Write-Host ("Built dist\bpi-launcher.exe ({0:N1} MB)" -f $size) -ForegroundColor Green
Write-Host "Double-click to launch, or copy to Mitch's desktop." -ForegroundColor Green
