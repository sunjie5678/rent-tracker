# Setup script for Windows PowerShell (using uv)
# Run from project root: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

# Ensure uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor Cyan
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

Write-Host "Creating virtual environment and installing dependencies..." -ForegroundColor Cyan
uv sync --all-groups

Write-Host "`nDone! Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
