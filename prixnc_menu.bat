@echo off
title PrixNC Data Retrieval System - Menu Principal
color 0A

:MENU
cls
echo ================================================
echo       PRIX.NC DATA RETRIEVAL SYSTEM - MENU
echo ================================================
echo.
echo  1. Recuperer tous les produits
echo  2. Recuperer 100 produits seulement (test)
echo  3. Visualiser les statistiques
echo  4. Rechercher des produits
echo  5. Exporter les resultats en CSV
echo  6. Verifier la configuration
echo  7. Quitter
echo.
echo ================================================
echo.

set /p choix="Votre choix (1-7): "

if "%choix%"=="1" goto RECUPERER_TOUS
if "%choix%"=="2" goto RECUPERER_TEST
if "%choix%"=="3" goto STATISTIQUES
if "%choix%"=="4" goto RECHERCHE
if "%choix%"=="5" goto EXPORT
if "%choix%"=="6" goto VERIFIER
if "%choix%"=="7" goto FIN

echo Choix invalide. Veuillez reessayer.
timeout /t 2 >nul
goto MENU

:RECUPERER_TOUS
cls
echo ================================================
echo      RECUPERATION DE TOUS LES PRODUITS
echo ================================================
echo.
echo Cette operation peut prendre plusieurs heures.
echo Appuyez sur CTRL+C a tout moment pour arreter.
echo.
pause
cls
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe recuperer_produits.py
pause
goto MENU

:RECUPERER_TEST
cls
echo ================================================
echo      RECUPERATION DE 100 PRODUITS (TEST)
echo ================================================
echo.
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe recuperer_produits.py --limit 100 --page-size 10
pause
goto MENU

:STATISTIQUES
cls
echo ================================================
echo      VISUALISATION DES STATISTIQUES
echo ================================================
echo.
echo Appuyez sur CTRL+C pour revenir au menu.
echo.
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe simple_stats_viewer.py
goto MENU

:RECHERCHE
cls
echo ================================================
echo      RECHERCHE DE PRODUITS
echo ================================================
echo.
set /p terme="Terme a rechercher: "
cls
echo Recherche en cours pour: %terme%
echo.
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe prix_nc_manager.py --search "%terme%"
pause
goto MENU

:EXPORT
cls
echo ================================================
echo      EXPORT DES RESULTATS EN CSV
echo ================================================
echo.
set /p terme="Terme a rechercher: "
set /p fichier="Nom du fichier CSV (sans extension): "
cls
echo Export en cours...
echo.
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe prix_nc_manager.py --search "%terme%" --export "%fichier%.csv"
echo.
echo Les resultats ont ete exportes dans le fichier: %fichier%.csv
pause
goto MENU

:VERIFIER
cls
echo ================================================
echo      VERIFICATION DE LA CONFIGURATION
echo ================================================
echo.
echo Version de Python:
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe --version
echo.
echo Version de pip:
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe -m pip --version
echo.
echo Verification de SQLite:
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe -c "import sqlite3; print(f'SQLite version: {sqlite3.sqlite_version}')"
echo.
echo Verification des dependances:
C:\Users\xavier\AppData\Local\Programs\Python\Python310\python.exe -c "import requests; print(f'Requests version: {requests.__version__}')"
echo.
echo Chemin de la base de donnees:
dir prix_nc.db
echo.
pause
goto MENU

:FIN
cls
echo ================================================
echo      AU REVOIR !
echo ================================================
echo.
echo Merci d'avoir utilise Prix.nc Data Retrieval System.
echo.
timeout /t 3 >nul
exit
