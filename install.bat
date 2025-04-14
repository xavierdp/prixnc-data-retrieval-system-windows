@echo off
echo === Installation de Prix.nc Data Retrieval System pour Windows ===
echo Ce script va installer toutes les dependances necessaires et configurer l'environnement.
echo.

:: Verification de Python
echo Verification de l'installation de Python...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez telecharger et installer Python depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher l'option "Add Python to PATH" lors de l'installation.
    echo Puis relancez ce script.
    pause
    exit /b 1
)

:: Verification de la version de Python
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
echo.

:: Verification de pip
echo Verification de l'installation de pip...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pip n'est pas installe. Installation en cours...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo Impossible d'installer pip. Veuillez l'installer manuellement.
        pause
        exit /b 1
    )
)
echo pip est installe.
echo.

:: Création d'un environnement virtuel (optionnel mais recommandé)
echo Voulez-vous creer un environnement virtuel pour ce projet? (o/n)
set /p use_venv=
if /i "%use_venv%"=="o" (
    echo Verification de l'installation de virtualenv...
    python -m pip install virtualenv
    echo Creation de l'environnement virtuel 'venv'...
    python -m virtualenv venv
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate
    echo Environnement virtuel active.
) else (
    echo Installation globale selectionnee (non recommande).
)
echo.

:: Installation des packages requis
echo Installation des dependances Python...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation des dependances.
    echo Tentative d'installation manuelle...
    
    echo Installation de requests...
    python -m pip install requests

    echo Verification de sqlite3 (inclus avec Python)...
    python -c "import sqlite3; print(f'SQLite version: {sqlite3.sqlite_version}')"
)
echo.

:: Initialisation de la base de données
echo Initialisation de la base de donnees...
python db_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'initialisation de la base de donnees.
    pause
    exit /b 1
)
echo Base de donnees initialisee avec succes.
echo.

:: Fin de l'installation
echo === Installation terminee ===
echo.
echo Pour utiliser Prix.nc Data Retrieval System:
if /i "%use_venv%"=="o" (
    echo 1. Activez l'environnement virtuel:
    echo    call venv\Scripts\activate
)
echo Pour recuperer tous les produits:
echo    python recuperer_produits.py
echo.
echo Pour visualiser les statistiques en temps reel:
echo    python simple_stats_viewer.py
echo.
echo Pour rechercher des produits:
echo    python prix_nc_manager.py --search "votre recherche"
echo.

if /i "%use_venv%"=="o" (
    echo Environnement virtuel actif. Vous pouvez commencer a utiliser le systeme.
) else (
    echo Vous pouvez maintenant commencer a utiliser le systeme.
)
echo.
pause
