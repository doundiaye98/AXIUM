@echo off
REM ============================================================
REM  AXIUM — serveur du site (Flask), PAS Apache/WAMP.
REM  Une fenetre NOIRE va s'ouvrir : laissez-la OUVERTE pendant
REM  que vous utilisez http://127.0.0.1:5001/ dans le navigateur.
REM ============================================================
set "TP=%~dp0toftal_python"
if not exist "%TP%\app.py" (
  echo [ERREUR] Dossier introuvable : %TP%
  pause
  exit /b 1
)
start "AXIUM Flask — port 5001" cmd /k pushd "%TP%" ^&^& call run.bat
echo Une nouvelle fenetre "AXIUM Flask" a ete ouverte.
echo Si le navigateur affiche encore "connexion refusee", lisez le texte dans cette fenetre.
timeout /t 4 >nul
