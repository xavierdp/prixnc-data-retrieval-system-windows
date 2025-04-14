#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Visualiseur en mode simple pour le système de récupération de données Prix.nc
Affiche les statistiques de la base de données et suit la progression de la récupération
"""

import sqlite3
import time
import os
import sys
import argparse
from datetime import datetime

# Codes de couleur ANSI
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Couleurs de texte
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Couleurs de texte brillantes
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Couleurs de fond
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

def create_connection(db_path="prix_nc.db"):
    """
    Crée une connexion à la base de données SQLite
    """
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"{Colors.RED}Erreur lors de la connexion à la base de données: {e}{Colors.RESET}")
        return None

def get_database_stats(conn):
    """
    Récupère les statistiques de la base de données
    """
    stats = {}
    cursor = conn.cursor()
    
    # Horodatage de la requête pour des calculs précis
    stats['timestamp'] = time.time()
    
    # Nombre de produits
    cursor.execute("SELECT COUNT(*) FROM produits")
    stats['total_produits'] = cursor.fetchone()[0]
    
    # Nombre de prix
    cursor.execute("SELECT COUNT(*) FROM prix")
    stats['total_prix'] = cursor.fetchone()[0]
    
    # Produits avec des prix
    cursor.execute("""
        SELECT COUNT(DISTINCT id_produit) 
        FROM prix
    """)
    stats['produits_avec_prix'] = cursor.fetchone()[0]
    
    # Pourcentage de produits avec prix
    if stats['total_produits'] > 0:
        stats['pourcentage_avec_prix'] = (stats['produits_avec_prix'] / stats['total_produits']) * 100
    else:
        stats['pourcentage_avec_prix'] = 0
    
    # Dernière mise à jour de produit
    cursor.execute("""
        SELECT date_mise_a_jour 
        FROM produits 
        ORDER BY date_mise_a_jour DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    stats['derniere_maj_produit'] = result[0] if result else "Aucune"
    
    # Nombre moyen de prix par produit (pour ceux qui ont des prix)
    if stats['produits_avec_prix'] > 0:
        cursor.execute("""
            SELECT AVG(prix_count) FROM (
                SELECT id_produit, COUNT(*) as prix_count
                FROM prix
                GROUP BY id_produit
            )
        """)
        stats['moyenne_prix_par_produit'] = cursor.fetchone()[0]
    else:
        stats['moyenne_prix_par_produit'] = 0
    
    # Distribution par secteur (top 5)
    cursor.execute("""
        SELECT secteur, COUNT(*) as count
        FROM produits
        GROUP BY secteur
        ORDER BY count DESC
        LIMIT 5
    """)
    stats['distribution_secteurs'] = cursor.fetchall()
    
    return stats

def get_log_activity(log_path="prix_nc_api.log", lines=5):
    """
    Récupère les dernières lignes du fichier de log
    """
    if not os.path.exists(log_path):
        return ["Fichier de log non trouvé"]
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines_list = f.readlines()
            return lines_list[-lines:]
    except Exception as e:
        return [f"Erreur lors de la lecture du fichier de log: {e}"]

