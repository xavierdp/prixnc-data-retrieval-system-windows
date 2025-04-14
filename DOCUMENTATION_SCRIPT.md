# Documentation de Prix.nc Manager

## À propos

`prix_nc_manager.py` est le script principal du système Prix.nc Data Retrieval System. Il permet de :
- Récupérer des données depuis l'API Prix.nc
- Effectuer des recherches dans la base de données
- Exporter les données vers des fichiers CSV
- Afficher des statistiques sur les données

## Menu interactif

Le système inclut un menu interactif (`prixnc_menu.bat`) qui permet d'accéder facilement à toutes les fonctionnalités principales :

1. **Récupérer tous les produits** - Récupère tous les produits et leurs prix
2. **Récupérer 100 produits seulement (test)** - Récupère un échantillon de 100 produits pour tester
3. **Récupérer UNIQUEMENT les tables annexes** - Récupère toutes les données annexes (communes, magasins, secteurs, etc.)
4. **Récupérer tables annexes PUIS produits** - Récupère d'abord les tables annexes, puis les produits et prix (approche recommandée)
5. **Visualiser les statistiques** - Affiche les statistiques en temps réel de la base de données
6. **Rechercher des produits** - Effectue une recherche par nom de produit
7. **Exporter les résultats en CSV** - Recherche des produits et exporte les résultats en CSV
8. **Vérifier la configuration** - Vérifie que tout est correctement installé et configuré
9. **Quitter** - Quitte le programme

Il est **fortement recommandé** d'utiliser l'option 4 **(Récupérer tables annexes PUIS produits)** car cela garantit que toutes les références nécessaires sont disponibles dans la base de données avant de récupérer les produits.

## Options disponibles pour le script prix_nc_manager.py

### Options générales

| Option | Forme courte | Description |
|--------|--------------|-------------|
| `--limit LIMIT` | `-l LIMIT` | Limite le nombre de produits à récupérer |
| `--page-size SIZE` | `-p SIZE` | Nombre de produits par page (défaut: 20) |
| `--start-page PAGE` | `-s PAGE` | Page de départ (défaut: 0) |
| `--output FILE` | `-o FILE` | Nom du fichier CSV de sortie (défaut: produits_prix_nc.csv) |
| `--database FILE` | `-d FILE` | Nom de la base de données SQLite (défaut: prix_nc.db) |
| `--stats` | | Afficher les statistiques de la base de données |
| `--export-only` | | Exporter uniquement les données existantes sans en récupérer de nouvelles |
| `--print` | | Afficher les données récupérées |

### Options pour les tables principales

| Option | Description |
|--------|-------------|
| `--communes` | Récupérer la liste des communes |
| `--magasins` | Récupérer la liste des magasins |
| `--produits` | Récupérer la liste des produits (inclut automatiquement les prix) |
| `--produits-sans-prix` | Récupérer uniquement les produits sans leurs prix |
| `--prix` | Récupérer uniquement les prix (nécessite --product-id) |
| `--all-except-products` | Récupérer toutes les données annexes sauf les produits |

### Options pour les tables de données annexes

| Option | Description |
|--------|-------------|
| `--annexes` | Récupérer toutes les données annexes |
| `--secteurs` | Récupérer uniquement les secteurs de consommation |
| `--sous-secteurs` | Récupérer uniquement les sous-secteurs de consommation |
| `--types-commerce` | Récupérer uniquement les types de commerce |
| `--marques` | Récupérer uniquement les marques |
| `--varietes` | Récupérer uniquement les variétés |
| `--boucliers` | Récupérer uniquement les boucliers qualité prix |

### Options de recherche

| Option | Description |
|--------|-------------|
| `--search` | Activer le mode recherche |
| `--nom NOM` | Rechercher par nom de produit |
| `--origine ORIGINE` | Rechercher par origine du produit (LOCAL, IMPORT, INCONNU, SERVICE) |
| `--type-produit TYPE` | Rechercher par type de produit |
| `--secteur-search SECTEUR` | Rechercher par secteur de consommation |
| `--sous-secteur-search SOUS_SECTEUR` | Rechercher par sous-secteur de consommation |
| `--prix-min PRIX` | Prix minimum pour la recherche |
| `--prix-max PRIX` | Prix maximum pour la recherche |
| `--commune-search COMMUNE` | Rechercher par commune |
| `--magasin-search MAGASIN` | Rechercher par magasin |
| `--search-output FILE` | Nom du fichier CSV pour les résultats de recherche (défaut: search_results.csv) |
| `--export-search` | Exporter les résultats de recherche au format CSV standard |

### Options pour les listes de valeurs

| Option | Description |
|--------|-------------|
| `--list-values FIELD` | Afficher les valeurs distinctes pour un champ (par exemple: origine, secteur, sous_secteur, marque) |
| `--list-table TABLE` | Table dans laquelle rechercher les valeurs distinctes (défaut: produits) |

