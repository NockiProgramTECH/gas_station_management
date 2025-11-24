"""
Système de Gestion de Station d'Essence - TOTAL
Point d'entrée principal de l'application

Auteur: Système de Gestion
Date: 2024
Version: 1.0
"""

import customtkinter as ctk
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
import os

def main():
    """
    Fonction principale pour lancer l'application
    
    Cette fonction initialise la base de données et lance l'interface graphique
    """
    # Configuration de CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Créer le dossier data s'il n'existe pas
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialiser la base de données
    db = DatabaseManager()
    db.initialize_database()
    
    # Créer et lancer l'interface
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()