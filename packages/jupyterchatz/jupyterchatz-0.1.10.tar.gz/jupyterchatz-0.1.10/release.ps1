# release.ps1
param (
    [string]$Version = ""
)

Write-Host "Starting release process..."

# 1. Clean old build artifacts
Write-Host "Cleaning old build files..."
if (Test-Path yarn.lock) { Remove-Item yarn.lock -Force }
if (Test-Path ".yarn\cache") { Remove-Item ".yarn\cache" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
Get-ChildItem -Filter "*.egg-info" | Remove-Item -Recurse -Force

# 2. Install frontend dependencies
Write-Host "Installing frontend dependencies..."
jlpm install

# 3. Build frontend extension
Write-Host "Building frontend extension..."
jlpm build:prod

# 4. Ensure Python build tools are installed
Write-Host "Checking Python build tools..."
python -m pip install --upgrade pip build twine hatchling hatch-jupyter-builder

# 5. Build Python package
Write-Host "Building Python package..."
python -m build

# 6. If version is provided, bump version
if ($Version -ne "") {
    Write-Host "Setting version to $Version ..."
    hatch version $Version
    python -m build
}

# 7. Upload to PyPI
Write-Host "Uploading to PyPI..."
python -m twine upload dist/*

Write-Host "Release finished!"
