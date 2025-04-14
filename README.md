# Prix.nc Data Retrieval System

## À propos

Prix.nc Data Retrieval System est un outil complet pour récupérer, stocker et analyser les données de l'API Prix.nc, le site de référence des prix en Nouvelle-Calédonie. Il offre une interface en ligne de commande permettant de récupérer différents types de données (produits, prix, communes, magasins...), d'effectuer des recherches avancées et d'exporter les résultats au format CSV.

## Fonctionnalités

- Récupération des données de l'API Prix.nc (produits, prix, annexes)
- Stockage dans une base de données SQLite locale
- Recherche avancée par différents critères (nom, origine, prix, secteur, etc.)
- Export des résultats au format CSV
- Visualisation des statistiques en temps réel
- Gestion des erreurs et mécanismes de reprise automatique
- Gestion robuste des particularités de l'API Prix.nc

## Installation

### Prérequis

- Linux (optimisé pour Debian 12)
- Accès à Internet
- Permissions suffisantes pour installer des packages

### Installation automatisée (recommandée pour Debian 12)

Utilisez le script d'installation automatique :

```bash
# Rendre le script exécutable
chmod +x install.sh

# Exécuter le script d'installation
./install.sh
```

Le script `install.sh` installera toutes les dépendances nécessaires, configurera l'environnement Python et préparera le système.

### Installation manuelle des dépendances système

```bash
# Mise à jour des paquets
apt update
apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev git
```

### Installation de pyenv (gestionnaire de versions Python)

```bash
# Installation de pyenv
curl https://pyenv.run | bash

# Configuration de l'environnement
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

### Installation de Python et configuration de l'environnement

```bash
# Installation de Python 3.10.x
pyenv install 3.10.17

# Création d'un environnement dédié au projet
mkdir -p /chemin/vers/projet
cd /chemin/vers/projet
pyenv local 3.10.17

# Création d'un fichier de profil pour l'environnement
cat << 'EOF' > .pyenv_profile
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
EOF

# Installation des dépendances Python
pip install -r requirements.txt
```

### Clonage du dépôt

```bash
git clone https://github.com/votre-compte/prixnc-data-retrieval-system.git
cd prixnc-data-retrieval-system
```

## Configuration

Le système ne nécessite pas de configuration particulière. Par défaut, il crée une base de données SQLite nommée `prix_nc.db` dans le répertoire courant.

## Utilisation

### Initialisation de la base de données

Avant d'utiliser le système, vous devez initialiser la base de données :

```bash
source .pyenv_profile
python db_setup.py
```

### Récupération des produits

Pour récupérer tous les produits de l'API Prix.nc et leurs prix associés :

```bash
source .pyenv_profile
python recuperer_produits.py
```

Options disponibles :
- `--limit` ou `-l` : Limite le nombre de produits à récupérer
- `--page-size` ou `-p` : Nombre d'éléments par page (défaut: 10)
- `--database` ou `-d` : Chemin vers la base de données
- `--initial-delay` : Délai initial entre les requêtes (défaut: 1.0 seconde)
- `--max-delay` : Délai maximum entre les requêtes (défaut: 10.0 secondes)
- `--reset` : Réinitialise les tables produits et prix avant de récupérer les données
- `--verify` : Vérifie et affiche les statistiques de pagination à la fin
- `--start-page` : Page de départ pour la récupération (utile pour reprendre après une interruption)

Exemple pour récupérer 500 produits par page en réinitialisant la base :
```bash
python recuperer_produits.py --page-size 500 --reset --verify
```

### Récupération des données annexes

Pour récupérer les données annexes (communes, magasins, secteurs, etc.) :

```bash
source .pyenv_profile
python prix_nc_manager.py --fetch-annexes
```

### Recherche de produits

Pour rechercher des produits dans la base de données :

```bash
source .pyenv_profile
python prix_nc_manager.py --search "lait" --export results.csv
```

Options de recherche :
- `--search` : Texte à rechercher dans le nom des produits
- `--origin` : Filtrer par origine
- `--min-price` : Prix minimum
- `--max-price` : Prix maximum
- `--sector` : Filtrer par secteur
- `--export` : Exporter les résultats dans un fichier CSV

### Visualisation des statistiques

Pour visualiser les statistiques en temps réel pendant la récupération des données :

```bash
source .pyenv_profile
python simple_stats_viewer.py
```

Le visualiseur affiche :
- Les statistiques générales (produits, prix, progression)
- Les taux d'extraction par minute
- Les produits récemment ajoutés
- Les produits sans prix
- Les prix récemment ajoutés (en XPF)
- L'activité récente via les logs

Options disponibles :
- `--database` ou `-d` : Chemin vers la base de données
- `--refresh` ou `-r` : Taux de rafraîchissement en secondes (défaut: 2)

### Affichage des tables

Pour afficher le contenu des tables de la base de données :

```bash
source .pyenv_profile
python print_table.py [nom_table] --limit 10
```

## Structure du projet

- `prix_nc_manager.py` : Script principal pour la gestion des données
- `db_setup.py` : Initialisation de la base de données
- `api_annexes.py` : Récupération des données annexes
- `recuperer_produits.py` : Script optimisé pour la récupération massive de produits
- `search.py` : Fonctionnalités de recherche
- `print_table.py` : Utilitaire d'affichage des tables
- `simple_stats_viewer.py` : Visualiseur de statistiques en temps réel

## Notes techniques et particularités

### Gestion des particularités de l'API Prix.nc

Le système gère une particularité importante de l'API Prix.nc : lorsqu'on effectue une requête pour récupérer les prix d'un produit spécifique (`/relevesprix?idProduit=XXX`), l'API retourne des prix pour des produits différents de celui demandé. Notre système :

1. Récupère l'ID du produit directement depuis chaque prix retourné par l'API
2. Vérifie l'existence du produit dans la base de données
3. Si le produit n'existe pas encore, l'ajoute automatiquement à la base
4. Associe correctement le prix au bon produit

Cette approche garantit la cohérence des données entre produits et prix.

### Optimisations pour Debian 12

- Le script d'installation `install.sh` est optimisé pour Debian 12
- Les commandes sont compatibles avec bash, le shell par défaut de Debian
- Les dépendances système sont adaptées aux paquets disponibles dans Debian 12

## Remarques

- Le code du projet est écrit en anglais, mais les commentaires sont en français conformément aux spécifications
- Le système effectue une gestion robuste des erreurs et des problèmes de connexion à l'API
- Les performances de recherche sont optimisées grâce à l'indexation des tables
- Les prix sont affichés en XPF (Franc Pacifique de Nouvelle-Calédonie)

## Licence

Ce projet est distribué sous licence [insérer licence ici].

## Contributeurs

[Liste des contributeurs]
