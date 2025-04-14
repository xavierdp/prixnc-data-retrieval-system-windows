#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour afficher le contenu des tables de la base de données Prix.nc
"""

import sqlite3
import argparse
import sys

def print_table(db_path, table_name, limit=50):
    """
    Affiche le contenu d'une table de la base de données
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Récupération des noms de colonnes
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Récupération des données
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"Aucune donnée trouvée dans la table {table_name}")
            return
        
        # Affichage formaté
        print(f"\nContenu de la table {table_name} ({len(rows)} entrées):")
        
        # Calcul de la largeur des colonnes
        col_widths = [max(len(str(col)), 15) for col in column_names]
        for row in rows:
            for i, col in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(col)) if col else 4)
        
        # Affichage des en-têtes
        header = ""
        for i, col in enumerate(column_names):
            header += f"{col:<{col_widths[i]}} "
        print(header)
        
        # Ligne de séparation
        separator = ""
        for width in col_widths:
            separator += "-" * width + " "
        print(separator)
        
        # Affichage des données
        for row in rows:
            line = ""
            for i, col in enumerate(row):
                line += f"{str(col):<{col_widths[i]}} "
            print(line)
        
    except sqlite3.Error as e:
        print(f"Erreur lors de l'affichage de la table {table_name}: {e}")
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Affichage du contenu des tables de la base de données Prix.nc")
    parser.add_argument("table", help="Nom de la table à afficher")
    parser.add_argument("-d", "--database", default="prix_nc.db", help="Chemin vers la base de données")
    parser.add_argument("-l", "--limit", type=int, default=50, help="Nombre maximum de lignes à afficher")
    
    args = parser.parse_args()
    
    print_table(args.database, args.table, args.limit)

if __name__ == "__main__":
    main()
