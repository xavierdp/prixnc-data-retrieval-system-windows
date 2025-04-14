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
echo  3. Recuperer UNIQUEMENT les tables annexes
echo  4. Recuperer tables annexes PUIS produits
echo  5. Visualiser les statistiques
echo  6. Rechercher des produits
echo  7. Exporter les resultats en CSV
echo  8. Verifier la configuration
echo  9. Quitter
echo.
echo ================================================
echo.

set /p choix="Votre choix (1-9): "

if "%choix%"=="1" goto RECUPERER_TOUS
if "%choix%"=="2" goto RECUPERER_TEST
if "%choix%"=="3" goto RECUPERER_ANNEXES
if "%choix%"=="4" goto RECUPERER_ANNEXES_PRODUITS
if "%choix%"=="5" goto STATISTIQUES
if "%choix%"=="6" goto RECHERCHE
if "%choix%"=="7" goto EXPORT
if "%choix%"=="8" goto VERIFIER
if "%choix%"=="9" goto FIN

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
python recuperer_produits.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La recuperation des produits a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
)
pause
goto MENU

:RECUPERER_TEST
cls
echo ================================================
echo      RECUPERATION DE 100 PRODUITS (TEST)
echo ================================================
echo.
python recuperer_produits.py --limit 100 --page-size 10
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La recuperation des produits a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
)
pause
goto MENU

:RECUPERER_ANNEXES
cls
echo ================================================
echo      RECUPERATION DES TABLES ANNEXES
echo ================================================
echo.
echo Cette operation va recuperer toutes les donnees annexes:
echo - Communes
echo - Magasins
echo - Secteurs de consommation
echo - Sous-secteurs
echo - Types de commerce
echo - Marques
echo - Varietes
echo - Boucliers qualite prix
echo.
echo Appuyez sur CTRL+C a tout moment pour arreter.
echo.
pause
cls
echo Recuperation des tables annexes en cours...
echo.
python prix_nc_manager.py --all-except-products
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La recuperation des tables annexes a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
)
pause
goto MENU

:RECUPERER_ANNEXES_PRODUITS
cls
echo ================================================
echo    RECUPERATION DES ANNEXES PUIS DES PRODUITS
echo ================================================
echo.
echo Cette operation va d'abord recuperer toutes les donnees annexes,
echo puis tous les produits et leurs prix.
echo.
echo ETAPE 1: Recuperation des tables annexes
echo ETAPE 2: Recuperation des produits et prix
echo.
echo Cette operation complete peut prendre plusieurs heures.
echo Appuyez sur CTRL+C a tout moment pour arreter.
echo.
pause
cls

echo ETAPE 1: Recuperation des tables annexes en cours...
echo.
python prix_nc_manager.py --all-except-products
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La recuperation des tables annexes a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
    pause
    goto MENU
)
echo.
echo Tables annexes recuperees avec succes.
echo.

echo ETAPE 2: Recuperation des produits et prix en cours...
echo.
python recuperer_produits.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La recuperation des produits a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
    pause
    goto MENU
)
echo.
echo Produits et prix recuperes avec succes.
echo.
echo Recuperation complete terminee!
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
python simple_stats_viewer.py
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
python prix_nc_manager.py --search "%terme%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: La recherche a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
)
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
python prix_nc_manager.py --search "%terme%" --export-search --search-output "%fichier%.csv"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: L'export a echoue.
    echo Verifiez que Python est correctement installe et que les dependances sont satisfaites.
    echo.
)
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
python --version
echo.
echo Version de pip:
python -m pip --version
echo.
echo Verification de SQLite:
python -c "import sqlite3; print(f'SQLite version: {sqlite3.sqlite_version}')"
echo.
echo Verification des dependances:
python -c "import requests; print(f'Requests version: {requests.__version__}')"
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
