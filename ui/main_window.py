"""
Interface Principale de l'Application
Fenêtre principale avec navigation et différentes vues
"""

import customtkinter as ctk
# from ui.enhanced_dashboard import DashboardFrame
from ui.fuel_inventory import FuelInventoryFrame
from ui.sales import SalesFrame
from ui.employees import EmployeesFrame
from ui.reports import ReportsFrame
from ui.settings import SettingsFrame
from PIL import Image
import os

from ui.enhanced_dashboard import EnhancedDashboard
from notification_system import NotificationManager
from auth_system import AuthSystem

class MainWindow(ctk.CTk):
    def __init__(self, auth_system: AuthSystem):
        super().__init__()
        
        self.auth = auth_system
         
        # Configuration de la fenêtre
        self.title("TOTAL - Gestion Station d'Essence")
        self.geometry("1400x900")
        
        # Couleurs basées sur l'image
        self.colors = {
            'primary': '#1976D2',      # Bleu
            'success': '#4CAF50',      # Vert
            'warning': '#FF9800',      # Orange
            'danger': '#F44336',       # Rouge
            'dark': '#424242',         # Gris foncé
            'light': '#F5F5F5',        # Gris clair
            'white': '#FFFFFF'
        }
        
        self.current_frame = None
        self.nav_buttons = {}
        
        self.create_widgets()
        self.show_dashboard()
    
    def create_widgets(self):
        """
        Crée tous les widgets de l'interface
        """
        # Configuration du grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Créer la sidebar
        self.create_sidebar()
        
        # Container principal
        self.main_container = ctk.CTkFrame(self, fg_color=self.colors['light'])
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
    
    def create_sidebar(self):
        """
        Crée la barre latérale de navigation
        """
        # Sidebar frame
        sidebar = ctk.CTkFrame(self, width=240, fg_color=self.colors['dark'],corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)
        sidebar.grid_propagate(False)
        
        # Logo frame
        logo_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['dark'], height=80)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        logo_img = Image.open("assets/logo.png")
        logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
        logo_img = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(150,150))

        # Logo TOTAL
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#EE3124",
            image=logo_img
        )
        logo_label.pack(pady=10)
        
        # Boutons de navigation
        nav_items = [
            ("🏠 Dashboard", self.show_dashboard, 1),
            ("⛽ Fuel Inventory", self.show_fuel_inventory, 2),
            ("💰 Sales & Transactions", self.show_sales, 3),
            ("👥 Employee Management", self.show_employees, 4),
            ("📊 Reports & Analytics", self.show_reports, 5),
            ("⚙️ Settings", self.show_settings, 6),
        ]
        
        for text, command, row in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                width=200,
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color="white",
                hover_color=self.colors['primary'],
                anchor="w",
                corner_radius=8
            )
            btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[text] = btn
    
    def highlight_button(self, button_text: str):
        """
        Met en surbrillance le bouton actif
        
        Args:
            button_text (str): Texte du bouton à mettre en surbrillance
        """
        for text, btn in self.nav_buttons.items():
            if text == button_text:
                btn.configure(fg_color=self.colors['primary'])
            else:
                btn.configure(fg_color="transparent")
    
    def clear_main_container(self):
        """
        Nettoie le container principal
        """
        if self.current_frame:
            self.current_frame.destroy()
    
    def show_dashboard(self):
        """
        Affiche le tableau de bord
        """
        self.clear_main_container()
        self.highlight_button("🏠 Dashboard")
        self.current_frame = DashboardFrame(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_fuel_inventory(self):
        """
        Affiche l'inventaire des carburants
        """
        self.clear_main_container()
        self.highlight_button("⛽ Fuel Inventory")
        self.current_frame = FuelInventoryFrame(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_sales(self):
        """
        Affiche les ventes et transactions
        """
        self.clear_main_container()
        self.highlight_button("💰 Sales & Transactions")
        self.current_frame = SalesFrame(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_employees(self):
        """
        Affiche la gestion des employés
        """
        self.clear_main_container()
        self.highlight_button("👥 Employee Management")
        self.current_frame = EmployeesFrame(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_reports(self):
        """
        Affiche les rapports et analyses
        """
        self.clear_main_container()
        self.highlight_button("📊 Reports & Analytics")
        self.current_frame = ReportsFrame(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
    
    def show_settings(self):
        """
        Affiche les paramètres
        """
        self.clear_main_container()
        self.highlight_button("⚙️ Settings")
        self.current_frame = SettingsFrame(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Initialiser le gestionnaire de notifications
        self.notifications = NotificationManager(self, self.colors)
        
        # Message de bienvenue
        self.notifications.show(
            f"Bienvenue {self.auth.current_user['full_name']} !",
            'success',
            duration=3000
        )
    
    def show_dashboard(self):
        """Affiche le dashboard amélioré"""
        self.clear_main_container()
        self.highlight_button("🏠 Dashboard")
        # Utiliser le nouveau dashboard
        self.current_frame = EnhancedDashboard(self.main_container, self.colors)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)