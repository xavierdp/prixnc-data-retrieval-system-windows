@echo off
setlocal enabledelayedexpansion
color 0A
title Installateur complet Prix.nc Data Retrieval System pour Windows

:: Variables pour stocker les chemins
set "PYTHON_PATH="
set "PYTHON_FOUND=0"

echo ================================================================
echo   INSTALLATEUR COMPLET PRIX.NC DATA RETRIEVAL SYSTEM - WINDOWS
echo ================================================================
echo.
echo Ce script va installer tous les composants necessaires :
echo  - Installation de Python (si necessaire)
echo  - Configuration du PATH
echo  - Installation des dependances
echo  - Initialisation de la base de donnees
echo.
echo ================================================================
echo.
pause

:MENU_PRINCIPAL
cls
echo ================================================================
echo               MENU D'INSTALLATION PRINCIPAL
echo ================================================================
echo.
echo  1. Installer Python (via winget - recommande)
echo  2. Chercher Python sur le systeme
echo  3. Ajouter Python au PATH
echo  4. Installer les dependances du projet
echo  5. Initialiser la base de donnees
echo  6. Lancer le menu interactif
echo  7. Installer tout automatiquement
echo  8. Quitter
echo.
echo ================================================================
echo.

set /p choix="Votre choix (1-8): "

if "%choix%"=="1" goto INSTALL_PYTHON
if "%choix%"=="2" goto FIND_PYTHON
if "%choix%"=="3" goto ADD_TO_PATH
if "%choix%"=="4" goto INSTALL_DEPS
if "%choix%"=="5" goto INIT_DB
if "%choix%"=="6" goto LAUNCH_MENU
if "%choix%"=="7" goto AUTO_INSTALL
if "%choix%"=="8" goto EXIT

echo Choix invalide. Veuillez reessayer.
timeout /t 2 >nul
goto MENU_PRINCIPAL

:INSTALL_PYTHON
cls
echo ================================================================
echo               INSTALLATION DE PYTHON
echo ================================================================
echo.
echo Installation de Python 3.10 via winget...
echo.
echo Cette operation necessite d'accepter les conditions d'utilisation.
echo Veuillez repondre "Y" quand on vous le demande.
echo.
pause
winget install -e --id Python.Python.3.10 --accept-package-agreements --accept-source-agreements
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation de Python.
    echo Veuillez l'installer manuellement depuis https://www.python.org/downloads/
    pause
) else (
    echo Python a ete installe avec succes.
    echo Notez que vous devrez peut-etre redemarrer votre ordinateur
    echo ou ce terminal pour que les changements prennent effet.
    pause
)
goto FIND_PYTHON

:FIND_PYTHON
cls
echo ================================================================
echo               RECHERCHE DE PYTHON
echo ================================================================
echo.
echo Recherche de Python sur votre systeme...
echo.

:: Recherche dans le PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_PATH=python"
    set "PYTHON_FOUND=1"
    echo Python trouve dans le PATH !
    goto PYTHON_FOUND
)

:: Recherche dans les emplacements standards
if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_PATH=C:\Program Files\Python310\python.exe"
    set "PYTHON_FOUND=1"
    echo Python trouve dans C:\Program Files\Python310\python.exe
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    set "PYTHON_PATH=C:\Program Files (x86)\Python310\python.exe"
    set "PYTHON_FOUND=1"
    echo Python trouve dans C:\Program Files (x86)\Python310\python.exe
    goto PYTHON_FOUND
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    set "PYTHON_FOUND=1"
    echo Python trouve dans C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe
    goto PYTHON_FOUND
)

echo Python n'a pas ete trouve sur votre systeme.
echo Veuillez l'installer en selectionnant l'option 1 du menu.
pause
goto MENU_PRINCIPAL

:PYTHON_FOUND
echo.
echo Python a ete trouve: !PYTHON_PATH!
echo.
echo Verification de la version:
"!PYTHON_PATH!" --version
echo.
pause
goto MENU_PRINCIPAL

:ADD_TO_PATH
cls
echo ================================================================
echo               AJOUT DE PYTHON AU PATH
echo ================================================================
echo.
if "%PYTHON_FOUND%"=="0" (
    echo Python n'a pas encore ete localise sur votre systeme.
    echo Veuillez d'abord executer l'option 2 pour trouver Python.
    pause
    goto MENU_PRINCIPAL
)

