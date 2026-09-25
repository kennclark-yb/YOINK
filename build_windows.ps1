param([string]$Python = "$PSScriptRoot\.venv\Scripts\python.exe", [switch]$QA)
$ErrorActionPreference = 'Stop'
$oldBrowserPath = $env:PLAYWRIGHT_BROWSERS_PATH
$oldPythonEncoding = $env:PYTHONIOENCODING
$oldPath = $env:PATH
Push-Location $PSScriptRoot
try {
    $env:PYTHONIOENCODING = 'utf-8'
    # Do not collect unrelated DLLs from developer tools on PATH. In particular,
    # a third-party ICU DLL can shadow Windows' ICU and break QtGui in the build.
    $Python = (Resolve-Path $Python).Path
    $env:PATH = "$(Split-Path $Python);$env:SystemRoot\System32;$env:SystemRoot"
    & $Python -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw 'Build dependency installation failed' }
    # Playwright's own frozen-runtime support finds this package-local browser.
    $env:PLAYWRIGHT_BROWSERS_PATH = '0'
    & $Python -m playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw 'Chromium installation failed' }
    $spec = if ($QA) { 'YOINK-QA.spec' } else { 'YOINK.spec' }
    & $Python -m PyInstaller --noconfirm --clean $spec
    if ($LASTEXITCODE -ne 0) { throw 'YOINK packaging failed' }
    if ($QA) { Write-Host 'Built dist\YOINK-QA\YOINK-QA.exe (tests only; do not distribute).' }
    else { Write-Host 'Built dist\YOINK\YOINK.exe. Distribute the entire YOINK folder.' }
} finally {
    $env:PLAYWRIGHT_BROWSERS_PATH = $oldBrowserPath
    $env:PYTHONIOENCODING = $oldPythonEncoding
    $env:PATH = $oldPath
    Pop-Location
}
