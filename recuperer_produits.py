#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script simplifié pour récupérer tous les produits de l'API Prix.nc
"""

import sqlite3
import requests
import os
import time
import random
import logging
from datetime import datetime
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prix_nc_api.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("prix_nc_api")

class APILimitExceeded(Exception):
    """Exception pour indiquer que la limite de l'API a été dépassée"""
    pass

def create_connection(db_path="prix_nc.db"):
    """
    Crée une connexion à la base de données SQLite
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"Connexion à la base de données {db_path} établie avec succès.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        return None

def make_api_request(url, max_retries=5, base_delay=2):
    """
    Effectue une requête à l'API avec une gestion robuste des erreurs et backoff exponentiel
    """
    headers = {
        "Accept": "application/json",
        "User-Agent": "PrixNC-DataRetriever/1.0"
    }
    
    for retry in range(max_retries):
        try:
            # Ajouter un délai aléatoire pour éviter les requêtes synchronisées
            if retry > 0:
                delay = base_delay * (2 ** retry) + random.uniform(0, 1)
                logger.info(f"Attente de {delay:.2f} secondes avant la tentative {retry+1}/{max_retries}...")
                time.sleep(delay)
            
            response = requests.get(url, headers=headers, timeout=30)
            
            # Gestion des codes d'erreur
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Too Many Requests
                retry_after = response.headers.get('Retry-After', base_delay * (2 ** retry))
                logger.warning(f"Limite d'API atteinte (429). Attente de {retry_after} secondes...")
                time.sleep(float(retry_after))
                continue
            elif response.status_code >= 500:  # Erreurs serveur
                logger.warning(f"Erreur serveur: {response.status_code}. Nouvelle tentative...")
                continue
            else:
                logger.error(f"Erreur {response.status_code}: {response.text}")
                return response  # Retourne la réponse même avec erreur pour traitement extérieur
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout lors de la requête. Tentative {retry+1}/{max_retries}...")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Erreur de connexion. Tentative {retry+1}/{max_retries}...")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            if retry == max_retries - 1:
                raise
    
    # Si on arrive ici, c'est que toutes les tentatives ont échoué
    raise APILimitExceeded("Limite d'API atteinte après plusieurs tentatives")

def progressive_fetch_products(base_url="https://prix.nc/api/v1", db_path="prix_nc.db", limit=None, page_size=10, initial_delay=1, max_delay=5, start_page=0):
    """
    Récupère les produits avec une stratégie progressive pour respecter les limites d'API
    """
    conn = create_connection(db_path)
    if not conn:
        return
    
    cursor = conn.cursor()
    
    current_page = start_page
    products_retrieved = 0
    total_prices = 0
    current_delay = initial_delay
    
    logger.info(f"Début de la récupération des produits (limite: {limit if limit else 'illimitée'}, page de départ: {start_page})...")
    
    try:
        while True:
            try:
                url = f"{base_url}/produitsprix?page={current_page}&size={page_size}"
                logger.info(f"Récupération de la page {current_page}...")
                
                # Requête avec gestion des limites d'API
                response = make_api_request(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "_embedded" in data and "produitsprix" in data["_embedded"]:
                        products = data["_embedded"]["produitsprix"]
                        
                        if not products:
                            logger.info("Plus de produits à récupérer")
                            break
                        
                        # Sauvegarde dans la base de données
                        for product in products:
                            # Insertion dans la table produits
                            cursor.execute(
                                """
                                INSERT OR IGNORE INTO produits 
                                (id, intitule, origine, type, id_secteur, secteur, id_sous_secteur, sous_secteur, date_creation)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                                """,
                                (
                                    product.get("id", ""),
                                    product.get("nom", ""),
                                    product.get("origine", ""),
                                    product.get("type", ""),
                                    product.get("idSecteur", ""),
                                    product.get("secteur", ""),
                                    product.get("idSousSecteur", ""),
                                    product.get("sousSecteur", "")
                                )
                            )
                            
                            # Mise à jour si le produit existe déjà
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
                                    product.get("type", ""),
                                    product.get("idSecteur", ""),
                                    product.get("secteur", ""),
                                    product.get("idSousSecteur", ""),
                                    product.get("sousSecteur", ""),
                                    product.get("id", "")
                                )
                            )
                        
                        conn.commit()
                        products_retrieved += len(products)
                        logger.info(f"Page {current_page}: {len(products)} produits récupérés")
                        
                        # Récupération progressive des prix pour chaque produit
                        prices_fetched_for_page = 0
                        for product in products:
                            product_id = product.get("id")
                            if not product_id:
                                continue
                            
                            # Attente entre chaque requête de prix
                            time.sleep(current_delay)
                            
                            # Utiliser l'endpoint correct pour les prix
                            url_prices = f"{base_url}/relevesprix?idProduit={product_id}"
                            logger.info(f"Récupération des prix pour le produit {product_id}...")
                            
                            try:
                                response_prices = make_api_request(url_prices)
                                
                                if response_prices.status_code == 200:
                                    data_prices = response_prices.json()
                                    
                                    if "_embedded" in data_prices and "relevesprix" in data_prices["_embedded"]:
                                        prices = data_prices["_embedded"]["relevesprix"]
                                        
                                        if prices:
                                            for price in prices:
                                                # Utiliser l'ID de produit fourni dans le prix et non celui de la requête
                                                prix_product_id = price.get("idProduit")
                                                
                                                # Ne pas insérer si l'ID de produit est absent
                                                if not prix_product_id:
                                                    continue
                                                
                                                # Vérifier si le produit existe déjà
                                                cursor.execute("SELECT 1 FROM produits WHERE id = ?", (prix_product_id,))
                                                if not cursor.fetchone():
                                                    # Si le produit n'existe pas, l'ajouter à la base de données
                                                    cursor.execute(
                                                        """
                                                        INSERT OR IGNORE INTO produits 
                                                        (id, intitule, origine, date_creation)
                                                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                                                        """,
                                                        (
                                                            prix_product_id,
                                                            price.get("nom", ""),
                                                            price.get("origine", "")
                                                        )
                                                    )
                                                    
                                                # Insérer le prix
                                                cursor.execute(
                                                    """
                                                    INSERT INTO prix
                                                    (id_produit, prix, prix_par_unite, unite_label, unite_label_court, promotion, date_releve, id_magasin, magasin, id_commune, commune)
                                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                                    """,
                                                    (
                                                        prix_product_id,  # Utiliser l'ID du produit dans le prix
                                                        price.get("prix"),
                                                        price.get("prixParUnite"),
                                                        price.get("uniteLabel"),
                                                        price.get("uniteLabelCourt"),
                                                        price.get("promotion", 0),
                                                        price.get("dateReleve"),
                                                        price.get("idMagasin"),
                                                        price.get("magasin"),
                                                        price.get("idCommune"),
                                                        price.get("commune")
                                                    )
                                                )
                                            conn.commit()
                                            logger.info(f"{len(prices)} prix récupérés pour le produit {product_id}")
                                            prices_fetched_for_page += len(prices)
                                            total_prices += len(prices)
                                            
                                            # Stratégie adaptative: si tout se passe bien, réduire un peu le délai
                                            current_delay = max(initial_delay, current_delay * 0.9)
                                        else:
                                            logger.info(f"Aucun prix trouvé pour le produit {product_id}")
                                    else:
                                        logger.info(f"Aucun prix trouvé pour le produit {product_id}")
                                else:
                                    logger.error(f"Erreur lors de la récupération des prix pour le produit {product_id}: {response_prices.status_code}")
                                    # Augmenter le délai en cas d'erreur
                                    current_delay = min(max_delay, current_delay * 1.5)
                            except APILimitExceeded:
                                logger.warning("Limite d'API atteinte pour les prix. Passage au produit suivant.")
                                # Augmenter considérablement le délai en cas de limite atteinte
                                current_delay = min(max_delay, current_delay * 2)
                                continue
                            except Exception as e:
                                logger.error(f"Erreur inattendue lors de la récupération des prix pour {product_id}: {str(e)}")
                                continue
                        
                        logger.info(f"Page {current_page}: {prices_fetched_for_page} prix récupérés")
                        
                        # Vérification si nous avons atteint la limite
                        if limit is not None and products_retrieved >= limit:
                            logger.info(f"Limite de {limit} produits atteinte")
                            break
                        
                        # Passage à la page suivante
                        if "page" in data:
                            current_page += 1
                            total_pages = data["page"].get("totalPages", 0)
                            total_elements = data["page"].get("totalElements", 0)
                            
                            if current_page >= total_pages:
                                logger.info(f"Toutes les pages ont été traitées ({total_pages} pages)")
                                break
                            
                            logger.info(f"Progression: {products_retrieved}/{total_elements} produits ({current_page}/{total_pages} pages)")
                        else:
                            current_page += 1
                    else:
                        logger.error("Structure de données inattendue dans la réponse de l'API")
                        break
                else:
                    logger.error(f"Erreur lors de la récupération des produits: {response.status_code}")
                    break
            
            except APILimitExceeded:
                logger.warning("Limite d'API atteinte. Attente prolongée avant de continuer...")
                time.sleep(60)  # Attente d'une minute avant de réessayer
                current_delay = max_delay  # Réinitialiser au délai maximum
                continue
            except Exception as e:
                logger.error(f"Erreur inattendue dans la boucle principale: {str(e)}")
                break
            
            # Attente entre les pages
            time.sleep(current_delay)
    
    except KeyboardInterrupt:
        logger.info("Interruption utilisateur détectée. Sauvegarde des données en cours...")
    finally:
        conn.commit()
        conn.close()
    
    logger.info(f"\nRécapitulatif:")
    logger.info(f"Nombre total de produits récupérés: {products_retrieved}")
    logger.info(f"Nombre total de prix récupérés: {total_prices}")
    
    return products_retrieved, total_prices

def reset_tables(db_path):
    """
    Réinitialise les tables produits et prix
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        logger.warning("Réinitialisation des tables produits et prix...")
        
        # Sauvegarde du nombre d'entrées avant suppression
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM produits")
        products_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prix")
        prices_count = cursor.fetchone()[0]
        
        # Désactiver les contraintes de clé étrangère pendant la suppression
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Suppression des données (en commençant par les prix qui référencent les produits)
        cursor.execute("DELETE FROM prix")
        cursor.execute("DELETE FROM produits")
        
        # Réactiver les contraintes de clé étrangère
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Valider la transaction
        conn.commit()
        
        # Fermer et rouvrir la connexion pour VACUUM
        conn.close()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        conn.commit()
        
        logger.warning(f"Tables réinitialisées : {products_count} produits et {prices_count} prix supprimés")
        
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la réinitialisation des tables : {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def verify_pagination(db_path, page_size, reported_products):
    """
    Vérifie si le nombre de produits est cohérent avec la taille de page
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérification du nombre de produits
        cursor.execute("SELECT COUNT(*) FROM produits")
        actual_products = cursor.fetchone()[0]
        
        # Calcul du nombre de pages théorique
        theoretical_pages = reported_products // page_size
        if reported_products % page_size > 0:
            theoretical_pages += 1
        
        # Affichage des statistiques
        logger.info("=== Vérification de la pagination ===")
        logger.info(f"Taille de page configurée : {page_size}")
        logger.info(f"Nombre de produits rapportés par le script : {reported_products}")
        logger.info(f"Nombre de produits dans la base de données : {actual_products}")
        
        if reported_products == actual_products:
            logger.info("✓ Le nombre de produits est cohérent")
        else:
            logger.warning(f"✗ Incohérence : différence de {actual_products - reported_products} produits")
        
        # Vérification de la complétude des pages
        if reported_products % page_size == 0:
            logger.info(f"✓ Le nombre de produits ({reported_products}) est un multiple exact de la taille de page ({page_size})")
        else:
            remaining = reported_products % page_size
            logger.info(f"ℹ La dernière page contient {remaining} produits sur {page_size} possibles")
        
        conn.close()
        
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la vérification de pagination : {e}")
    
    return

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Récupération des produits de l'API Prix.nc")
    parser.add_argument("-l", "--limit", type=int, help="Limite le nombre de produits à récupérer")
    parser.add_argument("-p", "--page-size", type=int, default=10, help="Nombre d'éléments par page (défaut: 10)")
    parser.add_argument("-d", "--database", default="prix_nc.db", help="Chemin vers la base de données")
    parser.add_argument("--initial-delay", type=float, default=1.0, help="Délai initial entre les requêtes en secondes (défaut: 1.0)")
    parser.add_argument("--max-delay", type=float, default=10.0, help="Délai maximum entre les requêtes en secondes (défaut: 10.0)")
    parser.add_argument("--reset", action="store_true", help="Réinitialiser les tables produits et prix avant de récupérer les données")
    parser.add_argument("--verify", action="store_true", help="Vérifier et afficher les statistiques de pagination à la fin")
    parser.add_argument("--start-page", type=int, default=0, help="Page de départ pour la récupération des produits")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_tables(args.database)
    
    products, prices = progressive_fetch_products(
        db_path=args.database, 
        limit=args.limit, 
        page_size=args.page_size,
        initial_delay=args.initial_delay,
        max_delay=args.max_delay,
        start_page=args.start_page
    )
    
    if args.verify:
        verify_pagination(args.database, args.page_size, products)

if __name__ == "__main__":
    main()
