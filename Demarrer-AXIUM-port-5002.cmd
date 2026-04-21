@echo off
chcp 65001 >nul
title AXIUM Flask — port 5002
cd /d "%~dp0"
REM Si 5001 est pris par WAMP ou une autre appli, ce lanceur force le port 5002.
set "PORT=5002"
echo Port force : %PORT%  ^(http://127.0.0.1:%PORT%/^)
echo Laissez la fenetre ouverte — sinon ERR_CONNECTION_REFUSED dans le navigateur.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-AXIUM.ps1"
if errorlevel 1 pause
