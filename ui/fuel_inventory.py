"""
Gestion de l'inventaire des carburants
Interface pour gérer les réservoirs et les niveaux quotidiens
"""
"""
Gestion de l'inventaire des carburants
Interface pour gérer les réservoirs et les niveaux quotidiens
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from datetime import datetime
from tkinter import messagebox
from typing import Dict, List

class FuelInventoryFrame(ctk.CTkFrame):
    """
    Frame de gestion de l'inventaire de carburant
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
        current_daily_data (List): Données actuelles des niveaux quotidiens
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
        self.current_daily_data = []
        
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
    
    def calculate_remaining_quantity(self, reservoir_id: int, date: str) -> float:
        """
        Calcule la quantité restante basée sur les ventes
        
        Args:
            reservoir_id (int): ID du réservoir
            date (str): Date au format YYYY-MM-DD
            
        Returns:
            float: Quantité restante en litres
        """
        try:
            # Obtenir le niveau quotidien
            niveau = self.db.obtenir_niveau_quotidien(reservoir_id, date)
            if not niveau:
                return 0
            
            # Obtenir les ventes pour ce réservoir à cette date
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT SUM(quantite_vendue) as total_vendu
                FROM ventes 
                WHERE reservoir_id = ? AND date = ?
            ''', (reservoir_id, date))
            
            result = cursor.fetchone()
            total_vendu = result['total_vendu'] if result and result['total_vendu'] else 0
            conn.close()
            
            # Calculer la quantité restante
            quantite_totale = niveau['quantite_debut'] + niveau['quantite_entree']
            quantite_restante = quantite_totale - total_vendu
            
            return max(0, quantite_restante)
        except Exception as e:
            print(f"Erreur calcul quantité restante: {e}")
            return 0
    
    def load_reservoirs(self):
        """
        Charge la liste des réservoirs avec les quantités restantes
        """
        reservoirs = self.db.obtenir_reservoirs()
        today = datetime.now().strftime('%Y-%m-%d')
        
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
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        headers = ["Name", "Type", "Capacity (L)", "Current Level", "Remaining (L)", "Status"]
        header_config = [
            {"width": 120, "anchor": "center"},
            {"width": 100, "anchor": "center"},
            {"width": 100, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 100, "anchor": "center"}
        ]
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['dark'],
                width=header_config[i]["width"],
                anchor=header_config[i]["anchor"]
            )
            label.grid(row=0, column=i, padx=2, pady=15)
        
        # Reservoir rows
        for reservoir in reservoirs:
            row_frame = ctk.CTkFrame(scroll, fg_color=self.colors['white'], height=50)
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
            
            # Calculer les quantités
            quantite_restante = self.calculate_remaining_quantity(reservoir['id'], today)
            niveau = self.db.obtenir_niveau_quotidien(reservoir['id'], today)
            quantite_totale = (niveau['quantite_debut'] + niveau['quantite_entree']) if niveau else 0
            pourcentage = (quantite_restante / reservoir['capacite_max']) * 100 if reservoir['capacite_max'] > 0 else 0
            
            # Déterminer le statut et la couleur
            if pourcentage < reservoir['seuil_alerte']:
                status_color = self.colors['danger']
                status_text = "LOW"
            elif pourcentage < 30:
                status_color = self.colors['warning']
                status_text = "MEDIUM"
            else:
                status_color = self.colors['success']
                status_text = "OK"
            
            # Name
            ctk.CTkLabel(
                row_frame,
                text=reservoir['nom'],
                font=ctk.CTkFont(size=11),
                width=120,
                anchor="center"
            ).grid(row=0, column=0, padx=2, pady=10)
            
            # Type avec couleur
            type_label = ctk.CTkLabel(
                row_frame,
                text=reservoir['type_carburant'],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white",
                fg_color=self.get_fuel_color(reservoir['type_carburant']),
                corner_radius=8,
                width=100,
                anchor="center"
            )
            type_label.grid(row=0, column=1, padx=2, pady=8)
            
            # Capacity
            ctk.CTkLabel(
                row_frame,
                text=f"{reservoir['capacite_max']:,.0f}",
                font=ctk.CTkFont(size=11),
                width=100,
                anchor="center"
            ).grid(row=0, column=2, padx=2, pady=10)
            
            # Current level avec barre de progression visuelle
            level_text = f"{quantite_totale:,.0f}L ({pourcentage:.1f}%)"
            ctk.CTkLabel(
                row_frame,
                text=level_text,
                font=ctk.CTkFont(size=11),
                width=120,
                anchor="center"
            ).grid(row=0, column=3, padx=2, pady=10)
            
            # Remaining quantity
            remaining_text = f"{quantite_restante:,.0f}L"
            ctk.CTkLabel(
                row_frame,
                text=remaining_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=status_color,
                width=120,
                anchor="center"
            ).grid(row=0, column=4, padx=2, pady=10)
            
            # Status
            status_label = ctk.CTkLabel(
                row_frame,
                text=status_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white",
                fg_color=status_color,
                corner_radius=8,
                width=100,
                anchor="center"
            )
            status_label.grid(row=0, column=5, padx=2, pady=8)
    
    def get_fuel_color(self, fuel_type: str) -> str:
        """
        Retourne la couleur associée au type de carburant
        
        Args:
            fuel_type (str): Type de carburant
            
        Returns:
            str: Code couleur
        """
        colors = {
            'Gasoline': self.colors['warning'],
            'Diesel': self.colors['primary'],
            'Premium': self.colors['success']
        }
        return colors.get(fuel_type, self.colors['dark'])
    
    def load_daily_levels(self):
        """
        Charge les niveaux quotidiens dans un tableau éditable
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Container principal
        main_frame = ctk.CTkFrame(self.content_area, fg_color=self.colors['white'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            controls_frame,
            text="Date:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        self.date_entry = ctk.CTkEntry(
            controls_frame,
            width=150,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.insert(0, today)
        self.date_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="🔍 Load",
            width=100,
            command=self.refresh_daily_levels,
            fg_color=self.colors['primary']
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="💾 Save All",
            width=120,
            command=self.save_all_daily_levels,
            fg_color=self.colors['success']
        ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="🔄 Reset",
            width=100,
            command=self.refresh_daily_levels,
            fg_color=self.colors['warning']
        ).pack(side="right", padx=10)
        
        # Table container
        table_container = ctk.CTkFrame(main_frame, fg_color=self.colors['white'], corner_radius=10)
        table_container.grid(row=1, column=0, sticky="nsew")
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Table header
        header_frame = ctk.CTkFrame(table_container, fg_color=self.colors['light'], height=50)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        headers = ["Reservoir", "Fuel Type", "Start Qty (L)", "Entry Qty (L)", "Total Qty (L)", "Remaining (L)"]
        header_config = [
            {"width": 150, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"}
        ]
        
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['dark'],
                width=header_config[i]["width"],
                anchor=header_config[i]["anchor"]
            ).grid(row=0, column=i, padx=2, pady=15)
        
        # Table content (scrollable)
        self.daily_table_scroll = ctk.CTkScrollableFrame(
            table_container,
            fg_color=self.colors['white']
        )
        self.daily_table_scroll.grid(row=1, column=0, sticky="nsew")
        
        # Charger les données initiales
        self.display_daily_levels_table()
    
    def display_daily_levels_table(self):
        """
        Affiche les niveaux quotidiens dans un tableau éditable
        """
        # Nettoyer le tableau
        for widget in self.daily_table_scroll.winfo_children():
            widget.destroy()
        
        reservoirs = self.db.obtenir_reservoirs()
        selected_date = self.date_entry.get()
        self.current_daily_data = []
        
        if not reservoirs:
            ctk.CTkLabel(
                self.daily_table_scroll,
                text="No reservoirs configured",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['dark']
            ).pack(pady=50)
            return
        
        for idx, reservoir in enumerate(reservoirs):
            row_frame = ctk.CTkFrame(
                self.daily_table_scroll, 
                fg_color=self.colors['white'] if idx % 2 == 0 else self.colors['light'],
                height=50
            )
            row_frame.pack(fill="x", pady=1)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
            
            # Obtenir les données existantes
            niveau = self.db.obtenir_niveau_quotidien(reservoir['id'], selected_date)
            quantite_restante = self.calculate_remaining_quantity(reservoir['id'], selected_date)
            
            # Stocker les données pour la sauvegarde
            row_data = {
                'reservoir_id': reservoir['id'],
                'date': selected_date,
                'quantite_debut': niveau['quantite_debut'] if niveau else 0,
                'quantite_entree': niveau['quantite_entree'] if niveau else 0
            }
            self.current_daily_data.append(row_data)
            
            # Reservoir name (readonly)
            ctk.CTkLabel(
                row_frame,
                text=reservoir['nom'],
                font=ctk.CTkFont(size=11),
                width=150,
                anchor="center"
            ).grid(row=0, column=0, padx=2, pady=10)
            
            # Fuel type (readonly)
            type_label = ctk.CTkLabel(
                row_frame,
                text=reservoir['type_carburant'],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white",
                fg_color=self.get_fuel_color(reservoir['type_carburant']),
                corner_radius=8,
                width=120,
                anchor="center"
            )
            type_label.grid(row=0, column=1, padx=2, pady=8)
            
            # Start quantity (editable)
            start_entry = ctk.CTkEntry(
                row_frame,
                width=120,
                font=ctk.CTkFont(size=11),
                justify="center"
            )
            start_entry.insert(0, str(row_data['quantite_debut']))
            start_entry.grid(row=0, column=2, padx=2, pady=8)
            
            # Entry quantity (editable)
            entry_entry = ctk.CTkEntry(
                row_frame,
                width=120,
                font=ctk.CTkFont(size=11),
                justify="center"
            )
            entry_entry.insert(0, str(row_data['quantite_entree']))
            entry_entry.grid(row=0, column=3, padx=2, pady=8)
            
            # Total quantity (calculated, readonly)
            total_qty = row_data['quantite_debut'] + row_data['quantite_entree']
            total_label = ctk.CTkLabel(
                row_frame,
                text=f"{total_qty:,.0f}",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=120,
                anchor="center"
            )
            total_label.grid(row=0, column=4, padx=2, pady=10)
            
            # Remaining quantity (calculated, readonly)
            remaining_label = ctk.CTkLabel(
                row_frame,
                text=f"{quantite_restante:,.0f}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors['success'],
                width=120,
                anchor="center"
            )
            remaining_label.grid(row=0, column=5, padx=2, pady=10)
            
            # Stocker les références pour la mise à jour
            row_data['start_entry'] = start_entry
            row_data['entry_entry'] = entry_entry
            row_data['total_label'] = total_label
            row_data['remaining_label'] = remaining_label
            
            # Lier les événements de modification
            start_entry.bind('<KeyRelease>', lambda e, idx=idx: self.update_calculations(idx))
            entry_entry.bind('<KeyRelease>', lambda e, idx=idx: self.update_calculations(idx))
    
    def update_calculations(self, row_index: int):
        """
        Met à jour les calculs pour une ligne spécifique
        
        Args:
            row_index (int): Index de la ligne à mettre à jour
        """
        try:
            row_data = self.current_daily_data[row_index]
            
            # Lire les nouvelles valeurs
            start_qty = float(row_data['start_entry'].get() or 0)
            entry_qty = float(row_data['entry_entry'].get() or 0)
            
            # Mettre à jour les données
            row_data['quantite_debut'] = start_qty
            row_data['quantite_entree'] = entry_qty
            
            # Calculer le total
            total_qty = start_qty + entry_qty
            
            # Mettre à jour les labels
            row_data['total_label'].configure(text=f"{total_qty:,.0f}")
            
            # Recalculer la quantité restante
            quantite_restante = self.calculate_remaining_quantity(
                row_data['reservoir_id'], 
                row_data['date']
            )
            row_data['remaining_label'].configure(text=f"{quantite_restante:,.0f}")
            
        except ValueError:
            # En cas d'erreur de conversion, ignorer
            pass
    
    def save_all_daily_levels(self):
        """
        Sauvegarde tous les niveaux quotidiens modifiés
        """
        try:
            saved_count = 0
            for row_data in self.current_daily_data:
                reservoir_id = row_data['reservoir_id']
                date = row_data['date']
                quantite_debut = row_data['quantite_debut']
                quantite_entree = row_data['quantite_entree']
                
                # Sauvegarder dans la base de données
                self.db.enregistrer_niveau_quotidien(
                    reservoir_id, date, quantite_debut, quantite_entree
                )
                saved_count += 1
            
            messagebox.showinfo("Success", f"{saved_count} daily levels saved successfully!")
            self.refresh_daily_levels()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save daily levels: {str(e)}")
    
    def refresh_daily_levels(self):
        """
        Rafraîchit l'affichage des niveaux quotidiens
        """
        self.display_daily_levels_table()
    
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

    # Les méthodes show_add_reservoir_dialog et show_add_level_dialog restent inchangées
    # ... (le reste du code existant pour les dialogues)
    
    def show_add_reservoir_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter un réservoir
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Reservoir")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.wait_visibility()
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
        dialog.wait_visibility()
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