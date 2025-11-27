"""
Système de Gestion de Station d'Essence - TOTAL
Point d'entrée principal avec authentification
"""

import customtkinter as ctk
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from auth_system import AuthSystem
from notification_system import NotificationManager
import os

def main():
    """Fonction principale avec écran de login"""
    
    # Configuration de CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Créer le dossier data
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialiser la base de données
    db = DatabaseManager()
    db.initialize_database()
    
    # Initialiser le système d'auth
    auth = AuthSystem()
    
    # Créer la fenêtre de login
    login_window = LoginWindow(auth)
    login_window.mainloop()
    
    # Si authentifié, lancer l'app principale
    if auth.current_user:
        app = MainWindow(auth)
        app.mainloop()


class LoginWindow(ctk.CTk):
    """Fenêtre de connexion"""
    
    def __init__(self, auth_system: AuthSystem):
        super().__init__()
        
        self.auth = auth_system
        self.title("TOTAL - Connexion")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Couleurs
        self.colors = {
            'primary': '#1976D2',
            'warning': '#FF9800',
            'dark': '#424242'
        }
        
        self.create_widgets()
        
        # Centrer la fenêtre
        self.center_window()
    
    def create_widgets(self):
        """Crée l'interface de login"""
        
        # Header avec logo
        header = ctk.CTkFrame(self, fg_color=self.colors['warning'], height=150)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="🏪",
            font=ctk.CTkFont(size=64)
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            header,
            text="TOTAL Station Service",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack()
        
        # Form
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=60, pady=40)
        
        ctk.CTkLabel(
            form_frame,
            text="Connexion",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 30))
        
        # Username
        ctk.CTkLabel(
            form_frame,
            text="Nom d'utilisateur:",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Entrez votre nom d'utilisateur",
            height=40
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password
        ctk.CTkLabel(
            form_frame,
            text="Mot de passe:",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(10, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Entrez votre mot de passe",
            show="•",
            height=40
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Message d'erreur
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        self.error_label.pack(pady=(0, 10))
        
        # Bouton connexion
        ctk.CTkButton(
            form_frame,
            text="Se Connecter",
            command=self.login,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary']
        ).pack(fill="x", pady=10)
        
        # Info par défaut
        info_text = "👤 Par défaut: admin / admin123"
        ctk.CTkLabel(
            form_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=20)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Tente la connexion"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="❌ Veuillez remplir tous les champs")
            return
        
        # Vérifier tentatives échouées
        failed_attempts = self.auth.get_failed_login_attempts(username, 30)
        if failed_attempts >= 5:
            self.error_label.configure(
                text="❌ Trop de tentatives échouées. Réessayez dans 30 minutes."
            )
            return
        
        # Tenter la connexion
        if self.auth.login(username, password):
            self.destroy()  # Fermer la fenêtre de login
        else:
            self.error_label.configure(
                text=f"❌ Identifiants incorrects ({5-failed_attempts-1} essais restants)"
            )
            self.password_entry.delete(0, 'end')
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')


if __name__ == "__main__":
    main()