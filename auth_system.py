"""
Système d'Authentification et Gestion des Utilisateurs
Sécurité, rôles et permissions
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

class AuthSystem:
    """
    Système d'authentification avec gestion des rôles
    
    Attributes:
        db_path (str): Chemin vers la base de données
        current_user (Dict): Utilisateur actuellement connecté
        session_token (str): Token de session
    """
    
    ROLES = {
        'admin': {
            'name': 'Administrateur',
            'permissions': ['all']
        },
        'manager': {
            'name': 'Gérant',
            'permissions': ['view_reports', 'manage_inventory', 'manage_sales', 'manage_employees']
        },
        'cashier': {
            'name': 'Caissier',
            'permissions': ['record_sales', 'view_inventory']
        },
        'attendant': {
            'name': 'Pompiste',
            'permissions': ['view_schedule']
        }
    }
    
    def __init__(self, db_path: str = 'data/station.db'):
        """
        Initialise le système d'authentification
        
        Args:
            db_path (str): Chemin vers la base de données
        """
        self.db_path = db_path
        self.current_user = None
        self.session_token = None
        self.initialize_auth_tables()
    
    def get_connection(self) -> sqlite3.Connection:
        """Crée une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_auth_tables(self):
        """Initialise les tables d'authentification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Table des sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table de l'audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                old_value TEXT,
                new_value TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table des tentatives de connexion
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                success INTEGER NOT NULL,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        
        # Créer un admin par défaut si aucun utilisateur n'existe
        cursor.execute('SELECT COUNT(*) as count FROM users')
        count = cursor.fetchone()['count']
        
        if count == 0:
            self._create_default_admin()
        
        conn.close()
    
    def _create_default_admin(self):
        """Crée un administrateur par défaut"""
        self.create_user(
            username='admin',
            password='admin123',
            role='admin',
            full_name='Administrateur',
            email='admin@station.com'
        )
        print("✅ Utilisateur admin créé: admin / admin123")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Hash un mot de passe avec salt
        
        Args:
            password (str): Mot de passe en clair
            salt (str): Salt (généré si None)
            
        Returns:
            tuple: (hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(32)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return pwd_hash, salt
    
    def create_user(self, username: str, password: str, role: str,
                   full_name: str, email: str = '', phone: str = '',
                   created_by: int = None) -> Optional[int]:
        """
        Crée un nouvel utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            role (str): Rôle (admin, manager, cashier, attendant)
            full_name (str): Nom complet
            email (str): Email
            phone (str): Téléphone
            created_by (int): ID de l'utilisateur créateur
            
        Returns:
            Optional[int]: ID de l'utilisateur créé ou None
        """
        if role not in self.ROLES:
            print(f"❌ Rôle invalide: {role}")
            return None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier si username existe déjà
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                print(f"❌ Nom d'utilisateur déjà existant: {username}")
                conn.close()
                return None
            
            # Hasher le mot de passe
            pwd_hash, salt = self.hash_password(password)
            
            # Insérer l'utilisateur
            cursor.execute('''
                INSERT INTO users 
                (username, password_hash, salt, role, full_name, email, phone, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, pwd_hash, salt, role, full_name, email, phone, created_by))
            
            user_id = cursor.lastrowid
            
            # Logger l'action
            if self.current_user:
                self.log_action(
                    'create_user',
                    'user',
                    user_id,
                    None,
                    json.dumps({'username': username, 'role': role})
                )
            
            conn.commit()
            conn.close()
            
            return user_id
        
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            return None
    
    def login(self, username: str, password: str, ip_address: str = None) -> bool:
        """
        Authentifie un utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            ip_address (str): Adresse IP
            
        Returns:
            bool: True si authentification réussie
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Récupérer l'utilisateur
            cursor.execute('''
                SELECT * FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))
            
            user = cursor.fetchone()
            
            if not user:
                self._log_login_attempt(username, False, ip_address)
                return False
            
            # Vérifier le mot de passe
            pwd_hash, _ = self.hash_password(password, user['salt'])
            
            if pwd_hash != user['password_hash']:
                self._log_login_attempt(username, False, ip_address)
                return False
            
            # Créer une session
            self.session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=8)
            
            cursor.execute('''
                INSERT INTO sessions 
                (user_id, token, ip_address, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (user['id'], self.session_token, ip_address, expires_at))
            
            # Mettre à jour last_login
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user['id'],))
            
            conn.commit()
            
            # Stocker l'utilisateur courant
            self.current_user = dict(user)
            
            # Logger succès
            self._log_login_attempt(username, True, ip_address)
            self.log_action('login', 'session', None, None, None)
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur login: {e}")
            return False
        
        finally:
            conn.close()
    
    def logout(self):
        """Déconnecte l'utilisateur courant"""
        if self.session_token:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET is_active = 0 
                WHERE token = ?
            ''', (self.session_token,))
            
            conn.commit()
            conn.close()
            
            self.log_action('logout', 'session', None, None, None)
        
        self.current_user = None
        self.session_token = None
    
    def check_permission(self, permission: str) -> bool:
        """
        Vérifie si l'utilisateur courant a une permission
        
        Args:
            permission (str): Permission à vérifier
            
        Returns:
            bool: True si permission accordée
        """
        if not self.current_user:
            return False
        
        role = self.current_user['role']
        permissions = self.ROLES.get(role, {}).get('permissions', [])
        
        return 'all' in permissions or permission in permissions
    
    def require_permission(self, permission: str) -> bool:
        """
        Vérifie la permission ou lève une exception
        
        Args:
            permission (str): Permission requise
            
        Returns:
            bool: True si permission accordée
            
        Raises:
            PermissionError: Si permission refusée
        """
        if not self.check_permission(permission):
            raise PermissionError(f"Permission refusée: {permission}")
        return True
    
    def get_all_users(self) -> List[Dict]:
        """
        Récupère tous les utilisateurs
        
        Returns:
            List[Dict]: Liste des utilisateurs
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role, full_name, email, phone, 
                   is_active, last_login, created_at
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return users
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """
        Met à jour un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
            **kwargs: Champs à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        allowed_fields = ['full_name', 'email', 'phone', 'role', 'is_active']
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Récupérer anciennes valeurs pour audit
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            old_user = cursor.fetchone()
            
            # Mettre à jour
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            values.append(user_id)
            
            cursor.execute(query, values)
            conn.commit()
            
            # Logger
            self.log_action(
                'update_user',
                'user',
                user_id,
                json.dumps(dict(old_user)),
                json.dumps(kwargs)
            )
            
            conn.close()
            return True
        
        except Exception as e:
            print(f"❌ Erreur mise à jour: {e}")
            return False
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change le mot de passe d'un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
            new_password (str): Nouveau mot de passe
            
        Returns:
            bool: True si changement réussi
        """
        try:
            pwd_hash, salt = self.hash_password(new_password)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, salt = ? 
                WHERE id = ?
            ''', (pwd_hash, salt, user_id))
            
            conn.commit()
            conn.close()
            
            self.log_action('change_password', 'user', user_id, None, None)
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur changement mot de passe: {e}")
            return False
    
    def log_action(self, action: str, entity_type: str = None,
                  entity_id: int = None, old_value: str = None,
                  new_value: str = None, ip_address: str = None):
        """
        Enregistre une action dans l'audit log
        
        Args:
            action (str): Action effectuée
            entity_type (str): Type d'entité
            entity_id (int): ID de l'entité
            old_value (str): Ancienne valeur (JSON)
            new_value (str): Nouvelle valeur (JSON)
            ip_address (str): Adresse IP
        """
        if not self.current_user:
            return
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_log 
                (user_id, action, entity_type, entity_id, old_value, new_value, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.current_user['id'], action, entity_type, entity_id,
                  old_value, new_value, ip_address))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"❌ Erreur log action: {e}")
    
    def get_audit_log(self, limit: int = 100, user_id: int = None) -> List[Dict]:
        """
        Récupère l'historique des actions
        
        Args:
            limit (int): Nombre d'entrées à récupérer
            user_id (int): Filtrer par utilisateur
            
        Returns:
            List[Dict]: Historique des actions
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT a.*, u.username, u.full_name
                FROM audit_log a
                JOIN users u ON a.user_id = u.id
                WHERE a.user_id = ?
                ORDER BY a.timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT a.*, u.username, u.full_name
                FROM audit_log a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        log = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return log
    
    def _log_login_attempt(self, username: str, success: bool, ip_address: str = None):
        """
        Enregistre une tentative de connexion
        
        Args:
            username (str): Nom d'utilisateur
            success (bool): Succès ou échec
            ip_address (str): Adresse IP
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO login_attempts 
                (username, success, ip_address)
                VALUES (?, ?, ?)
            ''', (username, 1 if success else 0, ip_address))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"❌ Erreur log tentative: {e}")
    
    def get_failed_login_attempts(self, username: str, minutes: int = 30) -> int:
        """
        Compte les tentatives échouées récentes
        
        Args:
            username (str): Nom d'utilisateur
            minutes (int): Période en minutes
            
        Returns:
            int: Nombre de tentatives échouées
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(minutes=minutes)
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM login_attempts
            WHERE username = ? 
            AND success = 0 
            AND timestamp > ?
        ''', (username, since))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0