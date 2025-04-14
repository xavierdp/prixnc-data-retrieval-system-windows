#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import requests
import json
import csv
import argparse
from datetime import datetime
import os
from db_setup import create_database
from api_annexes import APIAnnexes
from search import ProduitSearch
import logging
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prix_nc.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("prix_nc")

class PrixNCManager:
    """
    Classe pour gérer les interactions avec l'API Prix.nc
    """
    
    def __init__(self, db_path="prix_nc.db"):
        """
        Initialisation de la classe avec la base de données
        """
        self.base_url = "https://prix.nc/api/v1"
        self.db_path = db_path
        
        # Initialisation de la base de données si elle n'existe pas
        if not os.path.exists(db_path):
            logger.info(f"Création de la base de données: {db_path}")
            create_database(db_path)
        else:
            logger.info(f"Utilisation de la base de données existante: {db_path}")
        
        # Initialisation des modules annexes
        self.api_annexes = APIAnnexes(base_url=self.base_url, db_path=self.db_path)
        self.search_engine = ProduitSearch(db_path=self.db_path)
        
        # Configuration des tentatives de reconnexion
        self.max_retries = 3
        self.retry_delay = 2  # secondes
    
    def _make_request(self, url, method="GET", data=None, headers=None):
        """
        Effectue une requête HTTP avec gestion des erreurs et tentatives de reconnexion
        """
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "PrixNC-DataRetriever/1.0"
        }
        
        if headers:
            default_headers.update(headers)
        
        retry_count = 0
        max_retries = self.max_retries
        
        while retry_count < max_retries:
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=default_headers, timeout=30)
                elif method.upper() == "POST":
                    response = requests.post(url, json=data, headers=default_headers, timeout=30)
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")
                
                # Si on reçoit un code 429 (trop de requêtes), on attend et on réessaie
                if response.status_code == 429:
                    retry_count += 1
                    wait_time = response.headers.get('Retry-After', self.retry_delay * (2 ** retry_count))
                    logger.warning(f"Trop de requêtes (429). Attente de {wait_time} secondes avant de réessayer...")
                    time.sleep(float(wait_time))
                    continue
                
                return response
                
            except requests.exceptions.ConnectionError:
                retry_count += 1
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.error(f"Erreur de connexion. Tentative de reconnexion {retry_count}/{max_retries} dans {wait_time} secondes...")
                time.sleep(wait_time)
            except requests.exceptions.Timeout:
                retry_count += 1
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.error(f"Délai d'attente dépassé. Tentative {retry_count}/{max_retries} dans {wait_time} secondes...")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Erreur lors de la requête: {str(e)}")
                raise
        
        raise requests.exceptions.RequestException(f"Échec après {max_retries} tentatives.")
    
    # Autres méthodes...
    
    def fetch_products(self, limit=None, page_size=20, start_page=0, fetch_prices=True):
        """
        Récupère les produits depuis l'API avec pagination
        
        Args:
            limit: Nombre maximum de produits à récupérer (None pour tous)
            page_size: Taille de chaque page de résultats
            start_page: Page à partir de laquelle commencer
            fetch_prices: Si True, récupère également les prix détaillés pour chaque produit
        """
        total_products = 0
        current_page = start_page
        products_retrieved = 0
        total_prices = 0
        
        logger.info(f"Début de la récupération des produits (limite: {limit if limit else 'illimitée'})...")
        
        while True:
            try:
                # Récupération d'une page de produits
                url = f"{self.base_url}/produitsprix?page={current_page}&size={page_size}"
                logger.info(f"Récupération de la page {current_page}...")
                
                response = self._make_request(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Vérification de la structure de la réponse
                    if "_embedded" in data and "produitsprix" in data["_embedded"]:
                        products = data["_embedded"]["produitsprix"]
                        
                        if not products:
                            logger.info("Plus de produits à récupérer")
                            break
                            
                        # Sauvegarde dans la base de données
                        self.save_products_to_db(products)
                        
                        products_retrieved += len(products)
                        logger.info(f"Page {current_page}: {len(products)} produits récupérés")
                        
                        # Récupération des prix détaillés pour chaque produit si demandé
                        if fetch_prices:
                            page_prices = 0
                            for product in products:
                                product_id = product.get("idProduit")
                                if product_id:
                                    prices_count = self.fetch_product_prices(product_id)
                                    page_prices += prices_count
                            
                            total_prices += page_prices
                            logger.info(f"Page {current_page}: {page_prices} prix récupérés")
                        
                        # Vérification si nous avons atteint la limite
                        if limit is not None and products_retrieved >= limit:
                            logger.info(f"Limite de {limit} produits atteinte")
                            break
                            
                        # Passage à la page suivante
                        current_page += 1
                        
                        # Information sur la pagination
                        if "page" in data:
                            total_pages = data["page"].get("totalPages", 0)
                            total_elements = data["page"].get("totalElements", 0)
                            
                            if current_page >= total_pages:
                                logger.info(f"Toutes les pages ont été traitées ({total_pages} pages)")
                                break
                                
                            logger.info(f"Progression: {products_retrieved}/{total_elements} produits ({current_page}/{total_pages} pages)")
                        else:
                            # Si nous n'avons pas d'informations sur la pagination, on continue
                            pass
                    else:
                        logger.error("Structure de données inattendue dans la réponse de l'API")
                        break
                else:
                    logger.error(f"Erreur lors de la récupération des produits: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des produits: {str(e)}")
                break
        
        if fetch_prices:
            return products_retrieved, total_prices
        else:
            return products_retrieved
            
    def fetch_product_prices(self, product_id):
        """
        Récupère les prix détaillés d'un produit spécifique
        """
        try:
            # Utiliser l'endpoint des relevés de prix pour un produit spécifique
            url = f"{self.base_url}/relevesprix/search/findByIdProduitOrderByPrixParUniteAscPrixAscMagasinAsc?idProduit={product_id}"
            logger.info(f"Récupération des prix pour le produit {product_id}...")
            
            response = self._make_request(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "relevesprix" in data["_embedded"]:
                    prices = data["_embedded"]["relevesprix"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for price in prices:
                        cursor.execute(
                            """
                            INSERT INTO prix 
                            (id_produit, prix, prix_par_unite, unite_label, unite_label_court, promotion, id_commune, commune)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                price.get("idProduit", ""),
                                price.get("prix", 0),
                                price.get("prixParUnite", 0),
                                price.get("uniteLabel", ""),
                                price.get("uniteLabelCourt", ""),
                                price.get("promotion", False),
                                price.get("idCommune", ""),
                                price.get("commune", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"{len(prices)} prix récupérés pour le produit {product_id}")
                    return len(prices)
                else:
                    logger.error("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                logger.error(f"Erreur lors de la récupération des prix: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des prix: {str(e)}")
            return 0
            
    def save_products_to_db(self, products):
        """
        Sauvegarde les produits dans la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product in products:
            # Tentative d'insertion - si le produit existe déjà, cette requête sera ignorée
            cursor.execute(
                """
                INSERT OR IGNORE INTO produits 
                (id, intitule, origine, type, id_secteur, secteur, id_sous_secteur, sous_secteur, date_creation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    product.get("idProduit", ""),
                    product.get("nom", ""),
                    product.get("origine", ""),
                    "PRIX",  # Par défaut, nous utilisons "PRIX" comme type
                    product.get("idSecteurConso", ""),
                    product.get("secteurConso", ""),
                    product.get("idSsSecteurConso", ""),
                    product.get("sousSecteurConso", "")
                )
            )
            
            # Mise à jour si le produit existait déjà
            cursor.execute(
                """
                UPDATE produits SET
                    intitule = ?,
                    origine = ?,
                    type = ?,
                    id_secteur = ?,
                    secteur = ?,
                    id_sous_secteur = ?,
                    sous_secteur = ?,
                    date_mise_a_jour = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    product.get("nom", ""),
                    product.get("origine", ""),
                    "PRIX",  # Par défaut, nous utilisons "PRIX" comme type
                    product.get("idSecteurConso", ""),
                    product.get("secteurConso", ""),
                    product.get("idSsSecteurConso", ""),
                    product.get("sousSecteurConso", ""),
                    product.get("idProduit", "")
                )
            )
            
            # Récupération des informations de prix si elles existent
            if "meilleurPrix" in product:
                cursor.execute(
                    """
                    INSERT INTO prix 
                    (id_produit, prix, prix_par_unite, unite_label, unite_label_court, promotion, id_commune, commune)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product.get("idProduit", ""),
                        product.get("meilleurPrix", 0),
                        product.get("meilleurPrixParUnite", 0),
                        product.get("uniteLabel", ""),
                        product.get("uniteLabelCourt", ""),
                        product.get("promotion", False),
                        product.get("idCommune", ""),
                        product.get("commune", "")
                    )
                )
        
        conn.commit()
        conn.close()

    def fetch_annexes(self):
        """
        Récupère toutes les données annexes (secteurs, sous-secteurs, marques, etc.)
        """
        return self.api_annexes.fetch_all_annexes()

    def fetch_secteurs(self):
        """
    Récupère uniquement les secteurs de consommation
    """
        return self.api_annexes.fetch_secteurs()
        
    def fetch_sous_secteurs(self):
        """
    Récupère uniquement les sous-secteurs de consommation
    """
        return self.api_annexes.fetch_sous_secteurs()
        
    def fetch_types_commerce(self):
        """
    Récupère uniquement les types de commerce
    """
        return self.api_annexes.fetch_types_commerce()
        
    def fetch_marques(self):
        """
    Récupère uniquement les marques
    """
        return self.api_annexes.fetch_marques()
        
    def fetch_varietes(self):
        """
    Récupère uniquement les variétés
    """
        return self.api_annexes.fetch_varietes()
        
    def fetch_boucliers(self):
        """
    Récupère uniquement les boucliers qualité prix
    """
        return self.api_annexes.fetch_boucliers()

    def fetch_communes(self):
        """
        Récupère la liste des communes depuis l'API
        """
        try:
            url = f"{self.base_url}/communes"
            logger.info("Récupération des communes...")
            
            response = self._make_request(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "communes" in data["_embedded"]:
                    communes = data["_embedded"]["communes"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for commune in communes:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO communes 
                            (id, nom, province, date_mise_a_jour)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                commune["id"],
                                commune.get("commune", ""),
                                commune.get("province", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"{len(communes)} communes récupérées et enregistrées")
                    return len(communes)
                else:
                    logger.error("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                logger.error(f"Erreur lors de la récupération des communes: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des communes: {str(e)}")
            return 0
    
    def fetch_magasins(self):
        """
        Récupère la liste des magasins depuis l'API
        """
        try:
            url = f"{self.base_url}/magasins"
            logger.info("Récupération des magasins...")
            
            response = self._make_request(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "magasins" in data["_embedded"]:
                    magasins = data["_embedded"]["magasins"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for magasin in magasins:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO magasins 
                            (id, label, id_commune, commune, province, zone_geo, longitude, latitude, id_type_commerce, type_commerce, date_mise_a_jour)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                magasin.get("id", ""),
                                magasin.get("label", ""),
                                magasin.get("idCommune", ""),
                                magasin.get("commune", ""),
                                magasin.get("province", ""),
                                magasin.get("zoneGeo", ""),
                                magasin.get("longitude", 0),
                                magasin.get("latitude", 0),
                                magasin.get("idTypeCommerce", ""),
                                magasin.get("typeCommerce", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"{len(magasins)} magasins récupérés et enregistrés")
                    return len(magasins)
                else:
                    logger.error("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                logger.error(f"Erreur lors de la récupération des magasins: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des magasins: {str(e)}")
            return 0
            
    def search_products(self, **kwargs):
        """
        Recherche des produits selon différents critères
        """
        return self.search_engine.search_products(**kwargs)
    
    def export_search_results(self, results, output_file="search_results.csv"):
        """
        Exporte les résultats de recherche vers un fichier CSV
        """
        return self.search_engine.export_search_results_to_csv(results, output_file)
    
    def get_distinct_values(self, field, table="produits"):
        """
        Récupère toutes les valeurs distinctes pour un champ donné
        """
        return self.search_engine.get_distinct_values(field, table)
        
    def export_to_csv(self, output_file="produits_prix_nc.csv", **search_criteria):
        """
        Exporte les données de la base vers un fichier CSV
        Peut filtrer les données selon les critères de recherche passés en paramètres
        """
        # Si des critères de recherche sont fournis, on utilise le moteur de recherche
        if search_criteria:
            results = self.search_products(**search_criteria)
            
            if not results:
                logger.info("Aucun résultat correspondant aux critères de recherche")
                return 0
            
            # Préparation des données pour le CSV au format habituel
            rows_for_csv = []
            for result in results:
                # Pour chaque produit, on pourrait avoir plusieurs prix si le prix_min et prix_max sont différents
                # On exporte alors une ligne par prix
                if result['prix_min'] == result['prix_max'] and result['prix_min'] is not None:
                    # Un seul prix disponible
                    rows_for_csv.append({
                        'intitule': result['intitule'],
                        'prix': result['prix_min'],
                        'localisation': result.get('communes', ''),
                        'origine': result['origine'],
                        'type': result['type'],
                        'date_mise_a_jour': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    # Plusieurs prix disponibles, on ajoute deux lignes (min et max)
                    if result['prix_min'] is not None:
                        rows_for_csv.append({
                            'intitule': result['intitule'] + ' (prix min)',
                            'prix': result['prix_min'],
                            'localisation': result.get('communes', ''),
                            'origine': result['origine'],
                            'type': result['type'],
                            'date_mise_a_jour': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    if result['prix_max'] is not None and result['prix_max'] != result['prix_min']:
                        rows_for_csv.append({
                            'intitule': result['intitule'] + ' (prix max)',
                            'prix': result['prix_max'],
                            'localisation': result.get('communes', ''),
                            'origine': result['origine'],
                            'type': result['type'],
                            'date_mise_a_jour': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
            
            # Écriture dans le fichier CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['intitule', 'prix', 'localisation', 'origine', 'type', 'date_mise_a_jour'])
                writer.writeheader()
                writer.writerows(rows_for_csv)
            
            return len(rows_for_csv)
        else:
            # Comportement original sans critères de recherche
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Requête pour obtenir les données formatées comme demandé
            cursor.execute("""
                SELECT 
                    p.intitule, 
                    pr.prix, 
                    pr.commune as localisation, 
                    p.origine, 
                    p.type,
                    pr.date_releve as date_mise_a_jour
                FROM 
                    produits p
                LEFT JOIN 
                    prix pr ON p.id = pr.id_produit
                ORDER BY
                    p.intitule
            """)
            
            rows = cursor.fetchall()
            
            # Écriture dans le fichier CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # En-tête
                writer.writerow(['Intitulé du produit', 'Prix', 'Localisation', 'Origine', 'Type', 'Date de mise à jour'])
                
                # Données
                for row in rows:
                    writer.writerow([
                        row['intitule'], 
                        row['prix'], 
                        row['localisation'], 
                        row['origine'], 
                        row['type'],
                        row['date_mise_a_jour']
                    ])
            
            conn.close()
            return len(rows)
            
    def export_last_update_to_csv(self, output_file="derniere_maj_prix.csv"):
        """
        Exporte les informations de dernière mise à jour des prix vers un fichier CSV
        """
        results = self.get_last_price_update()
        
        # Écriture dans le fichier CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # En-tête
            writer.writerow(['ID Produit', 'Intitulé du produit', 'Dernière mise à jour', 'Prix Min', 'Prix Max'])
            
            # Données
            for row in results:
                writer.writerow([
                    row['id'], 
                    row['intitule'], 
                    row['derniere_mise_a_jour'], 
                    row['prix_min'], 
                    row['prix_max']
                ])
        
        return len(results)
        
    def get_last_price_update(self, product_id=None):
        """
        Récupère la dernière date de mise à jour des prix pour un produit spécifique
        ou pour tous les produits si aucun ID n'est spécifié
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if product_id:
            # Pour un produit spécifique
            cursor.execute("""
                SELECT 
                    p.id, 
                    p.intitule, 
                    MAX(pr.date_releve) as derniere_mise_a_jour, 
                    MIN(pr.prix) as prix_min,
                    MAX(pr.prix) as prix_max
                FROM 
                    produits p
                LEFT JOIN 
                    prix pr ON p.id = pr.id_produit
                WHERE 
                    p.id = ?
                GROUP BY
                    p.id, p.intitule
            """, (product_id,))
        else:
            # Pour tous les produits
            cursor.execute("""
                SELECT 
                    p.id, 
                    p.intitule, 
                    MAX(pr.date_releve) as derniere_mise_a_jour, 
                    MIN(pr.prix) as prix_min,
                    MAX(pr.prix) as prix_max
                FROM 
                    produits p
                LEFT JOIN 
                    prix pr ON p.id = pr.id_produit
                GROUP BY
                    p.id, p.intitule
                ORDER BY
                    derniere_mise_a_jour DESC
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
        
    def get_product_count(self):
        """
        Retourne le nombre de produits dans la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM produits")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_price_count(self):
        """
        Retourne le nombre d'entrées de prix dans la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM prix")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_commune_count(self):
        """
        Retourne le nombre de communes dans la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM communes")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_magasin_count(self):
        """
        Retourne le nombre de magasins dans la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM magasins")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def print_database_stats(self):
        """
        Affiche des statistiques sur la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Nombre de produits
        cursor.execute("SELECT COUNT(*) FROM produits")
        product_count = cursor.fetchone()[0]
        
        # Nombre de prix
        cursor.execute("SELECT COUNT(*) FROM prix")
        price_count = cursor.fetchone()[0]
        
        # Nombre de communes
        cursor.execute("SELECT COUNT(*) FROM communes")
        commune_count = cursor.fetchone()[0]
        
        # Nombre de magasins
        cursor.execute("SELECT COUNT(*) FROM magasins")
        magasin_count = cursor.fetchone()[0]
        
        # Origines des produits
        cursor.execute("SELECT origine, COUNT(*) FROM produits GROUP BY origine")
        origins = cursor.fetchall()
        
        # Secteurs de consommation
        cursor.execute("SELECT secteur, COUNT(*) FROM produits GROUP BY secteur")
        sectors = cursor.fetchall()
        
        # Dernière date de relevé
        cursor.execute("SELECT MAX(date_releve) as derniere_mise_a_jour FROM prix")
        last_update = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info("\n=== STATISTIQUES DE LA BASE DE DONNÉES ===")
        logger.info(f"Nombre total de produits: {product_count}")
        logger.info(f"Nombre total d'entrées de prix: {price_count}")
        logger.info(f"Nombre total de communes: {commune_count}")
        logger.info(f"Nombre total de magasins: {magasin_count}")
        logger.info(f"Dernière mise à jour des prix: {last_update}")
        
        logger.info("\nORIGINE DES PRODUITS:")
        for origin in origins:
            logger.info(f"  - {origin[0] or 'Non spécifié'}: {origin[1]} produits")
            
        logger.info("\nSECTEURS DE CONSOMMATION:")
        for sector in sectors:
            if sector[0]:  # Éviter les secteurs vides
                logger.info(f"  - {sector[0]}: {sector[1]} produits")
                
    def get_all_data(self, table_name):
        """
        Récupère toutes les données d'une table donnée
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Construction de la requête SQL en fonction du nom de la table
            if table_name == "produits":
                cursor.execute("SELECT id, intitule, origine, type, secteur, sous_secteur FROM produits ORDER BY intitule LIMIT 50")
            elif table_name == "prix":
                cursor.execute("SELECT id, id_produit, prix, magasin, commune, date_releve FROM prix ORDER BY date_releve DESC LIMIT 50")
            elif table_name == "communes":
                cursor.execute("SELECT id, nom, province FROM communes ORDER BY nom")
            elif table_name == "magasins":
                cursor.execute("SELECT id, label, commune, type_commerce FROM magasins ORDER BY label")
            elif table_name == "secteurs":
                cursor.execute("SELECT id, secteur_conso FROM secteurs ORDER BY secteur_conso")
            elif table_name == "sous_secteurs":
                cursor.execute("SELECT id, sous_secteur_conso FROM sous_secteurs ORDER BY sous_secteur_conso")
            elif table_name == "types_commerce":
                cursor.execute("SELECT id, type_commerce FROM types_commerce ORDER BY type_commerce")
            elif table_name == "marques":
                cursor.execute("SELECT id, marque FROM marques ORDER BY marque")
            elif table_name == "varietes":
                cursor.execute("SELECT id, variete FROM varietes ORDER BY variete")
            elif table_name == "boucliers":
                cursor.execute("SELECT id, titre FROM boucliers")
            else:
                logger.error(f"Table inconnue: {table_name}")
                return []
                
            return cursor.fetchall()
            
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des données de la table {table_name}: {str(e)}")
            return []
        finally:
            conn.close()
    
    def print_data(self, table_name):
        """
        Affiche les données d'une table donnée
        """
        data = self.get_all_data(table_name)
        
        if not data:
            logger.info(f"Aucune donnée trouvée dans la table {table_name}")
            return
        
        logger.info(f"\nContenu de la table {table_name} ({len(data)} entrées):")
        
        # Récupération des noms de colonnes
        column_names = data[0].keys()
        
        # Affichage formaté
        format_string = ""
        headers = []
        
        for column in column_names:
            headers.append(column)
            format_string += "{:<25}"
        
        logger.info(format_string.format(*headers))
        logger.info("-" * (25 * len(headers)))
        
        for row in data:
            values = [str(row[column]) for column in column_names]
            logger.info(format_string.format(*values))
        
        # Indiquer s'il y a plus de données
        if len(data) == 50:
            logger.info("... (utilisez l'export CSV pour voir toutes les données)")

def main():
    # Analyse des arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Gestion des données de Prix.nc")
    
    # Options générales
    parser.add_argument('-l', '--limit', type=int, help='Limite le nombre de produits à récupérer')
    parser.add_argument('-p', '--page-size', type=int, default=20, help='Nombre de produits par page (défaut: 20)')
    parser.add_argument('-s', '--start-page', type=int, default=0, help='Page de départ (défaut: 0)')
    parser.add_argument('-o', '--output', default='produits_prix_nc.csv', help='Nom du fichier CSV de sortie')
    parser.add_argument('-d', '--database', default='prix_nc.db', help='Nom de la base de données SQLite')
    parser.add_argument('--stats', action='store_true', help='Afficher les statistiques de la base de données')
    parser.add_argument('--export-only', action='store_true', help='Exporter uniquement les données existantes sans en récupérer de nouvelles')
    parser.add_argument('--print', action='store_true', help='Afficher les données récupérées')
    
    # Options pour les tables principales
    parser.add_argument('--communes', action='store_true', help='Récupérer la liste des communes')
    parser.add_argument('--magasins', action='store_true', help='Récupérer la liste des magasins')
    parser.add_argument('--produits', action='store_true', help='Récupérer la liste des produits (inclut automatiquement les prix)')
    parser.add_argument('--produits-sans-prix', action='store_true', help='Récupérer uniquement les produits sans leurs prix')
    parser.add_argument('--prix', action='store_true', help='Récupérer uniquement les prix (nécessite --product-id)')
    parser.add_argument('--all-except-products', action='store_true', help='Récupérer toutes les données annexes sauf les produits')

    # Options pour les tables de données annexes
    parser.add_argument('--annexes', action='store_true', help='Récupérer toutes les données annexes')
    parser.add_argument('--secteurs', action='store_true', help='Récupérer uniquement les secteurs de consommation')
    parser.add_argument('--sous-secteurs', action='store_true', help='Récupérer uniquement les sous-secteurs de consommation')
    parser.add_argument('--types-commerce', action='store_true', help='Récupérer uniquement les types de commerce')
    parser.add_argument('--marques', action='store_true', help='Récupérer uniquement les marques')
    parser.add_argument('--varietes', action='store_true', help='Récupérer uniquement les variétés')
    parser.add_argument('--boucliers', action='store_true', help='Récupérer uniquement les boucliers qualité prix')
    
    # Options de recherche
    parser.add_argument('--search', action='store_true', help='Activer le mode recherche')
    parser.add_argument('--nom', help='Rechercher par nom de produit')
    parser.add_argument('--origine', choices=['LOCAL', 'IMPORT', 'INCONNU', 'SERVICE'], help='Rechercher par origine du produit')
    parser.add_argument('--type-produit', help='Rechercher par type de produit')
    parser.add_argument('--secteur-search', help='Rechercher par secteur de consommation')
    parser.add_argument('--sous-secteur-search', help='Rechercher par sous-secteur de consommation')
    parser.add_argument('--prix-min', type=int, help='Prix minimum pour la recherche')
    parser.add_argument('--prix-max', type=int, help='Prix maximum pour la recherche')
    parser.add_argument('--commune-search', help='Rechercher par commune')
    parser.add_argument('--magasin-search', help='Rechercher par magasin')
    parser.add_argument('--search-output', default='search_results.csv', help='Nom du fichier CSV pour les résultats de recherche')
    parser.add_argument('--export-search', action='store_true', help='Exporter les résultats de recherche au format CSV standard')
    
    # Options pour les listes de valeurs
    parser.add_argument('--list-values', help='Afficher les valeurs distinctes pour un champ (par exemple: origine, secteur, sous_secteur, marque)')
    parser.add_argument('--list-table', default='produits', help='Table dans laquelle rechercher les valeurs distinctes')
    
    # Autres options
    parser.add_argument('--last-update', action='store_true', help='Exporter les dates de dernière mise à jour des prix')
    parser.add_argument('--product-id', help='ID du produit pour lequel récupérer les détails des prix')
    
    args = parser.parse_args()
    
    # Initialisation du gestionnaire
    manager = PrixNCManager(db_path=args.database)
    
    # Préparation des critères de recherche (si fournis)
    search_params = {}
    if args.nom or args.origine or args.type_produit or args.secteur_search or args.sous_secteur_search or \
       args.prix_min or args.prix_max or args.commune_search or args.magasin_search:
        search_params = {
            'nom': args.nom,
            'origine': args.origine,
            'type_produit': args.type_produit,
            'secteur': args.secteur_search,
            'sous_secteur': args.sous_secteur_search,
            'prix_min': args.prix_min,
            'prix_max': args.prix_max,
            'commune': args.commune_search,
            'magasin': args.magasin_search,
            'limit': args.limit,
        }
        # Suppression des paramètres None
        search_params = {k: v for k, v in search_params.items() if v is not None}
    
    # Affichage des valeurs distinctes pour un champ
    if args.list_values:
        values = manager.get_distinct_values(args.list_values, args.list_table)
        logger.info(f"\nValeurs distinctes pour {args.list_values} dans la table {args.list_table}:")
        for value in values:
            logger.info(f"  - {value}")
        return
    
    # Mode recherche
    if args.search:
        # Exécution de la recherche
        results = manager.search_products(**search_params)
        
        # Affichage du nombre de résultats
        logger.info(f"\nRecherche effectuée avec les critères: {search_params}")
        logger.info(f"Nombre de résultats: {len(results)}")
        
        # Affichage des premiers résultats
        if results:
            logger.info("\nPremiers résultats:")
            for i, result in enumerate(results[:5]):
                logger.info(f"\n{i+1}. {result['intitule']}")
                logger.info(f"   - Origine: {result['origine']}")
                logger.info(f"   - Prix: {result['prix_min']} - {result['prix_max']} XPF")
                logger.info(f"   - Communes: {result['communes']}")
        
        # Export des résultats au format de recherche
        if results:
            if args.export_search:
                # Export au format standard (même que pour --export-only)
                exported = manager.export_to_csv(args.output, **search_params)
                logger.info(f"\nRésultats exportés au format standard vers {args.output}")
            else:
                # Export au format de recherche
                exported = manager.export_search_results(results, args.search_output)
                logger.info(f"\nRésultats exportés au format de recherche vers {args.search_output}")
        
        return
    
    # Récupération de toutes les données sauf les produits
    if args.all_except_products:
        logger.info("Récupération de toutes les données annexes (sauf les produits)...")
        
        # Récupération des communes
        communes_count = manager.fetch_communes()
        logger.info(f"Nombre de communes récupérées: {communes_count}")
        
        # Récupération des magasins
        magasins_count = manager.fetch_magasins()
        logger.info(f"Nombre de magasins récupérés: {magasins_count}")
        
        # Récupération des données annexes
        annexes_count = manager.fetch_annexes()
        logger.info(f"Nombre de données annexes récupérées: {annexes_count}")
        
        logger.info("\nRécupération terminée avec succès!")
        
        # Afficher les statistiques
        manager.print_database_stats()
        return
    
    # Récupération des communes si demandé
    if args.communes:
        communes_count = manager.fetch_communes()
        logger.info(f"\nNombre de communes récupérées: {communes_count}")
        if args.print:
            manager.print_data("communes")
    
    # Récupération des magasins si demandé
    if args.magasins:
        magasins_count = manager.fetch_magasins()
        logger.info(f"\nNombre de magasins récupérés: {magasins_count}")
        if args.print:
            manager.print_data("magasins")
    
    # Récupération des données annexes
    if args.annexes:
        annexes_count = manager.fetch_annexes()
        logger.info(f"\nNombre de données annexes récupérées: {annexes_count}")
        if args.print:
            logger.info("\nContenu des tables annexes:")
            manager.print_data("secteurs")
            manager.print_data("sous_secteurs")
            manager.print_data("types_commerce")
            manager.print_data("marques")
            manager.print_data("varietes")
            manager.print_data("boucliers")
    
    # Récupération des données annexes individuelles
    if args.secteurs:
        secteurs_count = manager.fetch_secteurs()
        logger.info(f"\nNombre de secteurs récupérés: {secteurs_count}")
        if args.print:
            try:
                manager.print_data("secteurs")
            except Exception as e:
                logger.error(f"Erreur lors de l'affichage des secteurs: {str(e)}")
                # Afficher manuellement le contenu de la table secteurs
                conn = sqlite3.connect(manager.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT id, secteur_conso FROM secteurs ORDER BY secteur_conso")
                secteurs = cursor.fetchall()
                conn.close()
                
                if secteurs:
                    logger.info(f"\nContenu de la table secteurs ({len(secteurs)} entrées):")
                    logger.info("ID                                     Secteur")
                    logger.info("-" * 70)
                    for secteur in secteurs:
                        logger.info(f"{secteur[0]:<40} {secteur[1]}")
    
    if args.sous_secteurs:
        sous_secteurs_count = manager.fetch_sous_secteurs()
        logger.info(f"\nNombre de sous-secteurs récupérés: {sous_secteurs_count}")
        if args.print:
            manager.print_data("sous_secteurs")
    
    if args.types_commerce:
        types_commerce_count = manager.fetch_types_commerce()
        logger.info(f"\nNombre de types de commerce récupérés: {types_commerce_count}")
        if args.print:
            manager.print_data("types_commerce")
    
    if args.marques:
        marques_count = manager.fetch_marques()
        logger.info(f"\nNombre de marques récupérées: {marques_count}")
        if args.print:
            manager.print_data("marques")
    
    if args.varietes:
        varietes_count = manager.fetch_varietes()
        logger.info(f"\nNombre de variétés récupérées: {varietes_count}")
        if args.print:
            manager.print_data("varietes")
    
    if args.boucliers:
        boucliers_count = manager.fetch_boucliers()
        logger.info(f"\nNombre de boucliers qualité prix récupérés: {boucliers_count}")
        if args.print:
            manager.print_data("boucliers")
    
    # Affichage des statistiques si demandé
    if args.stats:
        manager.print_database_stats()
    
    # Récupération des produits et/ou des prix
    if args.produits:
        # Récupérer les produits avec leurs prix par défaut
        results = manager.fetch_products(limit=args.limit, page_size=args.page_size, start_page=args.start_page, fetch_prices=True)
        if isinstance(results, tuple):
            products_retrieved, prices_retrieved = results
            logger.info(f"\nNombre de produits récupérés: {products_retrieved}")
            logger.info(f"Nombre de prix récupérés: {prices_retrieved}")
            
            if args.print:
                manager.print_data("produits")
                if prices_retrieved > 0:
                    manager.print_data("prix")
        else:
            logger.info(f"\nNombre de produits récupérés: {results}")
            
            if args.print:
                manager.print_data("produits")
    elif args.produits_sans_prix:
        # Récupérer uniquement les produits sans leurs prix
        products_retrieved = manager.fetch_products(limit=args.limit, page_size=args.page_size, start_page=args.start_page, fetch_prices=False)
        logger.info(f"\nNombre de produits récupérés (sans prix): {products_retrieved}")
        
        if args.print:
            manager.print_data("produits")
    # Récupération des prix pour un produit spécifique
    elif args.prix and args.product_id:
        prices_count = manager.fetch_product_prices(args.product_id)
        logger.info(f"\nNombre de relevés de prix récupérés pour le produit {args.product_id}: {prices_count}")
        
        if args.print:
            conn = sqlite3.connect(manager.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prix WHERE id_produit = ? ORDER BY date_releve DESC", (args.product_id,))
            prices = cursor.fetchall()
            conn.close()
            
            if prices:
                logger.info(f"\nPrix pour le produit {args.product_id} ({len(prices)} entrées):")
                
                # Récupération des noms de colonnes
                column_names = prices[0].keys()
                
                # Affichage formaté
                format_string = ""
                headers = []
                
                for column in column_names:
                    headers.append(column)
                    format_string += "{:<15}"
                
                logger.info(format_string.format(*headers))
                logger.info("-" * (15 * len(headers)))
                
                for row in prices[:50]:
                    values = [str(row[column]) for column in column_names]
                    logger.info(format_string.format(*values))
                
                if len(prices) > 50:
                    logger.info(f"... et {len(prices) - 50} autres entrées")
            else:
                logger.info(f"Aucun prix trouvé pour le produit {args.product_id}")
{{ ... }}

if __name__ == "__main__":
    main()
