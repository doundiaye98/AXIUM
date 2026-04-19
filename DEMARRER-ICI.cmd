@echo off
chcp 65001 >nul
title AXIUM — demarrage
cd /d "%~dp0"
echo.
echo Lancement du serveur Flask (dossier toftal_python)...
echo Ne tapez PAS run.bat avec un point a la fin.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-AXIUM.ps1"
if errorlevel 1 pause
