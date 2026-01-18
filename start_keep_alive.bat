@echo off
title RESPIRIA Keep-Alive Service
echo ========================================
echo   RESPIRIA AI - Keep-Alive Service
echo ========================================
echo.

cd /d "%~dp0"

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

:: Lancer le script
echo Demarrage du service Keep-Alive...
echo Appuyez Ctrl+C pour arreter.
echo.
python keep_alive.py

pause
