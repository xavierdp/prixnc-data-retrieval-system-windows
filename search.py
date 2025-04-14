# -*- coding: utf-8 -*-

"""
Module pour la recherche de produits dans la base de données SQLite
"""

import sqlite3
import csv

class ProduitSearch:
    """
    Classe pour effectuer des recherches de produits selon différents critères
    """
    
    def __init__(self, db_path="prix_nc.db"):
        """
        Initialisation avec le chemin de la base de données
        """
        self.db_path = db_path
    
    def search_products(self, nom=None, origine=None, type_produit=None, 
                        secteur=None, sous_secteur=None, prix_min=None, prix_max=None, 
                        commune=None, magasin=None, limit=100):
        """
        Recherche des produits selon différents critères
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Construction de la requête SQL de base
        query = """
        SELECT 
            p.id,
            p.intitule,
            p.origine,
            p.type,
            p.secteur,
            p.sous_secteur,
            MIN(prix.prix) as prix_min,
            MAX(prix.prix) as prix_max,
            GROUP_CONCAT(DISTINCT prix.commune) as communes,
            GROUP_CONCAT(DISTINCT prix.magasin) as magasins
        FROM 
            produits p
        LEFT JOIN 
            prix ON p.id = prix.id_produit
        WHERE 1=1
        """
        
        # Liste pour stocker les paramètres de la requête
        params = []
        
        # Ajout des conditions selon les critères fournis
        if nom:
            query += " AND p.intitule LIKE ?"
            params.append(f"%{nom}%")
        
        if origine:
            query += " AND p.origine = ?"
            params.append(origine)
        
        if type_produit:
            query += " AND p.type = ?"
            params.append(type_produit)
        
        if secteur:
            query += " AND p.secteur LIKE ?"
            params.append(f"%{secteur}%")
        
        if sous_secteur:
            query += " AND p.sous_secteur LIKE ?"
            params.append(f"%{sous_secteur}%")
        
        if commune:
            query += " AND prix.commune LIKE ?"
            params.append(f"%{commune}%")
        
        if magasin:
            query += " AND prix.magasin LIKE ?"
            params.append(f"%{magasin}%")
        
        # Groupement et filtres sur les prix
        query += " GROUP BY p.id, p.intitule"
        
        if prix_min is not None or prix_max is not None:
            if prix_min is not None and prix_max is not None:
                query += " HAVING MIN(prix.prix) >= ? AND MAX(prix.prix) <= ?"
                params.append(prix_min)
                params.append(prix_max)
            elif prix_min is not None:
                query += " HAVING MIN(prix.prix) >= ?"
                params.append(prix_min)
            elif prix_max is not None:
                query += " HAVING MAX(prix.prix) <= ?"
                params.append(prix_max)
        
        # Tri et limite
        query += " ORDER BY p.intitule"
        
        if limit:
            query += f" LIMIT {limit}"
        
        # Exécution de la requête
        try:
            cursor.execute(query, params)
            
            # Récupération des résultats
            results = cursor.fetchall()
            
            # Conversion en dictionnaires
            results_list = [dict(row) for row in results]
            
            conn.close()
            
            return results_list
        except Exception as e:
            print(f"Erreur lors de la recherche: {str(e)}")
            conn.close()
            return []
    
    def export_search_results_to_csv(self, results, output_file="search_results.csv"):
        """
        Exporte les résultats de recherche vers un fichier CSV
        """
        if not results:
            print("Aucun résultat à exporter")
            return 0
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Utilisation des clés du premier résultat comme en-têtes de colonnes
            fieldnames = results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        
        return len(results)
    
    def get_distinct_values(self, field, table="produits"):
        """
        Récupère toutes les valeurs distinctes pour un champ donné
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = f"SELECT DISTINCT {field} FROM {table} WHERE {field} IS NOT NULL AND {field} != '' ORDER BY {field}"
            
            cursor.execute(query)
            
            results = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return results
        except Exception as e:
            print(f"Erreur lors de la récupération des valeurs distinctes: {str(e)}")
            conn.close()
            return []