### Autres options

| Option | Description |
|--------|-------------|
| `--last-update` | Exporter les dates de dernière mise à jour des prix |
| `--product-id ID` | ID du produit pour lequel récupérer les détails des prix |

## Exemples d'utilisation

### Approche recommandée pour une récupération complète

Pour une récupération complète des données, le processus recommandé est :

1. Récupérer d'abord toutes les tables annexes :
```bash
python prix_nc_manager.py --all-except-products
```

2. Puis récupérer les produits et leurs prix :
```bash
python recuperer_produits.py
```

Cette approche est également disponible via le menu interactif (option 4).

### Récupération de données

#### Récupérer tous les produits et leurs prix
```bash
python prix_nc_manager.py --produits
```

#### Récupérer une quantité limitée de produits
```bash
python prix_nc_manager.py --produits --limit 100
```

#### Récupérer uniquement les produits sans leurs prix
```bash
python prix_nc_manager.py --produits-sans-prix
```

#### Récupérer les prix d'un produit spécifique
```bash
python prix_nc_manager.py --prix --product-id "01af07eb-e9f6-4925-a715-ac6ca362fc95"
```

#### Récupérer la liste des communes
```bash
python prix_nc_manager.py --communes
```

#### Récupérer la liste des magasins
```bash
python prix_nc_manager.py --magasins
```

#### Récupérer toutes les données annexes
```bash
python prix_nc_manager.py --annexes
```

#### Récupérer toutes les données sauf les produits
```bash
python prix_nc_manager.py --all-except-products
```

### Recherche

#### Rechercher des produits par nom
```bash
python prix_nc_manager.py --search --nom "lait"
```

#### Rechercher des produits par origine
```bash
python prix_nc_manager.py --search --origine "LOCAL"
```

#### Rechercher des produits par gamme de prix
```bash
python prix_nc_manager.py --search --prix-min 500 --prix-max 1000
```

#### Rechercher des produits par secteur
```bash
python prix_nc_manager.py --search --secteur-search "Alimentation"
```

#### Rechercher par commune
```bash
python prix_nc_manager.py --search --commune-search "Nouméa"
```

#### Combinaison de critères de recherche
```bash
python prix_nc_manager.py --search --nom "riz" --origine "IMPORT" --prix-max 1500
```

### Export de données

#### Exporter les résultats de recherche
```bash
python prix_nc_manager.py --search --nom "lait" --export-search
```

#### Exporter les résultats de recherche dans un fichier spécifique
```bash
python prix_nc_manager.py --search --nom "lait" --search-output "resultats_lait.csv"
```

#### Exporter les dates de dernière mise à jour des prix
```bash
python prix_nc_manager.py --last-update
```

### Autres fonctionnalités

#### Afficher les statistiques de la base de données
```bash
python prix_nc_manager.py --stats
```

#### Afficher les valeurs distinctes pour un champ
```bash
python prix_nc_manager.py --list-values "origine"
```

#### Afficher les valeurs distinctes pour un champ dans une table spécifique
```bash
python prix_nc_manager.py --list-values "type_commerce" --list-table "magasins"
```

## Astuces

1. **Processus recommandé** : Toujours récupérer les tables annexes avant de récupérer les produits :
```bash
python prix_nc_manager.py --all-except-products
python recuperer_produits.py --limit 5000 --page-size 100
```

2. Pour obtenir la liste complète des secteurs disponibles :
```bash
python prix_nc_manager.py --list-values "secteur"
```

3. Pour exporter tout le contenu de la base de données :
```bash
python prix_nc_manager.py --export-only
```

4. Pour afficher les statistiques complètes de la base de données :
```bash
python prix_nc_manager.py --stats
```

5. Pour rechercher tous les produits d'une certaine gamme de prix dans une commune spécifique :
```bash
python prix_nc_manager.py --search --prix-min 500 --prix-max 2000 --commune-search "Nouméa"
```

## Notes importantes

1. Le script utilise par défaut la base de données `prix_nc.db` dans le répertoire courant.
2. L'exportation se fait dans le format CSV, compatible avec Excel et autres tableurs.
3. Le script gère automatiquement les erreurs de connexion à l'API et tente de reprendre en cas d'échec.
4. Les prix sont toujours exprimés en XPF (Franc Pacifique).
5. Pour une récupération complète et cohérente, il est fortement recommandé de récupérer toutes les tables annexes avant de récupérer les produits (utilisez l'option 4 du menu interactif).
6. Pour cloner le dépôt, utilisez le protocole HTTP :
   ```
   git clone https://github.com/xavierdp/prixnc-data-retrieval-system-windows.git
   ```
