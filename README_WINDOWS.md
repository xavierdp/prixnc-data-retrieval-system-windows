# Guide d'installation et d'utilisation de Prix.nc Data Retrieval System pour Windows

## Introduction

Ce guide explique comment installer et utiliser Prix.nc Data Retrieval System sur un système Windows. Le projet original a été conçu pour Linux, mais cette documentation vous aidera à l'adapter pour Windows.

## Prérequis

- **Windows 10/11**
- **Connexion Internet**
- **Droits d'administrateur** (recommandé mais pas obligatoire)

## Installation étape par étape

### Méthode simple : Installateur complet

1. Téléchargez l'installateur complet depuis le dépôt en clonant avec le protocole HTTP :
   ```
   git clone https://github.com/xavierdp/prixnc-data-retrieval-system-windows.git
   ```

2. Double-cliquez sur `installer_complet.bat`
3. Sélectionnez "7. Installer tout automatiquement" pour une installation complète en une étape
4. Ou naviguez dans le menu pour installer les composants individuellement

L'installateur s'occupera de :
- Installer Python via winget (si nécessaire)
- Ajouter Python au PATH système
- Installer les dépendances Python
- Initialiser la base de données
- Vous proposer de lancer le menu interactif

### Installation manuelle de Python (si l'installateur échoue)

#### Option 1 : Installation via winget
```
winget install -e --id Python.Python.3.10 --accept-package-agreements --accept-source-agreements
```

#### Option 2 : Installation manuelle
1. Téléchargez Python (version 3.10 ou supérieure) depuis [python.org](https://www.python.org/downloads/windows/)
2. Lancez l'installateur
3. **Important :** Cochez la case "Add Python to PATH"
4. Cliquez sur "Install Now" pour une installation standard

## Utilisation du système

### Option 1 : Utiliser le menu interactif (méthode la plus simple)
Double-cliquez sur `prixnc_menu.bat` et sélectionnez l'option désirée dans le menu.

### Option 2 : Utiliser les commandes Python directement

Si Python n'est pas dans votre PATH, utilisez le chemin complet :
```
C:\Users\[votre_nom]\AppData\Local\Programs\Python\Python310\python.exe recuperer_produits.py
```

Si Python est dans votre PATH :
```
python recuperer_produits.py
```

Options disponibles :
- `--limit` ou `-l` : Limite le nombre de produits à récupérer
- `--page-size` ou `-p` : Nombre d'éléments par page (défaut: 10)
- `--reset` : Réinitialises les tables produits et prix avant récupération

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

### Python n'est pas reconnu comme une commande

Si vous recevez une erreur comme "Python n'est pas reconnu comme une commande interne ou externe", vous avez deux options :
1. Redémarrer votre ordinateur pour que les modifications du PATH prennent effet
2. Utiliser le chemin complet vers Python : `C:\Users\[votre_nom]\AppData\Local\Programs\Python\Python310\python.exe`

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
cd chemin\vers\prixnc-data-retrieval-system-windows
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

**Q: Python est installé mais la commande 'python' n'est pas reconnue, que faire ?**  
R: Soit redémarrez votre ordinateur, soit utilisez le chemin complet vers l'exécutable Python.

## Logiciels recommandés pour Windows

- **DB Browser for SQLite** : Visualiser et gérer la base de données SQLite
- **Visual Studio Code** : Éditer les scripts Python si besoin
- **Windows Terminal** : Terminal moderne pour Windows avec onglets et personnalisation