def get_recent_product_ids(conn, limit=5):
    """
    Récupère les IDs des produits récemment ajoutés/mis à jour
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, intitule, date_mise_a_jour
        FROM produits
        ORDER BY date_mise_a_jour DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()

def get_products_without_prices(conn, limit=5):
    """
    Récupère les produits qui n'ont pas de prix associés
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.intitule, p.secteur, p.date_creation
        FROM produits p
        LEFT JOIN prix pr ON p.id = pr.id_produit
        WHERE pr.id_produit IS NULL
        ORDER BY p.date_creation DESC
        LIMIT ?
    """, (limit,))
    
    return cursor.fetchall()

def get_recent_prices(conn, limit=5):
    """
    Récupère les prix les plus récemment ajoutés avec groupement par produit
    """
    cursor = conn.cursor()
    
    # Cette requête va récupérer les derniers prix pour des produits différents
    cursor.execute("""
        WITH ranked_prices AS (
            SELECT 
                p.id as product_id,
                p.intitule, 
                pr.prix, 
                pr.magasin, 
                pr.date_creation,
                ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY pr.date_creation DESC) as rn
            FROM prix pr
            JOIN produits p ON pr.id_produit = p.id
        )
        SELECT intitule, prix, magasin, date_creation
        FROM ranked_prices
        WHERE rn = 1
        ORDER BY date_creation DESC
        LIMIT ?
    """, (limit,))
    
    return cursor.fetchall()

def format_duration(seconds):
    """
    Formate une durée en secondes en format lisible
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def display_stats(db_path="prix_nc.db", refresh_rate=2):
    """
    Affiche les statistiques en temps réel en mode simple
    """
    print("\033c", end="")  # Efface l'écran
    
    # Schéma de couleurs cohérent
    # Interface: Bleu
    header_bg = Colors.BG_BLUE
    header_fg = Colors.WHITE
    
    # Données primaires: Cyan
    primary_label = Colors.CYAN
    primary_value = Colors.BRIGHT_WHITE
    
    # Données secondaires: Bleu clair
    secondary_label = Colors.BLUE
    secondary_value = Colors.WHITE
    
    # Accents: Orange (simulé avec du jaune)
    accent = Colors.BRIGHT_YELLOW
    
    # Warnings: Jaune
    warning = Colors.YELLOW
    
    # Erreurs: Rouge
    error = Colors.RED
    
    # Succès: Vert
    success = Colors.GREEN
    
    # Initialisation
    conn = create_connection(db_path)
    
    if not conn:
        print(f"{error}Erreur: Impossible de se connecter à la base de données {db_path}{Colors.RESET}")
        return
    
    # Variables pour suivre les changements entre les mises à jour
    prev_stats = get_database_stats(conn)
    start_time = time.time()
    last_update_time = start_time
    
    # Taux d'extraction (par minute)
    produits_rate = 0
    prix_rate = 0
    
    try:
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Efface l'écran
            print("\033c", end="")
            
            # Récupération des statistiques actuelles
            stats = get_database_stats(conn)
            recent_products = get_recent_product_ids(conn)
            log_lines = get_log_activity()
            products_without_prices = get_products_without_prices(conn)
            recent_prices = get_recent_prices(conn)
            
            # Calcul du temps écoulé depuis la dernière mise à jour
            time_diff = current_time - last_update_time
            
            # Calcul des taux d'extraction uniquement si un minimum de temps s'est écoulé
            if time_diff >= refresh_rate:
                # Produits ajoutés depuis la dernière mise à jour
                new_produits = stats['total_produits'] - prev_stats['total_produits']
                new_prix = stats['total_prix'] - prev_stats['total_prix']
                
                # Calcul des taux par minute
                if time_diff > 0:
                    produits_rate = (new_produits / time_diff) * 60  # Conversion en taux par minute
                    prix_rate = (new_prix / time_diff) * 60  # Conversion en taux par minute
                
                # Mise à jour des variables pour la prochaine itération
                prev_stats = stats
                last_update_time = current_time
            
            # Calcul des taux d'extraction globaux (depuis le début)
            global_elapsed = current_time - start_time
            if global_elapsed > 0:
                global_produits_rate = (stats['total_produits'] / global_elapsed) * 60  # Conversion en taux par minute
                global_prix_rate = (stats['total_prix'] / global_elapsed) * 60  # Conversion en taux par minute
            else:
                global_produits_rate = 0
                global_prix_rate = 0
            
            # Affiche l'en-tête
            print("\n" + f"{header_bg}{header_fg}{'=' * 80}{Colors.RESET}")
            print(f"{header_bg}{header_fg}{Colors.BOLD} PRIX.NC DATA RETRIEVAL SYSTEM - STATS VIEWER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {Colors.RESET}".center(90))
            print(f"{header_bg}{header_fg}{'=' * 80}{Colors.RESET}" + "\n")
            
            # Durée d'exécution
            duration = format_duration(elapsed)
            print(f"{accent}Durée d'exécution: {duration}{Colors.RESET}")
            print(f"{Colors.BRIGHT_BLACK}" + "-" * 80 + Colors.RESET)
            
            # Section Statistiques générales
            print(f"\n{header_bg}{header_fg} STATISTIQUES GÉNÉRALES {Colors.RESET}")
            
            print(f"{primary_label}  Produits totaux          : {primary_value}{stats['total_produits']:,}{Colors.RESET}")
            print(f"{primary_label}  Prix totaux              : {primary_value}{stats['total_prix']:,}{Colors.RESET}")
            
            # Statistique de progression
            progress_color = error
            if stats['pourcentage_avec_prix'] > 75:
                progress_color = success
            elif stats['pourcentage_avec_prix'] > 30:
                progress_color = warning
                
            print(f"{primary_label}  Produits avec prix       : {primary_value}{stats['produits_avec_prix']:,} {progress_color}({stats['pourcentage_avec_prix']:.2f}%){Colors.RESET}")
            
            # Ajout d'une barre de progression visuelle
            progress_bar_width = 50
            filled_width = int(progress_bar_width * stats['pourcentage_avec_prix'] / 100)
            empty_width = progress_bar_width - filled_width
            
            progress_bar = f"{Colors.BRIGHT_BLACK}[{progress_color}{'#' * filled_width}{Colors.BRIGHT_BLACK}{' ' * empty_width}] {progress_color}{stats['pourcentage_avec_prix']:.2f}%{Colors.RESET}"
            print(f"{primary_label}  Progression              : {progress_bar}")
            
            print(f"{primary_label}  Moyenne de prix/produit  : {primary_value}{stats['moyenne_prix_par_produit']:.2f}{Colors.RESET}")
            print(f"{primary_label}  Dernière mise à jour     : {primary_value}{stats['derniere_maj_produit']}{Colors.RESET}")
            
            # Section Taux d'extraction
            print(f"\n{header_bg}{header_fg} TAUX D'EXTRACTION (par minute) {Colors.RESET}")
            
            # Coloration du taux selon sa valeur
            prod_rate_color = error
            if produits_rate > 300:
                prod_rate_color = success
            elif produits_rate > 60:
                prod_rate_color = warning
                
            prix_rate_color = error
            if prix_rate > 600:
                prix_rate_color = success
            elif prix_rate > 180:
                prix_rate_color = warning
                
            print(f"{secondary_label}  Produits                 : {prod_rate_color}{produits_rate:.2f}{Colors.RESET}")
            print(f"{secondary_label}  Prix                     : {prix_rate_color}{prix_rate:.2f}{Colors.RESET}")
            
            # Section Taux d'extraction global
            print(f"\n{header_bg}{header_fg} TAUX D'EXTRACTION GLOBAL (depuis le début) {Colors.RESET}")
            print(f"{secondary_label}  Produits                 : {secondary_value}{global_produits_rate:.2f}{Colors.RESET}")
            print(f"{secondary_label}  Prix                     : {secondary_value}{global_prix_rate:.2f}{Colors.RESET}")
            
            # Section Distribution par secteur
            print(f"\n{header_bg}{header_fg} DISTRIBUTION PAR SECTEUR (Top 5) {Colors.RESET}")
            
            for i, (secteur, count) in enumerate(stats['distribution_secteurs']):
                if not secteur:
                    secteur = "Non spécifié"
                print(f"{secondary_label}  {secteur:<30} : {primary_value}{count:,}{Colors.RESET}")
            
            # Section Produits récents
            print(f"\n{header_bg}{header_fg} PRODUITS RÉCEMMENT AJOUTÉS {Colors.RESET}")
            for id_produit, intitule, date in recent_products:
                # Tronquer l'intitulé si nécessaire
                max_len = 50
                intitule = intitule if intitule else "Produit sans nom"
                if len(intitule) > max_len:
                    intitule = intitule[:max_len] + "..."
                print(f"{secondary_label}  {intitule:<50} {Colors.BRIGHT_BLACK}|{primary_label} {date}{Colors.RESET}")
            
            # Section Produits sans prix
            print(f"\n{header_bg}{header_fg} PRODUITS SANS PRIX {Colors.RESET}")
            for id_produit, intitule, secteur, date in products_without_prices:
                # Tronquer l'intitulé si nécessaire
                max_len = 40
                intitule = intitule if intitule else "Produit sans nom"
                secteur = secteur if secteur else "Non spécifié"
                if len(intitule) > max_len:
                    intitule = intitule[:max_len] + "..."
                if len(secteur) > 20:
                    secteur = secteur[:20] + "..."
                print(f"{secondary_label}  {intitule:<40} {Colors.BRIGHT_BLACK}|{primary_label} {secteur:<20} | {date}{Colors.RESET}")
            
            # Section Prix récents
            print(f"\n{header_bg}{header_fg} PRIX RÉCEMMENT AJOUTÉS {Colors.RESET}")
            for intitule, prix, magasin, date in recent_prices:
                # Tronquer l'intitulé si nécessaire
                max_len = 40
                intitule = intitule if intitule else "Produit sans nom"
                magasin = magasin if magasin else "Magasin inconnu"
                if len(intitule) > max_len:
                    intitule = intitule[:max_len] + "..."
                if len(magasin) > 20:
                    magasin = magasin[:20] + "..."
                
                # Conversion du prix pour l'affichage (valeur stockée en XPF/centimes)
                prix_format = f"{prix} XPF" if prix is not None else "Prix inconnu"
                
                print(f"{secondary_label}  {intitule:<40} {Colors.BRIGHT_BLACK}|{primary_label} {prix_format:<10} {Colors.BRIGHT_BLACK}|{primary_label} {magasin:<20} | {date}{Colors.RESET}")
            
            # Section Log d'activité
            print(f"\n{header_bg}{header_fg} ACTIVITÉ RÉCENTE (logs) {Colors.RESET}")
            for line in log_lines:
                line = line.strip()
                if "ERROR" in line or "error" in line:
                    print(f"{error}  {line}{Colors.RESET}")
                elif "WARNING" in line or "warning" in line:
                    print(f"{warning}  {line}{Colors.RESET}")
                elif "INFO" in line:
                    if "prix trouvé" in line and "Aucun" not in line:
                        print(f"{success}  {line}{Colors.RESET}")
                    else:
                        print(f"{primary_label}  {line}{Colors.RESET}")
                else:
                    print(f"  {line}")
            
            # Instructions
            print("\n" + f"{Colors.BRIGHT_BLACK}" + "-" * 80 + Colors.RESET)
            print(f"{header_bg}{header_fg} Ctrl+C pour quitter | Les données sont actualisées automatiquement {Colors.RESET}".center(90))
            print(f"{Colors.BRIGHT_BLACK}" + "-" * 80 + Colors.RESET)
            
            # Attente avant actualisation
            time.sleep(refresh_rate)
            
    except KeyboardInterrupt:
        print(f"\n{accent}Arrêt du visualiseur.{Colors.RESET}")
    finally:
        # Fermeture de la connexion
        if conn:
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="Visualiseur en temps réel pour Prix.nc Data Retrieval System")
    parser.add_argument("-d", "--database", default="prix_nc.db", help="Chemin vers la base de données SQLite")
    parser.add_argument("-r", "--refresh", type=int, default=2, help="Taux de rafraîchissement en secondes (défaut: 2)")
    args = parser.parse_args()
    
    try:
        display_stats(args.database, args.refresh)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Arrêt du visualiseur.{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Erreur: {str(e)}{Colors.RESET}")

if __name__ == "__main__":
    main()
