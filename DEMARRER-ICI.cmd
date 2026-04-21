@echo off
chcp 65001 >nul
title AXIUM — demarrage
cd /d "%~dp0"
echo.
echo Lancement du serveur Flask (dossier toftal_python)...
echo Ne tapez PAS run.bat avec un point a la fin.
echo.
echo IMPORTANT : laissez la fenetre PowerShell OUVERTE. Si vous la fermez, le site
echo            affichera ERR_CONNECTION_REFUSED dans le navigateur.
echo            Attendez le message du type  Running on http://127.0.0.1:...  puis ouvrez l URL.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-AXIUM.ps1"
if errorlevel 1 pause
