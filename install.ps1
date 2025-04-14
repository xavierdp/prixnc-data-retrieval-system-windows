# Script d'installation pour Prix.nc Data Retrieval System sur Windows
Write-Host "=== Installation de Prix.nc Data Retrieval System pour Windows ===" -ForegroundColor Green
Write-Host "Ce script va installer toutes les dépendances nécessaires et configurer l'environnement."
Write-Host ""

# Fonction pour vérifier si une commande existe
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Vérification de Python
Write-Host "Vérification de l'installation de Python..." -ForegroundColor Yellow
if (-not (Test-CommandExists python)) {
    Write-Host "Python n'est pas installé ou n'est pas dans le PATH." -ForegroundColor Red
    Write-Host "Veuillez télécharger et installer Python depuis https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Assurez-vous de cocher l'option 'Add Python to PATH' lors de l'installation." -ForegroundColor Red
    Write-Host "Puis relancez ce script." -ForegroundColor Red
    Read-Host -Prompt "Appuyez sur Entrée pour quitter"
    exit 1
}

# Vérification de la version de Python
$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
Write-Host "Python $pythonVersion détecté" -ForegroundColor Green
Write-Host ""

# Vérification de pip
Write-Host "Vérification de l'installation de pip..." -ForegroundColor Yellow
if (-not (python -m pip --version)) {
    Write-Host "pip n'est pas installé. Installation en cours..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
    if (-not $?) {
        Write-Host "Impossible d'installer pip. Veuillez l'installer manuellement." -ForegroundColor Red
        Read-Host -Prompt "Appuyez sur Entrée pour quitter"
        exit 1
    }
}
Write-Host "pip est installé." -ForegroundColor Green
Write-Host ""

# Création d'un environnement virtuel (optionnel mais recommandé)
$useVenv = Read-Host "Voulez-vous créer un environnement virtuel pour ce projet? (o/n)"
if ($useVenv -eq "o") {
    Write-Host "Vérification de l'installation de virtualenv..." -ForegroundColor Yellow
    python -m pip install virtualenv
    Write-Host "Création de l'environnement virtuel 'venv'..." -ForegroundColor Yellow
    python -m virtualenv venv
    Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    Write-Host "Environnement virtuel activé." -ForegroundColor Green
} else {
    Write-Host "Installation globale sélectionnée (non recommandé)." -ForegroundColor Yellow
}
Write-Host ""

# Installation des packages requis
Write-Host "Installation des dépendances Python..." -ForegroundColor Yellow
python -m pip install -r requirements.txt
if (-not $?) {
    Write-Host "Erreur lors de l'installation des dépendances." -ForegroundColor Red
    Write-Host "Tentative d'installation manuelle..." -ForegroundColor Yellow
    
    Write-Host "Installation de requests..." -ForegroundColor Yellow
    python -m pip install requests

    Write-Host "Vérification de sqlite3 (inclus avec Python)..." -ForegroundColor Yellow
    python -c "import sqlite3; print(f'SQLite version: {sqlite3.sqlite_version}')"
}
Write-Host "Dépendances installées avec succès." -ForegroundColor Green
Write-Host ""

# Initialisation de la base de données
Write-Host "Initialisation de la base de données..." -ForegroundColor Yellow
python db_setup.py
if (-not $?) {
    Write-Host "Erreur lors de l'initialisation de la base de données." -ForegroundColor Red
    Read-Host -Prompt "Appuyez sur Entrée pour quitter"
    exit 1
}
Write-Host "Base de données initialisée avec succès." -ForegroundColor Green
Write-Host ""

# Fin de l'installation
Write-Host "=== Installation terminée ===" -ForegroundColor Green
Write-Host ""
Write-Host "Pour utiliser Prix.nc Data Retrieval System:" -ForegroundColor Cyan
if ($useVenv -eq "o") {
    Write-Host "1. Activez l'environnement virtuel:" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
}
Write-Host "Pour récupérer tous les produits:" -ForegroundColor Cyan
Write-Host "   python recuperer_produits.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour visualiser les statistiques en temps réel:" -ForegroundColor Cyan
Write-Host "   python simple_stats_viewer.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour rechercher des produits:" -ForegroundColor Cyan
Write-Host "   python prix_nc_manager.py --search ""votre recherche""" -ForegroundColor Cyan
Write-Host ""

if ($useVenv -eq "o") {
    Write-Host "Environnement virtuel actif. Vous pouvez commencer à utiliser le système." -ForegroundColor Green
} else {
    Write-Host "Vous pouvez maintenant commencer à utiliser le système." -ForegroundColor Green
}
Write-Host ""
Read-Host -Prompt "Appuyez sur Entrée pour quitter"
