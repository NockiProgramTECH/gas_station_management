"""
Gestion des ventes et transactions
Interface pour enregistrer et suivre les ventes par période
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from datetime import datetime
from tkinter import messagebox
from typing import Dict
import json
import os

class SalesFrame(ctk.CTkFrame):
    """
    Frame de gestion des ventes
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le frame des ventes
        
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
        self.load_sales()
    
    def create_widgets(self):
        """
        Crée tous les widgets de la page
        """
        # Header
        header = ctk.CTkFrame(self, fg_color=self.colors['success'], height=100)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="💰 Sales & Transactions",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=30)
        
        # Add sale button
        add_btn = ctk.CTkButton(
            header,
            text="+ New Sale",
            command=self.show_add_sale_dialog,
            width=150,
            height=40,
            fg_color=self.colors['warning'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_btn.pack(side="right", padx=30)
        
        # Main content
        content = ctk.CTkFrame(self, fg_color=self.colors['light'])
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # Date filter
        filter_frame = ctk.CTkFrame(content, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            filter_frame,
            text="Date:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        self.date_entry = ctk.CTkEntry(
            filter_frame,
            width=150,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(
            filter_frame,
            text="🔍 Search",
            width=100,
            command=self.load_sales,
            fg_color=self.colors['primary']
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            filter_frame,
            text="📊 Analyze Losses",
            width=150,
            command=self.show_loss_analysis,
            fg_color=self.colors['danger']
        ).pack(side="right", padx=10)
        
        # Summary cards
        summary_frame = ctk.CTkFrame(content, fg_color="transparent")
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.morning_card = self.create_summary_card(
            summary_frame, "☀️ Morning (6h-14h)", self.colors['warning'], 0
        )
        self.evening_card = self.create_summary_card(
            summary_frame, "🌆 Evening (14h-22h)", self.colors['primary'], 1
        )
        self.night_card = self.create_summary_card(
            summary_frame, "🌙 Night (22h-6h)", self.colors['dark'], 2
        )
        
        # Sales table container
        table_container = ctk.CTkFrame(content, fg_color=self.colors['white'], corner_radius=10)
        table_container.grid(row=2, column=0, sticky="nsew")
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Table header
        self.header_frame = ctk.CTkFrame(table_container, fg_color=self.colors['light'], height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # Table content (scrollable)
        self.table_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color=self.colors['white']
        )
        self.table_frame.grid(row=1, column=0, sticky="nsew")
    
    def create_summary_card(self, parent, title: str, color: str, col: int) -> ctk.CTkFrame:
        """
        Crée une carte résumé pour une période
        
        Args:
            parent: Widget parent
            title (str): Titre de la carte
            color (str): Couleur de fond
            col (int): Colonne dans le grid
            
        Returns:
            ctk.CTkFrame: Frame de la carte
        """
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15, height=120)
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False)
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 5))
        
        amount_label = ctk.CTkLabel(
            card,
            text="0 FCFA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        amount_label.pack(pady=5)
        
        qty_label = ctk.CTkLabel(
            card,
            text="0 L",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        qty_label.pack(pady=5)
        
        card.amount_label = amount_label
        card.qty_label = qty_label
        
        return card
    
    def load_sales(self):
        """
        Charge les ventes pour la date sélectionnée et les affiche dans un tableau
        """
        date = self.date_entry.get()
        ventes = self.db.obtenir_ventes_par_date(date)
        
        # Update summary cards
        periods = {'matin': self.morning_card, 'soir': self.evening_card, 'nuit': self.night_card}
        
        for period, card in periods.items():
            period_sales = [v for v in ventes if v['periode'] == period]
            total_amount = sum(v['montant_total'] for v in period_sales)
            total_qty = sum(v['quantite_vendue'] for v in period_sales)
            
            card.amount_label.configure(text=f"{total_amount:,.0f} FCFA")
            card.qty_label.configure(text=f"{total_qty:,.0f} L")
        
        # Clear table header and content
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Create table header
        headers = ["Period", "Fuel Type", "Attendant", "Quantity (L)", "Amount (FCFA)", "Time"]
        header_config = [
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 150, "anchor": "center"},
            {"width": 100, "anchor": "center"},
            {"width": 120, "anchor": "center"},
            {"width": 120, "anchor": "center"}
        ]
        
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors['dark'],
                width=header_config[i]["width"],
                anchor=header_config[i]["anchor"]
            )
            header_label.grid(row=0, column=i, padx=2, pady=15)
        
        if not ventes:
            # Message when no sales
            no_data_frame = ctk.CTkFrame(self.table_frame, fg_color=self.colors['white'], height=100)
            no_data_frame.pack(fill="x", pady=20)
            
            ctk.CTkLabel(
                no_data_frame,
                text="📭 No sales recorded for this date",
                font=ctk.CTkFont(size=16),
                text_color=self.colors['dark']
            ).pack(expand=True)
            return
        
        # Create data rows with alternating colors
        for idx, vente in enumerate(ventes):
            row_color = self.colors['white'] if idx % 2 == 0 else self.colors['light']
            
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=row_color, height=45)
            row_frame.pack(fill="x", pady=1)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
            
            # Period with icon
            period_icons = {'matin': '☀️', 'soir': '🌆', 'nuit': '🌙'}
            period_text = f"{period_icons.get(vente['periode'], '')} {vente['periode'].title()}"
            
            # Fuel type with color coding
            fuel_colors = {
                'Gasoline': self.colors['warning'],
                'Diesel': self.colors['primary'], 
                'Premium': self.colors['success']
            }
            
            # Create labels for each column
            period_label = ctk.CTkLabel(
                row_frame, 
                text=period_text, 
                font=ctk.CTkFont(size=12),
                width=120,
                anchor="center"
            )
            period_label.grid(row=0, column=0, padx=2, pady=10)
            
            fuel_label = ctk.CTkLabel(
                row_frame,
                text=vente['type_carburant'],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                fg_color=fuel_colors.get(vente['type_carburant'], self.colors['dark']),
                corner_radius=8,
                width=120,
                anchor="center"
            )
            fuel_label.grid(row=0, column=1, padx=2, pady=8)
            
            attendant_label = ctk.CTkLabel(
                row_frame,
                text=f"{vente.get('prenom', '')} {vente.get('nom', '')}".strip(),
                font=ctk.CTkFont(size=12),
                width=150,
                anchor="center"
            )
            attendant_label.grid(row=0, column=2, padx=2, pady=10)
            
            quantity_label = ctk.CTkLabel(
                row_frame,
                text=f"{vente['quantite_vendue']:,.1f}",
                font=ctk.CTkFont(size=12),
                width=100,
                anchor="center"
            )
            quantity_label.grid(row=0, column=3, padx=2, pady=10)
            
            amount_label = ctk.CTkLabel(
                row_frame,
                text=f"{vente['montant_total']:,.0f}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['success'],
                width=120,
                anchor="center"
            )
            amount_label.grid(row=0, column=4, padx=2, pady=10)
            
            time_label = ctk.CTkLabel(
                row_frame,
                text=f"{vente.get('heure_debut', '')}-{vente.get('heure_fin', '')}",
                font=ctk.CTkFont(size=11),
                width=120,
                anchor="center"
            )
            time_label.grid(row=0, column=5, padx=2, pady=10)
        
        # Add summary row
        total_frame = ctk.CTkFrame(self.table_frame, fg_color=self.colors['dark'], height=50)
        total_frame.pack(fill="x", pady=(10, 0))
        total_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        total_qty = sum(v['quantite_vendue'] for v in ventes)
        total_amount = sum(v['montant_total'] for v in ventes)
        
        ctk.CTkLabel(
            total_frame,
            text="TOTAL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            width=120,
            anchor="center"
        ).grid(row=0, column=0, padx=2, pady=12)
        
        ctk.CTkLabel(
            total_frame,
            text="",
            font=ctk.CTkFont(size=12),
            width=120,
            anchor="center"
        ).grid(row=0, column=1, padx=2, pady=12)
        
        ctk.CTkLabel(
            total_frame,
            text="",
            font=ctk.CTkFont(size=12),
            width=150,
            anchor="center"
        ).grid(row=0, column=2, padx=2, pady=12)
        
        ctk.CTkLabel(
            total_frame,
            text=f"{total_qty:,.1f} L",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            width=100,
            anchor="center"
        ).grid(row=0, column=3, padx=2, pady=12)
        
        ctk.CTkLabel(
            total_frame,
            text=f"{total_amount:,.0f} FCFA",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['warning'],
            width=120,
            anchor="center"
        ).grid(row=0, column=4, padx=2, pady=12)
        
        ctk.CTkLabel(
            total_frame,
            text=f"{len(ventes)} sales",
            font=ctk.CTkFont(size=12),
            text_color="white",
            width=120,
            anchor="center"
        ).grid(row=0, column=5, padx=2, pady=12)

    # Les autres méthodes restent inchangées...
    def show_add_sale_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter une vente
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Record New Sale")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color=self.colors['success'], height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="💰 Record New Sale",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title.pack(pady=15)
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=self.colors['light'])
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        form_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_frame.pack(fill="both", padx=30, pady=20)
        
        # Date et heure actuels
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        current_hour = now.hour
        
        # Déterminer la période automatiquement
        if 6 <= current_hour < 14:
            auto_period = "matin"
            period_label = "☀️ Morning (6h-14h)"
        elif 14 <= current_hour < 22:
            auto_period = "soir"
            period_label = "🌆 Evening (14h-22h)"
        else:
            auto_period = "nuit"
            period_label = "🌙 Night (22h-6h)"
        
        # Date (readonly)
        ctk.CTkLabel(form_frame, text="Date:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        date_display = ctk.CTkLabel(
            form_frame, 
            text=current_date,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['white'],
            height=35,
            corner_radius=6,
            anchor="w",
            padx=10
        )
        date_display.pack(fill="x", pady=(0, 10))
        
        # Heure actuelle (readonly)
        ctk.CTkLabel(form_frame, text="Time:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        time_display = ctk.CTkLabel(
            form_frame,
            text=current_time,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['white'],
            height=35,
            corner_radius=6,
            anchor="w",
            padx=10
        )
        time_display.pack(fill="x", pady=(0, 10))
        
        # Period (auto-détecté, readonly)
        ctk.CTkLabel(form_frame, text="Period:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        period_display = ctk.CTkLabel(
            form_frame,
            text=period_label,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            text_color="white",
            height=35,
            corner_radius=6
        )
        period_display.pack(fill="x", pady=(0, 10))
        
        # Trouver l'employé en service automatiquement
        pompiste_info = self.get_pompiste_en_service(current_date, auto_period, current_time)
        
        if pompiste_info:
            attendant_text = f"👤 {pompiste_info['prenom']} {pompiste_info['nom']}"
            attendant_color = self.colors['success']
        else:
            attendant_text = "⚠️ No attendant scheduled"
            attendant_color = self.colors['danger']
        
        # Attendant (auto-détecté, readonly)
        ctk.CTkLabel(form_frame, text="Attendant:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        attendant_display = ctk.CTkLabel(
            form_frame,
            text=attendant_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=attendant_color,
            text_color="white",
            height=35,
            corner_radius=6
        )
        attendant_display.pack(fill="x", pady=(0, 10))
        
        # Separator
        ctk.CTkFrame(form_frame, fg_color=self.colors['dark'], height=2).pack(fill="x", pady=15)
        
        # Reservoir
        ctk.CTkLabel(form_frame, text="Fuel Type:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        reservoirs = self.db.obtenir_reservoirs()
        reservoir_names = [f"{r['nom']} - {r['type_carburant']}" for r in reservoirs]
        reservoir_var = ctk.StringVar(value=reservoir_names[0] if reservoir_names else "")
        reservoir_menu = ctk.CTkOptionMenu(form_frame, values=reservoir_names, variable=reservoir_var, height=35)
        reservoir_menu.pack(fill="x", pady=(0, 10))
        
        # Total Amount (entrée principale)
        ctk.CTkLabel(form_frame, text="Total Amount (FCFA):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        amount_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 7500", height=35, font=ctk.CTkFont(size=14))
        amount_entry.pack(fill="x", pady=(0, 10))
        
        # Info label pour montrer le calcul
        info_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['primary']
        )
        info_label.pack(anchor="w", pady=(0, 10))
        
        # Fonction pour calculer la quantité automatiquement
        def calculate_quantity(*args):
            try:
                if amount_entry.get() and reservoir_var.get():
                    amount = float(amount_entry.get())
                    
                    # Récupérer le prix depuis settings
                    reservoir_idx = reservoir_names.index(reservoir_var.get())
                    fuel_type = reservoirs[reservoir_idx]['type_carburant']
                    price_per_liter = self.get_fuel_price(fuel_type)
                    
                    if price_per_liter > 0:
                        quantity = amount / price_per_liter
                        info_label.configure(
                            text=f"💡 Quantity: {quantity:.2f} L (@ {price_per_liter:.0f} FCFA/L)"
                        )
                    else:
                        info_label.configure(
                            text="⚠️ Price not configured in Settings"
                        )
                else:
                    info_label.configure(text="")
            except ValueError:
                info_label.configure(text="")
        
        # Lier les changements pour calcul automatique
        amount_entry.bind('<KeyRelease>', calculate_quantity)
        reservoir_menu.configure(command=lambda x: calculate_quantity())
        
        # Spacer
        ctk.CTkFrame(form_frame, fg_color="transparent", height=10).pack()
        
        # Buttons at bottom of dialog (fixed position)
        btn_container = ctk.CTkFrame(dialog, fg_color=self.colors['light'])
        btn_container.pack(fill="x", side="bottom", padx=0, pady=0)
        
        btn_frame = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)
        
        def save_sale():
            try:
                if not pompiste_info:
                    messagebox.showerror("Error", "No attendant scheduled for this period.\nPlease add shift in Employee Management first.")
                    return
                
                if not amount_entry.get():
                    messagebox.showerror("Error", "Please enter the total amount")
                    return
                
                reservoir_idx = reservoir_names.index(reservoir_var.get())
                fuel_type = reservoirs[reservoir_idx]['type_carburant']
                price_per_liter = self.get_fuel_price(fuel_type)
                
                if price_per_liter <= 0:
                    messagebox.showerror("Error", "Fuel price not configured.\nPlease set prices in Settings first.")
                    return
                
                amount = float(amount_entry.get())
                quantity = amount / price_per_liter
                
                # Déterminer les heures de début et fin selon la période
                if auto_period == "matin":
                    heure_debut, heure_fin = "06:00", "14:00"
                elif auto_period == "soir":
                    heure_debut, heure_fin = "14:00", "22:00"
                else:
                    heure_debut, heure_fin = "22:00", "06:00"
                
                self.db.enregistrer_vente(
                    reservoirs[reservoir_idx]['id'],
                    pompiste_info['id'],
                    current_date,
                    auto_period,
                    quantity,
                    amount,
                    heure_debut,
                    heure_fin
                )
                
                messagebox.showinfo(
                    "Success", 
                    f"Sale recorded successfully!\n\n"
                    f"Attendant: {pompiste_info['prenom']} {pompiste_info['nom']}\n"
                    f"Quantity: {quantity:.2f} L\n"
                    f"Amount: {amount:.2f} FCFA"
                )
                dialog.destroy()
                self.load_sales()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save",
            command=save_sale,
            width=140,
            height=40,
            fg_color=self.colors['success'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=140,
            height=40,
            fg_color=self.colors['danger'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=5)
    
    def get_fuel_price(self, fuel_type: str) -> float:
        """
        Récupère le prix du carburant depuis les settings
        
        Args:
            fuel_type (str): Type de carburant (Gasoline, Diesel, Premium)
            
        Returns:
            float: Prix par litre
        """
        try:
            settings_file = 'data/settings.json'
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return float(settings.get('fuel_prices', {}).get(fuel_type, 0))
            return 0
        except Exception as e:
            print(f"Erreur lecture settings: {e}")
            return 0
    
    def get_pompiste_en_service(self, date: str, periode: str, heure: str) -> Dict:
        """
        Trouve le pompiste en service pour une date, période et heure données
        
        Args:
            date (str): Date au format YYYY-MM-DD
            periode (str): Période (matin, soir, nuit)
            heure (str): Heure au format HH:MM
            
        Returns:
            Dict: Informations du pompiste ou None
        """
        try:
            # Obtenir le jour de la semaine
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            jour_semaine = date_obj.strftime('%A')  # Monday, Tuesday, etc.
            
            # Chercher dans le planning
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, po.prenom, po.nom
                FROM planning p
                JOIN pompistes po ON p.pompiste_id = po.id
                WHERE p.jour_semaine = ? 
                AND p.periode = ?
                AND po.statut = 'actif'
                ORDER BY p.date DESC
                LIMIT 1
            ''', (jour_semaine, periode))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Erreur recherche pompiste: {e}")
            return None
    
    def show_loss_analysis(self):
        """
        Affiche l'analyse des pertes
        """
        date = self.date_entry.get()
        reservoirs = self.db.obtenir_reservoirs()
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Loss Analysis")
        dialog.geometry("700x600")
        dialog.transient(self)
        
        title = ctk.CTkLabel(
            dialog,
            text=f"Loss Analysis - {date}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(dialog, fg_color=self.colors['light'])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        for reservoir in reservoirs:
            analysis = self.db.calculer_pertes(reservoir['id'], date)
            
            card = ctk.CTkFrame(scroll, fg_color=self.colors['white'])
            card.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(
                card,
                text=f"{reservoir['nom']} - {reservoir['type_carburant']}",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=10)
            
            if 'erreur' in analysis:
                ctk.CTkLabel(
                    card,
                    text=analysis['erreur'],
                    font=ctk.CTkFont(size=13),
                    text_color=self.colors['danger']
                ).pack(pady=10)
            else:
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(fill="x", padx=20, pady=10)
                
                info_text = f"""
                Starting Quantity: {analysis['quantite_debut']:,.0f} L
                Quantity Sold: {analysis['quantite_vendue']:,.0f} L
                Theoretical Remaining: {analysis['quantite_theorique']:,.0f} L
                Total Revenue: {analysis['montant_total']:,.0f} FCFA
                Unit Price: {analysis['prix_unitaire']:.0f} FCFA/L
                """
                
                ctk.CTkLabel(
                    info_frame,
                    text=info_text,
                    font=ctk.CTkFont(size=13),
                    justify="left"
                ).pack(anchor="w")
        
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            width=150,
            fg_color=self.colors['primary']
        ).pack(pady=20)

    def check_stock_availability(self, reservoir_id: int, quantity_to_sell: float) -> Dict:
        """
        Vérifie la disponibilité du stock avant une vente
        
        Args:
            reservoir_id (int): ID du réservoir
            quantity_to_sell (float): Quantité à vendre
            
        Returns:
            Dict: Résultat avec disponibilité et message
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Obtenir le niveau actuel
            niveau = self.db.obtenir_niveau_quotidien(reservoir_id, today)
            if not niveau:
                return {
                    'available': False,
                    'message': 'No daily level recorded for today'
                }
            
            # Calculer la quantité restante
            quantite_restante = self.calculate_remaining_quantity(reservoir_id, today)
            
            # Vérifier si la vente est possible
            nouvelle_quantite = quantite_restante - quantity_to_sell
            
            if nouvelle_quantite < 0:
                return {
                    'available': False,
                    'message': f'Insufficient stock. Available: {quantite_restante:.1f}L, Requested: {quantity_to_sell:.1f}L'
                }
            elif nouvelle_quantite < 100:
                return {
                    'available': True,
                    'message': f'⚠️ Warning: After this sale, only {nouvelle_quantite:.1f}L will remain (below 100L threshold)',
                    'warning': True
                }
            else:
                return {
                    'available': True,
                    'message': f'Stock sufficient: {quantite_restante:.1f}L available',
                    'warning': False
                }
                
        except Exception as e:
            return {
                'available': False,
                'message': f'Error checking stock: {str(e)}'
            }

    def calculate_remaining_quantity(self, reservoir_id: int, date: str) -> float:
        """
        Calcule la quantité restante dans un réservoir
        
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