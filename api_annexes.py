# -*- coding: utf-8 -*-

"""
Module contenant les fonctions pour récupérer les données annexes de l'API Prix.nc
"""

import sqlite3
import requests
import json

class APIAnnexes:
    """
    Classe pour récupérer les données annexes de l'API Prix.nc
    """
    
    def __init__(self, base_url="https://prix.nc/api/v1", db_path="prix_nc.db"):
        """
        Initialisation de la classe
        """
        self.base_url = base_url
        self.db_path = db_path
    
    def fetch_secteurs(self):
        """
        Récupère les secteurs de consommation
        """
        try:
            url = f"{self.base_url}/secteurs"
            print("Récupération des secteurs de consommation...")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "secteurs" in data["_embedded"]:
                    secteurs = data["_embedded"]["secteurs"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for secteur in secteurs:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO secteurs 
                            (id, id_neolan, secteur_conso, date_mise_a_jour)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                secteur["id"],
                                secteur.get("idNeolan", None),
                                secteur.get("secteurConso", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"{len(secteurs)} secteurs récupérés et enregistrés")
                    return len(secteurs)
                else:
                    print("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                print(f"Erreur lors de la récupération des secteurs: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Erreur lors de la récupération des secteurs: {str(e)}")
            return 0
    
    def fetch_sous_secteurs(self):
        """
        Récupère les sous-secteurs de consommation
        """
        try:
            url = f"{self.base_url}/ss-secteurs"
            print("Récupération des sous-secteurs de consommation...")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "ss_secteurs" in data["_embedded"]:
                    sous_secteurs = data["_embedded"]["ss_secteurs"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for sous_secteur in sous_secteurs:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO sous_secteurs 
                            (id, id_neolan, id_neolan_secteur_conso, sous_secteur_conso, date_mise_a_jour)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                sous_secteur["id"],
                                sous_secteur.get("idNeolan", None),
                                sous_secteur.get("idNeolanSecteurConso", None),
                                sous_secteur.get("sousSecteurConso", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"{len(sous_secteurs)} sous-secteurs récupérés et enregistrés")
                    return len(sous_secteurs)
                else:
                    print("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                print(f"Erreur lors de la récupération des sous-secteurs: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Erreur lors de la récupération des sous-secteurs: {str(e)}")
            return 0
    
    def fetch_types_commerce(self):
        """
        Récupère les types de commerce
        """
        try:
            url = f"{self.base_url}/typesCommerce"
            print("Récupération des types de commerce...")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "typesCommerce" in data["_embedded"]:
                    types_commerce = data["_embedded"]["typesCommerce"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for type_commerce in types_commerce:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO types_commerce 
                            (id, id_neolan, type_commerce, date_mise_a_jour)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                type_commerce["id"],
                                type_commerce.get("idNeolan", None),
                                type_commerce.get("typeCommerce", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"{len(types_commerce)} types de commerce récupérés et enregistrés")
                    return len(types_commerce)
                else:
                    print("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                print(f"Erreur lors de la récupération des types de commerce: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Erreur lors de la récupération des types de commerce: {str(e)}")
            return 0
    
    def fetch_marques(self):
        """
        Récupère les marques
        """
        try:
            url = f"{self.base_url}/marques"
            print("Récupération des marques...")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "marques" in data["_embedded"]:
                    marques = data["_embedded"]["marques"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for marque in marques:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO marques 
                            (id, id_neolan, marque, date_mise_a_jour)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                marque["id"],
                                marque.get("idNeolan", None),
                                marque.get("marque", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"{len(marques)} marques récupérées et enregistrées")
                    return len(marques)
                else:
                    print("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                print(f"Erreur lors de la récupération des marques: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Erreur lors de la récupération des marques: {str(e)}")
            return 0
    
    def fetch_varietes(self):
        """
        Récupère les variétés
        """
        try:
            url = f"{self.base_url}/varietes"
            print("Récupération des variétés...")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "varietes" in data["_embedded"]:
                    varietes = data["_embedded"]["varietes"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for variete in varietes:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO varietes 
                            (id, id_neolan, variete, date_mise_a_jour)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                variete["id"],
                                variete.get("idNeolan", None),
                                variete.get("variete", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"{len(varietes)} variétés récupérées et enregistrées")
                    return len(varietes)
                else:
                    print("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                print(f"Erreur lors de la récupération des variétés: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Erreur lors de la récupération des variétés: {str(e)}")
            return 0
    
    def fetch_boucliers(self):
        """
        Récupère les boucliers qualité prix
        """
        try:
            url = f"{self.base_url}/boucliers"
            print("Récupération des boucliers qualité prix...")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if "_embedded" in data and "boucliers" in data["_embedded"]:
                    boucliers = data["_embedded"]["boucliers"]
                    
                    # Connexion à la base de données
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for bouclier in boucliers:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO boucliers 
                            (id, titre, contenu, image, date_mise_a_jour)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                            (
                                bouclier["id"],
                                bouclier.get("titre", ""),
                                bouclier.get("contenu", ""),
                                bouclier.get("image", "")
                            )
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"{len(boucliers)} boucliers qualité prix récupérés et enregistrés")
                    return len(boucliers)
                else:
                    print("Structure de données inattendue dans la réponse de l'API")
                    return 0
            else:
                print(f"Erreur lors de la récupération des boucliers qualité prix: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Erreur lors de la récupération des boucliers qualité prix: {str(e)}")
            return 0

    def fetch_all_annexes(self):
        """
        Récupère toutes les données annexes
        """
        secteurs_count = self.fetch_secteurs()
        sous_secteurs_count = self.fetch_sous_secteurs()
        types_commerce_count = self.fetch_types_commerce()
        marques_count = self.fetch_marques()
        varietes_count = self.fetch_varietes()
        boucliers_count = self.fetch_boucliers()
        
        return {
            "secteurs": secteurs_count,
            "sous_secteurs": sous_secteurs_count,
            "types_commerce": types_commerce_count,
            "marques": marques_count,
            "varietes": varietes_count,
            "boucliers": boucliers_count
        }
