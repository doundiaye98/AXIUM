@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AXIUM — serveur local
if not defined PORT set PORT=5001

echo.
echo ============================================================
echo   AXIUM — serveur Flask sur le port %PORT%
echo   Depuis la racine AXIUM : double-clic sur DEMARRER-ICI.cmd
echo   Ne tapez PAS run.bat. avec un point ^(PowerShell^).
echo   URL : http://127.0.0.1:%PORT%/
echo   Reparation cookies : http://127.0.0.1:%PORT%/_axium/nettoyer-cookies
echo   NE FERMEZ PAS cette fenetre tant que vous testez le site.
echo   (La fermer = ERR_CONNECTION_REFUSED dans le navigateur.)
echo ============================================================
echo.

set "VENVP=%~dp0..\.venv\Scripts\python.exe"

if exist "%VENVP%" (
  echo Python : venv AXIUM\.venv
  "%VENVP%" -c "import flask" 2>nul
  if errorlevel 1 (
    echo Installation de Flask ^(une fois^)...
    "%VENVP%" -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
      echo [ERREUR] pip install a echoue.
      goto :fin
    )
  )
  "%VENVP%" "%~dp0app.py"
  goto :fin
)

py -3 -c "import sys" 2>nul
if not errorlevel 1 (
  echo Python : py -3 ^(lanceur Windows^)
  py -3 -c "import flask" 2>nul
  if errorlevel 1 (
    echo Installation de Flask ^(py -3^)...
    py -3 -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 goto :try_python
  )
  py -3 "%~dp0app.py"
  goto :fin
)

:try_python
echo Python : commande "python"
python -c "import flask" 2>nul
if errorlevel 1 (
  echo.
  echo [ERREUR] Flask introuvable. Dans une invite cmd :
  echo   py -3 -m pip install -r "%~dp0requirements.txt"
  echo Ou creez le venv :  cd /d "%~dp0.." ^& py -3 -m venv .venv
  goto :fin
)
python "%~dp0app.py"

:fin
echo.
echo Appuyez sur une touche pour fermer...
pause >nul
