# Demarre Flask (dossier toftal_python).
# PowerShell : depuis ce dossier, tapez  .\Start-AXIUM.ps1  (le .\ est obligatoire)
# Ou double-clic sur DEMARRER-ICI.cmd
# Ne pas taper "run.bat." avec un point.

$ErrorActionPreference = 'Continue'

$Root = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent -Path $MyInvocation.MyCommand.Path
}
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Get-Location | Select-Object -ExpandProperty Path
}

$AppDir = Join-Path $Root 'toftal_python'
$AppPy = Join-Path $AppDir 'app.py'
$Req = Join-Path $AppDir 'requirements.txt'

$VenvPy = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $VenvPy)) {
    $VenvPy = Join-Path $AppDir '.venv\Scripts\python.exe'
}

if (-not (Test-Path -LiteralPath $AppDir)) {
    Write-Host "ERREUR : dossier introuvable : $AppDir" -ForegroundColor Red
    Read-Host 'Appuyez sur Entree pour fermer'
    exit 1
}

if (-not $env:PORT) { $env:PORT = '5001' }

Write-Host ''
Write-Host '=== AXIUM - laissez cette fenetre OUVERTE ===' -ForegroundColor Cyan
Write-Host "Dossier : $AppDir"
Write-Host "URL     : http://127.0.0.1:$($env:PORT)/"
Write-Host "Services: http://127.0.0.1:$($env:PORT)/services/"
Write-Host ''

Set-Location -LiteralPath $AppDir

function Invoke-AxiumPython {
    param([string]$Exe, [string[]]$PrefixArgs)
    $argsList = @()
    if ($PrefixArgs) { $argsList += $PrefixArgs }
    $argsList += @('-m', 'pip', 'install', '-r', $Req)
    & $Exe @argsList
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Attention : pip a signale une erreur (dependances).' -ForegroundColor Yellow
    }
    $argsRun = @()
    if ($PrefixArgs) { $argsRun += $PrefixArgs }
    $argsRun += $AppPy
    & $Exe @argsRun
}

if (Test-Path -LiteralPath $VenvPy) {
    Write-Host "Python : $VenvPy"
    & $VenvPy -c 'import flask' 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Installation des dependances (pip)...'
        & $VenvPy -m pip install -r $Req
    }
    & $VenvPy $AppPy
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    Write-Host 'Python : py -3'
    Invoke-AxiumPython -Exe 'py' -PrefixArgs @('-3')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host 'Python : python'
    & python -m pip install -r $Req
    & python $AppPy
} else {
    Write-Host 'ERREUR : Python introuvable. Installez Python 3 ou creez un venv.' -ForegroundColor Red
    Write-Host "Essayez : cd `"$AppDir`" puis py -3 app.py"
    Read-Host 'Entree pour fermer'
    exit 1
}

Write-Host ''
Read-Host 'Serveur arrete. Entree pour fermer'
