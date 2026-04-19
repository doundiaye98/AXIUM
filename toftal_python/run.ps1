# Lance Flask (port 5001 par defaut). Utilise AXIUM\.venv\Scripts\python.exe si present.
Set-Location $PSScriptRoot

if (-not $env:PORT) { $env:PORT = '5001' }

$parent = Split-Path -Parent $PSScriptRoot
$venvPy = Join-Path $parent '.venv\Scripts\python.exe'

if (Test-Path -LiteralPath $venvPy) {
    $py = $venvPy
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $py = 'py'
}
else {
    $py = 'python'
}

Write-Host ''
Write-Host "Dossier : $(Get-Location)"
Write-Host "Python  : $py"
Write-Host "Port    : $($env:PORT)"
Write-Host "URL     : http://127.0.0.1:$($env:PORT)/"
Write-Host ''
Write-Host 'Gardez cette fenetre OUVERTE — sinon ERR_CONNECTION_REFUSED dans le navigateur.'
Write-Host ''

& $py -c "import flask" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host '[ERREUR] Flask absent. Installez avec :'
    Write-Host "  & `"$py`" -m pip install -r `"$PSScriptRoot\requirements.txt`""
    exit 1
}

& $py (Join-Path $PSScriptRoot 'app.py')
