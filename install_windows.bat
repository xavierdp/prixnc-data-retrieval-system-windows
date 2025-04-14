@echo off
echo === Lancement de l'installateur Prix.nc Data Retrieval System ===
echo.

:: Exécute le script PowerShell avec les permissions "Bypass" pour éviter les problèmes d'exécution
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

:: Fin du script
exit
