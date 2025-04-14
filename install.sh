#!/bin/bash

# Script d'installation pour Prix.nc Data Retrieval System
# Ce script installe toutes les dépendances nécessaires et configure l'environnement

echo "=== Installation de Prix.nc Data Retrieval System ==="
echo "Ce script doit être exécuté avec les permissions nécessaires pour installer des packages."
echo "Système d'exploitation recommandé : Debian 12 ou Ubuntu 22.04+"
echo ""

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Vérification des permissions
if [ "$(id -u)" -eq 0 ]; then
    # L'utilisateur est root, on peut continuer
    SUDO=""
    echo "Mode administrateur détecté."
else
    # L'utilisateur n'est pas root, on vérifie si sudo est disponible
    if command_exists sudo; then
        SUDO="sudo"
        echo "Mode utilisateur détecté, sudo sera utilisé."
    else
        echo "ERREUR: Ce script doit être exécuté avec les permissions administrateur ou avec sudo."
        echo "Si vous ne souhaitez pas utiliser sudo, vous devrez installer manuellement les dépendances."
        exit 1
    fi
fi

# Demande de confirmation
read -p "Continuer l'installation? (o/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "Installation annulée."
    exit 1
fi

# 1. Installation des dépendances système
echo "=== Installation des dépendances système ==="
$SUDO apt update
$SUDO apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev git python3-pip

# 2. Vérifier si pyenv est déjà installé
echo "=== Configuration de l'environnement Python ==="
if command_exists pyenv; then
    echo "pyenv déjà installé, mise à jour..."
    if [ -d "$HOME/.pyenv" ]; then
        cd "$HOME/.pyenv" && git pull && cd -
    fi
else
    echo "Installation de pyenv..."
    curl https://pyenv.run | bash
    
    # Ajout à .bashrc
    if ! grep -q "pyenv" "$HOME/.bashrc"; then
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$HOME/.bashrc"
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> "$HOME/.bashrc"
        echo 'eval "$(pyenv init --path)"' >> "$HOME/.bashrc"
        echo 'eval "$(pyenv init -)"' >> "$HOME/.bashrc"
    fi
    
    # Pour l'environnement actuel
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
fi

# 3. Installation de Python
PYTHON_VERSION="3.10.17"
if pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Python $PYTHON_VERSION déjà installé."
else
    echo "Installation de Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
fi

# 4. Configuration de l'environnement local
echo "=== Configuration de l'environnement local ==="
pyenv local $PYTHON_VERSION

# 5. Création du profil pour l'environnement
cat > .pyenv_profile << 'EOF'
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
EOF

echo "=== Installation des dépendances Python ==="
pip install -r requirements.txt

# 6. Initialisation de la base de données
echo "=== Initialisation de la base de données ==="
source .pyenv_profile
python db_setup.py

echo "=== Installation terminée ==="
echo ""
echo "Pour utiliser Prix.nc Data Retrieval System, exécutez:"
echo "  source .pyenv_profile"
echo "  python prix_nc_manager.py --help"
echo ""
echo "Pour récupérer toutes les données:"
echo "  source .pyenv_profile"
echo "  python recuperer_produits.py"
echo ""
echo "Pour visualiser les statistiques en temps réel:"
echo "  source .pyenv_profile"
echo "  python simple_stats_viewer.py"
echo ""
