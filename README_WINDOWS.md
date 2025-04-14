# Guide d'installation et d'utilisation de Prix.nc Data Retrieval System pour Windows

## Introduction

Ce guide explique comment installer et utiliser Prix.nc Data Retrieval System sur un système Windows. Le projet original a été conçu pour Linux, mais cette documentation vous aidera à l'adapter pour Windows.

## Prérequis

- **Windows 10/11**
- **Connexion Internet**
- **Droits d'administrateur** (recommandé mais pas obligatoire)

## Installation étape par étape

### 1. Installer Python

Si Python n'est pas déjà installé :

1. Téléchargez Python (version 3.10 ou supérieure) depuis [python.org](https://www.python.org/downloads/windows/)
2. Lancez l'installateur
3. **Important :** Cochez la case "Add Python to PATH"
4. Cliquez sur "Install Now" pour une installation standard

Pour vérifier l'installation, ouvrez une invite de commande (cmd) et tapez :
```
python --version
```

### 2. Installer Git (si pas déjà fait)

Si Git n'est pas déjà installé :

1. Téléchargez Git depuis [git-scm.com](https://git-scm.com/download/win)
2. Lancez l'installateur et suivez les instructions par défaut

### 3. Cloner le dépôt

Ouvrez une invite de commande (cmd) ou PowerShell et exécutez :

```
git clone https://github.com/xavierdp/prixnc-data-retrieval-system.git
cd prixnc-data-retrieval-system
```

Ou si vous avez déjà cloné avec SSH :
```
git clone git@github.com:xavierdp/prixnc-data-retrieval-system.git
cd prixnc-data-retrieval-system
```

### 4. Lancer le script d'installation Windows

Double-cliquez sur `install.bat` ou exécutez-le depuis l'invite de commande :

```
install.bat
```

Ce script va :
- Vérifier l'installation de Python
- Installer pip si nécessaire
- Proposer de créer un environnement virtuel (recommandé)
- Installer les dépendances requises
- Initialiser la base de données

## Utilisation du système

### Activer l'environnement virtuel (si vous en avez créé un)

Avant d'utiliser le système, activez l'environnement virtuel :

```
venv\Scripts\activate
```

### Récupérer les données de produits

Pour récupérer tous les produits et leurs prix :

```
python recuperer_produits.py
```

Options disponibles :
- `--limit` ou `-l` : Limite le nombre de produits à récupérer
- `--page-size` ou `-p` : Nombre d'éléments par page (défaut: 10)
- `--reset` : Réinitialise les tables produits et prix avant récupération

### Visualiser les statistiques en temps réel

```
python simple_stats_viewer.py
```

### Rechercher des produits

```
python prix_nc_manager.py --search "lait"
```

Pour exporter les résultats en CSV :
```
python prix_nc_manager.py --search "lait" --export results.csv
```

## Résolution des problèmes courants

### Problème d'importation de SQLite3

SQLite3 est normalement inclus avec Python. Si vous rencontrez une erreur, vérifiez :

```python
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

### Erreurs de connexion à l'API

Si vous rencontrez des erreurs lors de la récupération des données :
- Vérifiez votre connexion Internet
- Augmentez les délais entre requêtes avec `--initial-delay 2.0`

### Erreurs "Command not found"

Assurez-vous d'être dans le bon répertoire :
```
cd chemin\vers\prixnc-data-retrieval-system
```

## Notes spécifiques à Windows

- Les chemins utilisent des backslash (`\`) au lieu des slash (`/`)
- La base de données sera créée dans le répertoire courant sous le nom `prix_nc.db`
- Utilisez `cls` au lieu de `clear` pour effacer l'écran du terminal

## FAQ

**Q: Dois-je installer SQLite manuellement ?**  
R: Non, SQLite est inclus avec Python standard.

**Q: Comment puis-je voir le contenu de la base de données ?**  
R: Utilisez `python print_table.py produits --limit 10` pour afficher les 10 premiers produits.

**Q: Comment arrêter une récupération en cours ?**  
R: Appuyez sur Ctrl+C dans la fenêtre du terminal.

**Q: Est-ce que je peux automatiser la récupération régulière des données ?**  
R: Oui, utilisez le Planificateur de tâches Windows pour exécuter les scripts périodiquement.

## Logiciels recommandés pour Windows

- **DB Browser for SQLite** : Visualiser et gérer la base de données SQLite
- **Visual Studio Code** : Éditer les scripts Python si besoin
- **Windows Terminal** : Terminal moderne pour Windows avec onglets et personnalisation
