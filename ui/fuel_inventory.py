"""
Gestion de l'inventaire des carburants
Interface pour gérer les réservoirs et les niveaux quotidiens
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from datetime import datetime
from tkinter import messagebox
from typing import Dict

class FuelInventoryFrame(ctk.CTkFrame):
    """
    Frame de gestion de l'inventaire de carburant
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le frame d'inventaire
        
        Args:
            parent: Widget parent
            colors (Dict): Dictionnaire des couleurs
        """
        super().__init__(parent, fg_color=colors['white'])
        self.colors = colors
        self.db = DatabaseManager()
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_reservoirs()
    
    def create_widgets(self):
        """
        Crée tous les widgets de la page
        """
        # Header
        header = ctk.CTkFrame(self, fg_color=self.colors['primary'], height=100)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="⛽ Fuel Inventory Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=30)
        
        # Add reservoir button
        add_btn = ctk.CTkButton(
            header,
            text="+ New Reservoir",
            command=self.show_add_reservoir_dialog,
            width=150,
            height=40,
            fg_color=self.colors['success'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="right", padx=30)
        
        # Main content
        content = ctk.CTkFrame(self, fg_color=self.colors['light'])
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # Tabs
        tab_frame = ctk.CTkFrame(content, fg_color="transparent")
        tab_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.tab_reservoirs = ctk.CTkButton(
            tab_frame,
            text="Reservoirs",
            command=lambda: self.switch_tab("reservoirs"),
            width=150,
            height=40,
            fg_color=self.colors['primary']
        )
        self.tab_reservoirs.pack(side="left", padx=5)
        
        self.tab_daily = ctk.CTkButton(
            tab_frame,
            text="Daily Levels",
            command=lambda: self.switch_tab("daily"),
            width=150,
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color=self.colors['primary'],
            text_color=self.colors['primary']
        )
        self.tab_daily.pack(side="left", padx=5)
        
        self.tab_movements = ctk.CTkButton(
            tab_frame,
            text="Stock Movements",
            command=lambda: self.switch_tab("movements"),
            width=150,
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color=self.colors['primary'],
            text_color=self.colors['primary']
        )
        self.tab_movements.pack(side="left", padx=5)
        
        # Content area
        self.content_area = ctk.CTkFrame(content, fg_color=self.colors['white'])
        self.content_area.grid(row=1, column=0, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.current_tab = "reservoirs"
    
    def switch_tab(self, tab_name: str):
        """
        Change l'onglet actif
        
        Args:
            tab_name (str): Nom de l'onglet à afficher
        """
        self.current_tab = tab_name
        
        # Update button styles
        tabs = {
            "reservoirs": self.tab_reservoirs,
            "daily": self.tab_daily,
            "movements": self.tab_movements
        }
        
        for name, btn in tabs.items():
            if name == tab_name:
                btn.configure(
                    fg_color=self.colors['primary'],
                    text_color="white",
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors['primary'],
                    border_width=2,
                    border_color=self.colors['primary']
                )
        
        # Clear and reload content
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        if tab_name == "reservoirs":
            self.load_reservoirs()
        elif tab_name == "daily":
            self.load_daily_levels()
        elif tab_name == "movements":
            self.load_movements()
    
    def load_reservoirs(self):
        """
        Charge la liste des réservoirs
        """
        reservoirs = self.db.obtenir_reservoirs()
        
        if not reservoirs:
            label = ctk.CTkLabel(
                self.content_area,
                text="No reservoirs configured. Click 'New Reservoir' to add one.",
                font=ctk.CTkFont(size=16),
                text_color=self.colors['dark']
            )
            label.pack(pady=50)
            return
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header row
        header_frame = ctk.CTkFrame(scroll, fg_color=self.colors['light'], height=50)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        headers = ["Name", "Type", "Capacity (L)", "Alert Threshold (%)"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors['dark']
            )
            label.grid(row=0, column=i, padx=10, pady=10)
        
        # Reservoir rows
        for reservoir in reservoirs:
            row_frame = ctk.CTkFrame(scroll, fg_color=self.colors['white'], height=60)
            row_frame.pack(fill="x", pady=5)
            row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            # Name
            ctk.CTkLabel(
                row_frame,
                text=reservoir['nom'],
                font=ctk.CTkFont(size=13)
            ).grid(row=0, column=0, padx=10, pady=15)
            
            # Type
            type_label = ctk.CTkLabel(
                row_frame,
                text=reservoir['type_carburant'],
                font=ctk.CTkFont(size=13, weight="bold")
            )
            type_label.grid(row=0, column=1, padx=10, pady=15)
            
            # Capacity
            ctk.CTkLabel(
                row_frame,
                text=f"{reservoir['capacite_max']:,.0f}",
                font=ctk.CTkFont(size=13)
            ).grid(row=0, column=2, padx=10, pady=15)
            
            # Alert threshold
            ctk.CTkLabel(
                row_frame,
                text=f"{reservoir['seuil_alerte']}%",
                font=ctk.CTkFont(size=13)
            ).grid(row=0, column=3, padx=10, pady=15)
    
    def load_daily_levels(self):
        """
        Charge les niveaux quotidiens
        """
        # Nettoyer d'abord le content_area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Date selector
        date_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            date_frame,
            text="Date:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        self.date_entry = ctk.CTkEntry(
            date_frame,
            width=150,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.insert(0, today)
        self.date_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(
            date_frame,
            text="Load",
            width=100,
            command=self.refresh_daily_levels,  # Utiliser une fonction séparée
            fg_color=self.colors['primary']
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            date_frame,
            text="+ Add Level",
            width=120,
            command=self.show_add_level_dialog,
            fg_color=self.colors['success']
        ).pack(side="right", padx=10)
        
        # Content
        self.daily_levels_scroll = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.daily_levels_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Charger les données initiales
        self.display_daily_levels()
    
    def refresh_daily_levels(self):
        """
        Rafraîchit l'affichage des niveaux quotidiens sans recréer l'interface
        """
        self.display_daily_levels()
    
    def display_daily_levels(self):
        """
        Affiche les niveaux quotidiens dans le scroll frame
        """
        # Nettoyer seulement le scroll frame
        for widget in self.daily_levels_scroll.winfo_children():
            widget.destroy()
        
        reservoirs = self.db.obtenir_reservoirs()
        selected_date = self.date_entry.get()
        
        for reservoir in reservoirs:
            niveau = self.db.obtenir_niveau_quotidien(reservoir['id'], selected_date)
            
            card = ctk.CTkFrame(self.daily_levels_scroll, fg_color=self.colors['white'])
            card.pack(fill="x", pady=10, padx=10)
            
            # Title
            ctk.CTkLabel(
                card,
                text=f"{reservoir['nom']} - {reservoir['type_carburant']}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=10)
            
            if niveau:
                info_text = f"Start: {niveau['quantite_debut']:,.0f}L | Entry: {niveau['quantite_entree']:,.0f}L | Total: {niveau['quantite_debut'] + niveau['quantite_entree']:,.0f}L"
            else:
                info_text = "No data for this date"
            
            ctk.CTkLabel(
                card,
                text=info_text,
                font=ctk.CTkFont(size=13)
            ).pack(pady=10)
    
    def load_movements(self):
        """
        Charge les mouvements de stock
        """
        label = ctk.CTkLabel(
            self.content_area,
            text="Stock Movements - Coming Soon",
            font=ctk.CTkFont(size=18),
            text_color=self.colors['dark']
        )
        label.pack(pady=50)
    
    def show_add_reservoir_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter un réservoir
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Reservoir")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text="New Reservoir",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Form
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Name
        ctk.CTkLabel(form_frame, text="Name:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Tank A")
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Type
        ctk.CTkLabel(form_frame, text="Fuel Type:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        type_var = ctk.StringVar(value="Gasoline")
        type_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["Gasoline", "Diesel", "Premium"],
            variable=type_var
        )
        type_menu.pack(fill="x", pady=(0, 10))
        
        # Capacity
        ctk.CTkLabel(form_frame, text="Max Capacity (Liters):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        capacity_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 50000")
        capacity_entry.pack(fill="x", pady=(0, 10))
        
        # Alert threshold
        ctk.CTkLabel(form_frame, text="Alert Threshold (%):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        threshold_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 20")
        threshold_entry.pack(fill="x", pady=(0, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=20)
        
        def save_reservoir():
            try:
                nom = name_entry.get()
                type_carburant = type_var.get()
                capacite = float(capacity_entry.get())
                seuil = float(threshold_entry.get())
                
                if not nom:
                    messagebox.showerror("Error", "Please enter a name")
                    return
                
                self.db.ajouter_reservoir(nom, type_carburant, capacite, seuil)
                messagebox.showinfo("Success", "Reservoir added successfully!")
                dialog.destroy()
                self.load_reservoirs()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save_reservoir,
            width=120,
            fg_color=self.colors['success']
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            fg_color=self.colors['danger']
        ).pack(side="right", padx=5)
    
    def show_add_level_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter un niveau quotidien
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Daily Level")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text="Record Daily Level",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Form
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Reservoir
        ctk.CTkLabel(form_frame, text="Reservoir:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        reservoirs = self.db.obtenir_reservoirs()
        reservoir_names = [f"{r['nom']} - {r['type_carburant']}" for r in reservoirs]
        reservoir_var = ctk.StringVar(value=reservoir_names[0] if reservoir_names else "")
        reservoir_menu = ctk.CTkOptionMenu(form_frame, values=reservoir_names, variable=reservoir_var)
        reservoir_menu.pack(fill="x", pady=(0, 10))
        
        # Date
        ctk.CTkLabel(form_frame, text="Date:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        date_entry = ctk.CTkEntry(form_frame)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack(fill="x", pady=(0, 10))
        
        # Starting quantity
        ctk.CTkLabel(form_frame, text="Starting Quantity (L):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        start_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 45000")
        start_entry.pack(fill="x", pady=(0, 10))
        
        # Entry quantity
        ctk.CTkLabel(form_frame, text="Entry Quantity (L):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        entry_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 0")
        entry_entry.insert(0, "0")
        entry_entry.pack(fill="x", pady=(0, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=20)
        
        def save_level():
            try:
                selected_idx = reservoir_names.index(reservoir_var.get())
                reservoir_id = reservoirs[selected_idx]['id']
                date = date_entry.get()
                start_qty = float(start_entry.get())
                entry_qty = float(entry_entry.get())
                
                self.db.enregistrer_niveau_quotidien(reservoir_id, date, start_qty, entry_qty)
                messagebox.showinfo("Success", "Daily level recorded successfully!")
                dialog.destroy()
                self.load_daily_levels()
            except (ValueError, IndexError) as e:
                messagebox.showerror("Error", f"Please enter valid values: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save_level,
            width=120,
            fg_color=self.colors['success']
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            fg_color=self.colors['danger']
        ).pack(side="right", padx=5)