echo Execution du script d'ajout au PATH...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0add_python_to_path.ps1"
echo.
echo Pour que les modifications du PATH prennent effet,
echo vous devrez peut-etre redemarrer ce terminal ou votre ordinateur.
echo.
pause
goto MENU_PRINCIPAL

:INSTALL_DEPS
cls
echo ================================================================
echo           INSTALLATION DES DEPENDANCES
echo ================================================================
echo.
if "%PYTHON_FOUND%"=="0" (
    echo Python n'a pas encore ete localise sur votre systeme.
    echo Veuillez d'abord executer l'option 2 pour trouver Python.
    pause
    goto MENU_PRINCIPAL
)

echo Installation des packages Python requis...
echo.
"!PYTHON_PATH!" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation des dependances.
    echo Tentative d'installation directe...
    echo.
    "!PYTHON_PATH!" -m pip install requests
)
echo.
echo Dependances installees avec succes.
echo.
pause
goto MENU_PRINCIPAL

:INIT_DB
cls
echo ================================================================
echo           INITIALISATION DE LA BASE DE DONNEES
echo ================================================================
echo.
if "%PYTHON_FOUND%"=="0" (
    echo Python n'a pas encore ete localise sur votre systeme.
    echo Veuillez d'abord executer l'option 2 pour trouver Python.
    pause
    goto MENU_PRINCIPAL
)

echo Initialisation de la base de donnees SQLite...
echo.
"!PYTHON_PATH!" db_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'initialisation de la base de donnees.
    pause
) else (
    echo Base de donnees initialisee avec succes.
    echo.
    pause
)
goto MENU_PRINCIPAL

:LAUNCH_MENU
cls
echo ================================================================
echo           LANCEMENT DU MENU INTERACTIF
echo ================================================================
echo.
echo Lancement du menu interactif...
echo.
start prixnc_menu.bat
goto MENU_PRINCIPAL

:AUTO_INSTALL
cls
echo ================================================================
echo           INSTALLATION AUTOMATIQUE COMPLETE
echo ================================================================
echo.
echo Cette option va installer tout automatiquement.
echo.
set /p confirm="Etes-vous sur de vouloir continuer? (o/n): "
if /i not "%confirm%"=="o" goto MENU_PRINCIPAL

:: 1. Installer Python via winget
echo [1/4] Installation de Python...
winget install -e --id Python.Python.3.10 --accept-package-agreements --accept-source-agreements --silent

:: 2. Rechercher Python
echo [2/4] Recherche de Python...
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" (
    set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    set "PYTHON_FOUND=1"
)

if "%PYTHON_FOUND%"=="0" (
    if exist "C:\Program Files\Python310\python.exe" (
        set "PYTHON_PATH=C:\Program Files\Python310\python.exe"
        set "PYTHON_FOUND=1"
    )
)

if "%PYTHON_FOUND%"=="0" (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_PATH=python"
        set "PYTHON_FOUND=1"
    )
)

if "%PYTHON_FOUND%"=="0" (
    echo Python n'a pas ete trouve meme apres l'installation.
    echo Cela peut arriver si l'installation a echoue ou si le PATH n'est pas a jour.
    echo Veuillez redemarrer votre ordinateur et reessayer.
    pause
    goto MENU_PRINCIPAL
)

echo Python trouve: !PYTHON_PATH!

:: 3. Ajouter au PATH (silencieusement)
echo [3/4] Ajout de Python au PATH...
powershell -ExecutionPolicy Bypass -File "%~dp0add_python_to_path.ps1"

:: 4. Installer les dependances
echo [4/4] Installation des dependances...
"!PYTHON_PATH!" -m pip install -r requirements.txt

:: 5. Initialiser la base de donnees
echo [5/4] Initialisation de la base de donnees...
"!PYTHON_PATH!" db_setup.py

:: 6. Terminer
cls
echo ================================================================
echo           INSTALLATION COMPLETE !
echo ================================================================
echo.
echo Toutes les etapes d'installation ont ete effectuees avec succes.
echo.
echo Que souhaitez-vous faire maintenant ?
echo.
echo  1. Lancer le menu interactif
echo  2. Revenir au menu principal
echo  3. Quitter
echo.
echo ================================================================
echo.
set /p final_choice="Votre choix (1-3): "

if "%final_choice%"=="1" (
    start prixnc_menu.bat
    goto EXIT
)
if "%final_choice%"=="2" goto MENU_PRINCIPAL
goto EXIT

:EXIT
echo.
echo Merci d'avoir utilise l'installateur de Prix.nc Data Retrieval System.
echo Au revoir !
timeout /t 3 >nul
exit
