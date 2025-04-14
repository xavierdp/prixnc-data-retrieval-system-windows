#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os

def setup_database(db_path="prix_nc.db"):
    """
    Configure la base de données avec les tables nécessaires
    """
    try:
        # Connexion à la base de données (créera le fichier s'il n'existe pas)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Table de configuration pour stocker les paramètres globaux
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            cle TEXT PRIMARY KEY,
            valeur TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Création des tables si elles n'existent pas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id TEXT PRIMARY KEY,
            intitule TEXT NOT NULL,
            origine TEXT,
            type TEXT,
            id_secteur TEXT,
            secteur TEXT,
            id_sous_secteur TEXT,
            sous_secteur TEXT,
            id_marque TEXT,
            marque TEXT,
            variete TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des prix
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prix (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produit TEXT NOT NULL,
            prix INTEGER,
            prix_par_unite INTEGER,
            unite_label TEXT,
            unite_label_court TEXT,
            promotion BOOLEAN,
            date_releve DATE,
            id_magasin TEXT,
            magasin TEXT,
            id_commune TEXT,
            commune TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_produit) REFERENCES produits(id)
        )
        ''')
        
        # Ajout de la table communes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS communes (
            id TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            province TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Ajout de la table magasins
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS magasins (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            id_commune TEXT,
            commune TEXT,
            province TEXT,
            zone_geo TEXT,
            longitude REAL,
            latitude REAL,
            id_type_commerce TEXT,
            type_commerce TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_commune) REFERENCES communes(id)
        )
        ''')
        
        # Table des secteurs de consommation
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS secteurs (
            id TEXT PRIMARY KEY,
            id_neolan INTEGER,
            secteur_conso TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des sous-secteurs de consommation
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sous_secteurs (
            id TEXT PRIMARY KEY,
            id_neolan INTEGER,
            id_neolan_secteur_conso INTEGER,
            sous_secteur_conso TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des types de commerce
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS types_commerce (
            id TEXT PRIMARY KEY,
            id_neolan INTEGER,
            type_commerce TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des marques
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS marques (
            id TEXT PRIMARY KEY,
            id_neolan INTEGER,
            marque TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des variétés
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS varietes (
            id TEXT PRIMARY KEY,
            id_neolan INTEGER,
            variete TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des boucliers qualité prix
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS boucliers (
            id TEXT PRIMARY KEY,
            titre TEXT,
            contenu TEXT,
            image TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_mise_a_jour TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Création des index pour améliorer les performances
        print("Création des index pour optimiser les performances...")
        
        # Index pour la table produits
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_origine ON produits(origine)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_secteur ON produits(secteur)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_sous_secteur ON produits(sous_secteur)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_intitule ON produits(intitule)')
        
        # Index pour la table prix
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prix_id_produit ON prix(id_produit)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prix_commune ON prix(commune)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prix_magasin ON prix(magasin)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prix_date_releve ON prix(date_releve)')
        
        # Index pour les tables de référence
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_magasins_commune ON magasins(commune)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_magasins_type_commerce ON magasins(type_commerce)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sous_secteurs_id_secteur ON sous_secteurs(id_neolan_secteur_conso)')
        
        # Validation et fermeture
        conn.commit()
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Erreur lors de la création de la base de données : {e}")
        
if __name__ == "__main__":
    setup_database()
