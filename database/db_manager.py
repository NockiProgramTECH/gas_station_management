"""
Gestionnaire de Base de Données
Module pour gérer toutes les opérations de base de données SQLite
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

class DatabaseManager:
    """
    Classe pour gérer toutes les opérations de base de données
    
    Attributes:
        db_path (str): Chemin vers le fichier de base de données
    """
    
    def __init__(self, db_path: str = 'data/station.db'):
        """
        Initialise le gestionnaire de base de données
        
        Args:
            db_path (str): Chemin vers le fichier de base de données
        """
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Crée et retourne une connexion à la base de données
        
        Returns:
            sqlite3.Connection: Connexion à la base de données
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """
        Initialise toutes les tables de la base de données
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des réservoirs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservoirs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type_carburant TEXT NOT NULL,
                capacite_max REAL NOT NULL,
                seuil_alerte REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des niveaux de carburant quotidiens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS niveaux_quotidiens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservoir_id INTEGER,
                date DATE NOT NULL,
                quantite_debut REAL NOT NULL,
                quantite_entree REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reservoir_id) REFERENCES reservoirs (id)
            )
        ''')
        
        # Table des ventes par période
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservoir_id INTEGER,
                pompiste_id INTEGER,
                date DATE NOT NULL,
                periode TEXT NOT NULL,
                quantite_vendue REAL NOT NULL,
                montant_total REAL NOT NULL,
                heure_debut TIME,
                heure_fin TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reservoir_id) REFERENCES reservoirs (id),
                FOREIGN KEY (pompiste_id) REFERENCES pompistes (id)
            )
        ''')
        
        # Table des pompistes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pompistes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                telephone TEXT,
                email TEXT,
                photo_path TEXT,
                statut TEXT DEFAULT 'actif',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table du planning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pompiste_id INTEGER,
                date DATE NOT NULL,
                jour_semaine TEXT NOT NULL,
                periode TEXT NOT NULL,
                heure_debut TIME NOT NULL,
                heure_fin TIME NOT NULL,
                FOREIGN KEY (pompiste_id) REFERENCES pompistes (id)
            )
        ''')
        
        # Table des mouvements de stock
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mouvements_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservoir_id INTEGER,
                type_mouvement TEXT NOT NULL,
                quantite REAL NOT NULL,
                date_mouvement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reference TEXT,
                notes TEXT,
                FOREIGN KEY (reservoir_id) REFERENCES reservoirs (id)
            )
        ''')
        
        # Table des alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservoir_id INTEGER,
                type_alerte TEXT NOT NULL,
                message TEXT NOT NULL,
                date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                statut TEXT DEFAULT 'non_lu',
                FOREIGN KEY (reservoir_id) REFERENCES reservoirs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ===== GESTION DES RÉSERVOIRS =====
    
    def ajouter_reservoir(self, nom: str, type_carburant: str, 
                         capacite_max: float, seuil_alerte: float) -> int:
        """
        Ajoute un nouveau réservoir
        
        Args:
            nom (str): Nom du réservoir
            type_carburant (str): Type de carburant (Gasoline, Diesel, Premium)
            capacite_max (float): Capacité maximale en litres
            seuil_alerte (float): Seuil d'alerte en pourcentage
            
        Returns:
            int: ID du réservoir créé
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reservoirs (nom, type_carburant, capacite_max, seuil_alerte)
            VALUES (?, ?, ?, ?)
        ''', (nom, type_carburant, capacite_max, seuil_alerte))
        
        reservoir_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reservoir_id
    
    def obtenir_reservoirs(self) -> List[Dict]:
        """
        Récupère tous les réservoirs
        
        Returns:
            List[Dict]: Liste des réservoirs
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reservoirs')
        reservoirs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return reservoirs
    
    def obtenir_reservoir(self, reservoir_id: int) -> Optional[Dict]:
        """
        Récupère un réservoir spécifique
        
        Args:
            reservoir_id (int): ID du réservoir
            
        Returns:
            Optional[Dict]: Données du réservoir ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reservoirs WHERE id = ?', (reservoir_id,))
        reservoir = cursor.fetchone()
        
        conn.close()
        return dict(reservoir) if reservoir else None
    
    # ===== GESTION DES NIVEAUX QUOTIDIENS =====
    
    def enregistrer_niveau_quotidien(self, reservoir_id: int, date: str, 
                                    quantite_debut: float, quantite_entree: float = 0) -> int:
        """
        Enregistre le niveau quotidien d'un réservoir
        
        Args:
            reservoir_id (int): ID du réservoir
            date (str): Date au format YYYY-MM-DD
            quantite_debut (float): Quantité au début de la journée
            quantite_entree (float): Quantité entrée dans la journée
            
        Returns:
            int: ID de l'enregistrement
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO niveaux_quotidiens 
            (reservoir_id, date, quantite_debut, quantite_entree)
            VALUES (?, ?, ?, ?)
        ''', (reservoir_id, date, quantite_debut, quantite_entree))
        
        niveau_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return niveau_id
    
    def obtenir_niveau_quotidien(self, reservoir_id: int, date: str) -> Optional[Dict]:
        """
        Récupère le niveau quotidien d'un réservoir pour une date
        
        Args:
            reservoir_id (int): ID du réservoir
            date (str): Date au format YYYY-MM-DD
            
        Returns:
            Optional[Dict]: Niveau quotidien ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM niveaux_quotidiens 
            WHERE reservoir_id = ? AND date = ?
        ''', (reservoir_id, date))
        
        niveau = cursor.fetchone()
        conn.close()
        
        return dict(niveau) if niveau else None
    
    # ===== GESTION DES VENTES =====
    
    def enregistrer_vente(self, reservoir_id: int, pompiste_id: int, date: str,
                         periode: str, quantite_vendue: float, montant_total: float,
                         heure_debut: str, heure_fin: str) -> int:
        """
        Enregistre une vente
        
        Args:
            reservoir_id (int): ID du réservoir
            pompiste_id (int): ID du pompiste
            date (str): Date de la vente
            periode (str): Période (matin, soir, nuit)
            quantite_vendue (float): Quantité vendue en litres
            montant_total (float): Montant total
            heure_debut (str): Heure de début
            heure_fin (str): Heure de fin
            
        Returns:
            int: ID de la vente
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ventes 
            (reservoir_id, pompiste_id, date, periode, quantite_vendue, 
             montant_total, heure_debut, heure_fin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reservoir_id, pompiste_id, date, periode, quantite_vendue, 
              montant_total, heure_debut, heure_fin))
        
        vente_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return vente_id
    
    def obtenir_ventes_par_date(self, date: str) -> List[Dict]:
        """
        Récupère toutes les ventes pour une date
        
        Args:
            date (str): Date au format YYYY-MM-DD
            
        Returns:
            List[Dict]: Liste des ventes
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.*, r.type_carburant, p.nom, p.prenom
            FROM ventes v
            JOIN reservoirs r ON v.reservoir_id = r.id
            JOIN pompistes p ON v.pompiste_id = p.id
            WHERE v.date = ?
        ''', (date,))
        
        ventes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return ventes
    
    def calculer_pertes(self, reservoir_id: int, date: str) -> Dict:
        """
        Calcule les pertes pour un réservoir et une date
        
        Args:
            reservoir_id (int): ID du réservoir
            date (str): Date au format YYYY-MM-DD
            
        Returns:
            Dict: Résultat avec pertes de produit et d'argent
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer le niveau du matin
        niveau = self.obtenir_niveau_quotidien(reservoir_id, date)
        if not niveau:
            return {'erreur': 'Niveau quotidien non trouvé'}
        
        # Récupérer toutes les ventes de la journée
        cursor.execute('''
            SELECT SUM(quantite_vendue) as total_vendu, 
                   SUM(montant_total) as total_montant
            FROM ventes
            WHERE reservoir_id = ? AND date = ?
        ''', (reservoir_id, date))
        
        ventes_jour = cursor.fetchone()
        
        # Récupérer le prix unitaire (dernière vente)
        cursor.execute('''
            SELECT montant_total / quantite_vendue as prix_unitaire
            FROM ventes
            WHERE reservoir_id = ? AND date = ?
            LIMIT 1
        ''', (reservoir_id, date))
        
        prix = cursor.fetchone()
        prix_unitaire = prix['prix_unitaire'] if prix else 0
        
        conn.close()
        
        quantite_debut = niveau['quantite_debut'] + niveau['quantite_entree']
        quantite_vendue = ventes_jour['total_vendu'] if ventes_jour['total_vendu'] else 0
        
        # Calculer la quantité théorique restante
        quantite_theorique = quantite_debut - quantite_vendue
        
        # Pour cet exemple, on suppose qu'on connaît la quantité réelle
        # Dans la pratique, il faudrait mesurer le niveau actuel
        
        return {
            'quantite_debut': quantite_debut,
            'quantite_vendue': quantite_vendue,
            'quantite_theorique': quantite_theorique,
            'montant_total': ventes_jour['total_montant'] if ventes_jour['total_montant'] else 0,
            'prix_unitaire': prix_unitaire
        }
    
    # ===== GESTION DES POMPISTES =====
    
    def ajouter_pompiste(self, nom: str, prenom: str, 
                        telephone: str = '', email: str = '') -> int:
        """
        Ajoute un nouveau pompiste
        
        Args:
            nom (str): Nom du pompiste
            prenom (str): Prénom du pompiste
            telephone (str): Numéro de téléphone
            email (str): Email
            
        Returns:
            int: ID du pompiste créé
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pompistes (nom, prenom, telephone, email)
            VALUES (?, ?, ?, ?)
        ''', (nom, prenom, telephone, email))
        
        pompiste_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return pompiste_id
    
    def obtenir_pompistes(self, statut: str = 'actif') -> List[Dict]:
        """
        Récupère tous les pompistes
        
        Args:
            statut (str): Statut des pompistes à récupérer
            
        Returns:
            List[Dict]: Liste des pompistes
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pompistes WHERE statut = ?', (statut,))
        pompistes = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return pompistes
    
    # ===== GESTION DU PLANNING =====
    
    def ajouter_planning(self, pompiste_id: int, date: str, jour_semaine: str,
                        periode: str, heure_debut: str, heure_fin: str) -> int:
        """
        Ajoute une entrée au planning
        
        Args:
            pompiste_id (int): ID du pompiste
            date (str): Date
            jour_semaine (str): Jour de la semaine
            periode (str): Période (matin, soir, nuit)
            heure_debut (str): Heure de début
            heure_fin (str): Heure de fin
            
        Returns:
            int: ID de l'entrée planning
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO planning 
            (pompiste_id, date, jour_semaine, periode, heure_debut, heure_fin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pompiste_id, date, jour_semaine, periode, heure_debut, heure_fin))
        
        planning_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return planning_id
    
    def obtenir_planning_semaine(self, date_debut: str) -> List[Dict]:
        """
        Récupère le planning pour une semaine
        
        Args:
            date_debut (str): Date de début de la semaine
            
        Returns:
            List[Dict]: Planning de la semaine
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, po.nom, po.prenom
            FROM planning p
            JOIN pompistes po ON p.pompiste_id = po.id
            WHERE p.date >= ?
            ORDER BY p.date, p.heure_debut
        ''', (date_debut,))
        
        planning = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return planning
    
    # ===== GESTION DES ALERTES =====
    
    def creer_alerte(self, reservoir_id: int, type_alerte: str, message: str) -> int:
        """
        Crée une nouvelle alerte
        
        Args:
            reservoir_id (int): ID du réservoir
            type_alerte (str): Type d'alerte
            message (str): Message de l'alerte
            
        Returns:
            int: ID de l'alerte
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alertes (reservoir_id, type_alerte, message)
            VALUES (?, ?, ?)
        ''', (reservoir_id, type_alerte, message))
        
        alerte_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alerte_id
    
    def verifier_seuils(self):
        """
        Vérifie les seuils de tous les réservoirs et crée des alertes si nécessaire
        """
        reservoirs = self.obtenir_reservoirs()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for reservoir in reservoirs:
            niveau = self.obtenir_niveau_quotidien(reservoir['id'], today)
            if niveau:
                quantite_actuelle = niveau['quantite_debut'] + niveau['quantite_entree']
                pourcentage = (quantite_actuelle / reservoir['capacite_max']) * 100
                
                if pourcentage <= reservoir['seuil_alerte']:
                    message = f"Niveau bas pour {reservoir['nom']}: {pourcentage:.1f}%"
                    self.creer_alerte(reservoir['id'], 'niveau_bas', message)
    
    def obtenir_alertes_non_lues(self) -> List[Dict]:
        """
        Récupère toutes les alertes non lues
        
        Returns:
            List[Dict]: Liste des alertes non lues
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, r.nom as reservoir_nom
            FROM alertes a
            JOIN reservoirs r ON a.reservoir_id = r.id
            WHERE a.statut = 'non_lu'
            ORDER BY a.date_alerte DESC
        ''')
        
        alertes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return alertes