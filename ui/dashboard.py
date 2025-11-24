"""
Tableau de bord principal
Affiche les statistiques principales de la station
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from datetime import datetime
from typing import Dict
from PIL import Image, ImageTk
import os
import urllib.request

class DashboardFrame(ctk.CTkFrame):
    """
    Frame du tableau de bord principal
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le tableau de bord
        
        Args:
            parent: Widget parent
            colors (Dict): Dictionnaire des couleurs
        """
        super().__init__(parent, fg_color=colors['light'])
        self.colors = colors
        self.db = DatabaseManager()
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """
        Crée tous les widgets du tableau de bord
        """
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=self.colors['dark'], height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo dans le header
        try:
            logo_img = Image.open("assets/logo.png")
            logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
            logo_photo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(50, 50))
            logo_label = ctk.CTkLabel(
                header_frame,
                image=logo_photo,
                text=""
            )
            logo_label.image = logo_photo  # Garder référence
            logo_label.grid(row=0, column=0, padx=(40, 20), pady=20, sticky="w")
        except Exception as e:
            print(f"Erreur chargement logo: {e}")
            # Logo de secours si l'image n'est pas trouvée
            logo_label = ctk.CTkLabel(
                header_frame,
                text="🏪",
                font=ctk.CTkFont(size=28),
                text_color=self.colors['warning']
            )
            logo_label.grid(row=0, column=0, padx=(40, 20), pady=20, sticky="w")
        
        # welcome_label = ctk.CTkLabel(
        #     header_frame,
        #     text="WELCOME!",
        #     font=ctk.CTkFont(size=36, weight="bold"),
        #     text_color=self.colors['warning']
        # )
        # welcome_label.grid(row=0, column=0, padx=(120, 0), pady=20, sticky="w")
        
        # Menu button (hamburger)
        menu_btn = ctk.CTkButton(
            header_frame,
            text="☰",
            width=50,
            height=50,
            font=ctk.CTkFont(size=24),
            fg_color="transparent",
            hover_color=self.colors['primary']
        )
        menu_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        
        # Content area
        content_frame = ctk.CTkFrame(self, fg_color=self.colors['light'])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Hero image avec l'image du pompiste
        hero_frame = ctk.CTkFrame(
            content_frame,
            height=250,
            fg_color=self.colors['white'],
            corner_radius=15
        )
        hero_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        hero_frame.grid_propagate(False)
        
        # Charger l'image du pompiste
        try:
            pompiste_img = Image.open("assets/pompiste.png")
            # Redimensionner pour s'adapter à la zone hero (environ 900x250)
            pompiste_img = pompiste_img.resize((900, 450), Image.Resampling.LANCZOS)
            pompiste_photo = ctk.CTkImage(light_image=pompiste_img, dark_image=pompiste_img, size=(900, 450))
            pompiste_label = ctk.CTkLabel(
                hero_frame,
                image=pompiste_photo,
                text=""
            )
            pompiste_label.image = pompiste_photo  # Garder référence
            pompiste_label.pack(fill="both", expand=True, padx=0, pady=0)
        except Exception as e:
            print(f"Erreur chargement image pompiste: {e}")
            # Image de secours si l'image n'est pas trouvée
            hero_label = ctk.CTkLabel(
                hero_frame,
                text="🚗 Station Service TOTAL",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=self.colors['dark']
            )
            hero_label.pack(expand=True)
        
        # Stats cards
        # Current Fuel Levels Card
        self.fuel_card = self.create_card(
            content_frame,
            "CURRENT FUEL LEVELS",
            self.colors['primary'],
            1, 0
        )
        
        # Today's Sales Card
        self.sales_card = self.create_card(
            content_frame,
            "TODAY'S SALES",
            self.colors['success'],
            1, 1
        )
        
        # Employees on Duty Card
        self.employees_card = self.create_card(
            content_frame,
            "EMPLOYEES ON DUTY",
            self.colors['warning'],
            1, 2
        )
        
        # Last updated
        update_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        update_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        self.last_update_label = ctk.CTkLabel(
            update_frame,
            text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['dark']
        )
        self.last_update_label.pack(side="left", padx=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            update_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=120,
            height=35,
            fg_color=self.colors['primary'],
            hover_color=self.colors['dark']
        )
        refresh_btn.pack(side="right", padx=10)
    
    def create_card(self, parent, title: str, color: str, row: int, col: int) -> ctk.CTkFrame:
        """
        Crée une carte statistique
        
        Args:
            parent: Widget parent
            title (str): Titre de la carte
            color (str): Couleur de fond
            row (int): Ligne dans le grid
            col (int): Colonne dans le grid
            
        Returns:
            ctk.CTkFrame: Frame de la carte
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=15,
            height=200
        )
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        card.grid_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(20, 10))
        
        # Content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        return content
    
    def load_data(self):
        """
        Charge les données du tableau de bord
        """
        # Load fuel levels
        self.load_fuel_levels()
        
        # Load today's sales
        self.load_sales()
        
        # Load employees on duty
        self.load_employees()
    
    def load_fuel_levels(self):
        """
        Charge les niveaux de carburant actuels
        """
        reservoirs = self.db.obtenir_reservoirs()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for widget in self.fuel_card.winfo_children():
            widget.destroy()
        
        if not reservoirs:
            label = ctk.CTkLabel(
                self.fuel_card,
                text="No reservoir configured",
                font=ctk.CTkFont(size=13),
                text_color="white"
            )
            label.pack(pady=10)
            return
        
        for reservoir in reservoirs[:3]:  # Afficher max 3
            niveau = self.db.obtenir_niveau_quotidien(reservoir['id'], today)
            
            if niveau:
                quantite = niveau['quantite_debut'] + niveau['quantite_entree']
                pourcentage = (quantite / reservoir['capacite_max']) * 100
            else:
                pourcentage = 0
            
            # Fuel row avec style moderne
            fuel_row = ctk.CTkFrame(self.fuel_card, fg_color="transparent")
            fuel_row.pack(fill="x", pady=8)
            
            # Container pour le nom et pourcentage
            info_container = ctk.CTkFrame(fuel_row, fg_color="transparent")
            info_container.pack(fill="x")
            
            fuel_label = ctk.CTkLabel(
                info_container,
                text=reservoir['type_carburant'],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            fuel_label.pack(side="left")
            
            # Icône emoji selon le niveau
            if pourcentage < 20:
                emoji = "😟"
            elif pourcentage < 50:
                emoji = "😐"
            else:
                emoji = "😊"
            
            # Container pour pourcentage et emoji
            percentage_container = ctk.CTkFrame(info_container, fg_color="transparent")
            percentage_container.pack(side="right")
            
            percentage_label = ctk.CTkLabel(
                percentage_container,
                text=f"{pourcentage:.0f}%",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
            percentage_label.pack(side="left", padx=(0, 5))
            
            emoji_label = ctk.CTkLabel(
                percentage_container,
                text=emoji,
                font=ctk.CTkFont(size=16)
            )
            emoji_label.pack(side="left")
    
    def load_sales(self):
        """
        Charge les ventes du jour
        """
        today = datetime.now().strftime('%Y-%m-%d')
        ventes = self.db.obtenir_ventes_par_date(today)
        
        for widget in self.sales_card.winfo_children():
            widget.destroy()
        
        total = sum(v['montant_total'] for v in ventes)
        
        # Container principal centré
        main_container = ctk.CTkFrame(self.sales_card, fg_color="transparent")
        main_container.pack(expand=True)
        
        # Total amount avec style moderne
        amount_label = ctk.CTkLabel(
            main_container,
            text=f"${total:,.2f}",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="white"
        )
        amount_label.pack(pady=(10, 10))
        
        # Icône avec flèche montante et dollar
        icon_container = ctk.CTkFrame(main_container, fg_color="transparent")
        icon_container.pack()
        
        up_arrow = ctk.CTkLabel(
            icon_container,
            text="↗",
            font=ctk.CTkFont(size=28),
            text_color="white"
        )
        up_arrow.pack(side="left", padx=5)
        
        dollar_icon = ctk.CTkLabel(
            icon_container,
            text="💵",
            font=ctk.CTkFont(size=28)
        )
        dollar_icon.pack(side="left", padx=5)
    
    def load_employees(self):
        """
        Charge les employés en service
        """
        pompistes = self.db.obtenir_pompistes()
        
        for widget in self.employees_card.winfo_children():
            widget.destroy()
        
        # Number
        number_label = ctk.CTkLabel(
            self.employees_card,
            text=str(len(pompistes)),
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="white"
        )
        number_label.pack(pady=20)
        
        # Employee photos
        if pompistes:
            photos_frame = ctk.CTkFrame(self.employees_card, fg_color="transparent")
            photos_frame.pack()
            
            # Afficher jusqu'à 4 employés
            for i, pompiste in enumerate(pompistes[:4]):
                photo_frame = ctk.CTkFrame(
                    photos_frame, 
                    fg_color=self.colors['white'],
                    width=50, 
                    height=50, 
                    corner_radius=25
                )
                photo_frame.grid(row=0, column=i, padx=5)
                photo_frame.grid_propagate(False)
                
                # Charger la photo si elle existe
                photo_path = pompiste.get('photo_path', '')
                if photo_path and os.path.exists(photo_path):
                    try:
                        img = Image.open(photo_path)
                        img = img.resize((45, 45), Image.Resampling.LANCZOS)
                        photo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(45, 45))
                        photo_label = ctk.CTkLabel(photo_frame, image=photo_img, text="")
                        photo_label.image = photo_img  # Garder référence
                        photo_label.pack(expand=True)
                    except Exception as e:
                        print(f"Erreur chargement photo: {e}")
                        # Icône par défaut
                        ctk.CTkLabel(
                            photo_frame,
                            text="👤",
                            font=ctk.CTkFont(size=24),
                            text_color=self.colors['dark']
                        ).pack(expand=True)
                else:
                    # Icône par défaut
                    ctk.CTkLabel(
                        photo_frame,
                        text="👤",
                        font=ctk.CTkFont(size=24),
                        text_color=self.colors['dark']
                    ).pack(expand=True)
    
        
    def refresh_data(self):
        """
        Rafraîchit les données du tableau de bord
        """
        self.load_data()
        # Le label de temps se met déjà à jour automatiquement via update_time_label()