"""
Paramètres de l'Application
Interface pour configurer les paramètres généraux
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from tkinter import messagebox, filedialog
from typing import Dict
import json
import os
from PIL import Image, ImageTk

class SettingsFrame(ctk.CTkFrame):
    """
    Frame des paramètres de l'application
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
        settings_file (str): Fichier de configuration
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le frame des paramètres
        
        Args:
            parent: Widget parent
            colors (Dict): Dictionnaire des couleurs
        """
        super().__init__(parent, fg_color=colors['light'])
        self.colors = colors
        self.db = DatabaseManager()
        self.settings_file = 'data/settings.json'
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.load_settings()
        self.create_widgets()
    
    def load_settings(self):
        """
        Charge les paramètres depuis le fichier JSON
        """
        default_settings = {
            'company_name': 'TOTAL Station Service',
            'currency': 'FCFA',
            'fuel_prices': {
                'Gasoline': 650,
                'Diesel': 550,
                'Premium': 750
            },
            'alert_thresholds': {
                'default': 20,
                'critical': 10
            },
            'work_periods': {
                'matin': {'start': '06:00', 'end': '14:00'},
                'soir': {'start': '14:00', 'end': '22:00'},
                'nuit': {'start': '22:00', 'end': '06:00'}
            },
            'notifications': {
                'low_fuel': True,
                'losses': True,
                'daily_summary': True
            },
            'language': 'fr',
            'date_format': '%Y-%m-%d',
            'backup_frequency': 7
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception as e:
            print(f"Erreur chargement settings: {e}")
            self.settings = default_settings
    
    def save_settings(self):
        """
        Sauvegarde les paramètres dans le fichier JSON
        """
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde settings: {e}")
            return False
    
    def create_widgets(self):
        """
        Crée tous les widgets de la page
        """
        # Header
        header = ctk.CTkFrame(self, fg_color=self.colors['dark'], height=100)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=30)
        
        # Save button
        save_btn = ctk.CTkButton(
            header,
            text="💾 Save Settings",
            command=self.save_all_settings,
            width=150,
            height=40,
            fg_color=self.colors['success'],
            hover_color=self.colors['primary'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="right", padx=30)
        
        # Main content
        content = ctk.CTkScrollableFrame(self, fg_color=self.colors['white'])
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Section: General
        self.create_general_section(content)
        
        # Section: Fuel Prices
        self.create_fuel_prices_section(content)
        
        # Section: Alert Thresholds
        self.create_alerts_section(content)
        
        # Section: Work Periods
        self.create_periods_section(content)
        
        # Section: Notifications
        self.create_notifications_section(content)
        
        # Section: Database
        self.create_database_section(content)
        
        # Section: About
        self.create_about_section(content)
    
    def create_general_section(self, parent):
        """
        Crée la section des paramètres généraux
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="🏢 General Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form = ctk.CTkFrame(section, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=20)
        
        # Company name
        ctk.CTkLabel(
            form,
            text="Company Name:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        self.company_entry = ctk.CTkEntry(form, width=400)
        self.company_entry.insert(0, self.settings.get('company_name', ''))
        self.company_entry.pack(anchor="w", pady=(0, 15))
        
        # Currency
        ctk.CTkLabel(
            form,
            text="Currency:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        self.currency_var = ctk.StringVar(value=self.settings.get('currency', 'FCFA'))
        currency_menu = ctk.CTkOptionMenu(
            form,
            values=['FCFA', 'USD', 'EUR', 'XOF'],
            variable=self.currency_var,
            width=200
        )
        currency_menu.pack(anchor="w", pady=(0, 15))
        
        # Language
        ctk.CTkLabel(
            form,
            text="Language:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        self.language_var = ctk.StringVar(value=self.settings.get('language', 'fr'))
        language_menu = ctk.CTkOptionMenu(
            form,
            values=['Français', 'English'],
            variable=self.language_var,
            width=200
        )
        language_menu.pack(anchor="w", pady=(0, 15))
    
    def create_fuel_prices_section(self, parent):
        """
        Crée la section des prix des carburants
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="⛽ Fuel Prices",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form = ctk.CTkFrame(section, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=20)
        
        prices = self.settings.get('fuel_prices', {})
        self.price_entries = {}
        
        for fuel_type in ['Gasoline', 'Diesel', 'Premium']:
            price_frame = ctk.CTkFrame(form, fg_color="transparent")
            price_frame.pack(fill="x", pady=10)
            price_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                price_frame,
                text=f"{fuel_type}:",
                font=ctk.CTkFont(size=14, weight="bold"),
                width=120
            ).grid(row=0, column=0, sticky="w")
            
            entry = ctk.CTkEntry(price_frame, width=150)
            entry.insert(0, str(prices.get(fuel_type, 0)))
            entry.grid(row=0, column=1, sticky="w", padx=10)
            
            ctk.CTkLabel(
                price_frame,
                text=f"{self.settings.get('currency', 'FCFA')}/L",
                font=ctk.CTkFont(size=13)
            ).grid(row=0, column=2, sticky="w")
            
            self.price_entries[fuel_type] = entry
    
    def create_alerts_section(self, parent):
        """
        Crée la section des seuils d'alerte
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="🔔 Alert Thresholds",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form = ctk.CTkFrame(section, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=20)
        
        thresholds = self.settings.get('alert_thresholds', {})
        
        # Default threshold
        ctk.CTkLabel(
            form,
            text="Default Alert Threshold (%):",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        self.default_threshold = ctk.CTkEntry(form, width=150)
        self.default_threshold.insert(0, str(thresholds.get('default', 20)))
        self.default_threshold.pack(anchor="w", pady=(0, 15))
        
        # Critical threshold
        ctk.CTkLabel(
            form,
            text="Critical Alert Threshold (%):",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        self.critical_threshold = ctk.CTkEntry(form, width=150)
        self.critical_threshold.insert(0, str(thresholds.get('critical', 10)))
        self.critical_threshold.pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(
            form,
            text="⚠️ An alert will be triggered when fuel level drops below these percentages",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['warning']
        ).pack(anchor="w", pady=10)
    
    def create_periods_section(self, parent):
        """
        Crée la section des périodes de travail
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="🕐 Work Periods",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form = ctk.CTkFrame(section, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=20)
        
        periods = self.settings.get('work_periods', {})
        self.period_entries = {}
        
        for period_name, icon in [('matin', '☀️'), ('soir', '🌆'), ('nuit', '🌙')]:
            period_data = periods.get(period_name, {})
            
            period_frame = ctk.CTkFrame(form, fg_color=self.colors['white'], corner_radius=10)
            period_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                period_frame,
                text=f"{icon} {period_name.title()}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=10)
            
            time_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
            time_frame.pack(fill="x", padx=20, pady=10)
            time_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Start time
            start_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
            start_frame.grid(row=0, column=0, padx=10)
            
            ctk.CTkLabel(
                start_frame,
                text="Start:",
                font=ctk.CTkFont(size=13)
            ).pack(anchor="w")
            
            start_entry = ctk.CTkEntry(start_frame, width=100, placeholder_text="HH:MM")
            start_entry.insert(0, period_data.get('start', ''))
            start_entry.pack(pady=5)
            
            # End time
            end_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
            end_frame.grid(row=0, column=1, padx=10)
            
            ctk.CTkLabel(
                end_frame,
                text="End:",
                font=ctk.CTkFont(size=13)
            ).pack(anchor="w")
            
            end_entry = ctk.CTkEntry(end_frame, width=100, placeholder_text="HH:MM")
            end_entry.insert(0, period_data.get('end', ''))
            end_entry.pack(pady=5)
            
            self.period_entries[period_name] = {
                'start': start_entry,
                'end': end_entry
            }
    
    def create_notifications_section(self, parent):
        """
        Crée la section des notifications
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="🔔 Notifications",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form = ctk.CTkFrame(section, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=20)
        
        notifications = self.settings.get('notifications', {})
        self.notification_vars = {}
        
        notif_options = [
            ('low_fuel', 'Low Fuel Level Alerts', 'Get notified when fuel levels are low'),
            ('losses', 'Loss Detection Alerts', 'Get notified when losses are detected'),
            ('daily_summary', 'Daily Summary', 'Receive daily summary notifications')
        ]
        
        for key, title, desc in notif_options:
            notif_frame = ctk.CTkFrame(form, fg_color=self.colors['white'], corner_radius=10)
            notif_frame.pack(fill="x", pady=10)
            
            var = ctk.BooleanVar(value=notifications.get(key, True))
            self.notification_vars[key] = var
            
            switch = ctk.CTkSwitch(
                notif_frame,
                text=title,
                variable=var,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            switch.pack(pady=10, padx=20, anchor="w")
            
            ctk.CTkLabel(
                notif_frame,
                text=desc,
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(pady=(0, 10), padx=40, anchor="w")
    
    def create_database_section(self, parent):
        """
        Crée la section de gestion de la base de données
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="💾 Database Management",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form = ctk.CTkFrame(section, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=20)
        
        # Backup frequency
        ctk.CTkLabel(
            form,
            text="Backup Frequency (days):",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        self.backup_freq = ctk.CTkEntry(form, width=150)
        self.backup_freq.insert(0, str(self.settings.get('backup_frequency', 7)))
        self.backup_freq.pack(anchor="w", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="📥 Backup Database",
            command=self.backup_database,
            width=180,
            height=40,
            fg_color=self.colors['success']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📂 Restore Database",
            command=self.restore_database,
            width=180,
            height=40,
            fg_color=self.colors['primary']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear All Data",
            command=self.clear_database,
            width=180,
            height=40,
            fg_color=self.colors['danger']
        ).pack(side="left", padx=5)
    
    def create_about_section(self, parent):
        """
        Crée la section À propos
        
        Args:
            parent: Widget parent
        """
        section = ctk.CTkFrame(parent, fg_color=self.colors['light'], corner_radius=15)
        section.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section,
            text="ℹ️ About",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        info_frame = ctk.CTkFrame(section, fg_color="transparent")
        info_frame.pack(fill="x", padx=40, pady=20)
        
        about_text = """
        Gas Station Management System
        Version: 1.0.0
        
        © 2024 TOTAL Station Service
        All rights reserved.
        
        Developed with Python, CustomTkinter & SQLite
        
        For support and documentation, please refer to the README.md file.
        """
        
        ctk.CTkLabel(
            info_frame,
            text=about_text,
            font=ctk.CTkFont(size=13),
            justify="left"
        ).pack(pady=10)
    
    def save_all_settings(self):
        """
        Sauvegarde tous les paramètres modifiés
        """
        try:
            # General
            self.settings['company_name'] = self.company_entry.get()
            self.settings['currency'] = self.currency_var.get()
            self.settings['language'] = 'fr' if self.language_var.get() == 'Français' else 'en'
            
            # Fuel prices
            for fuel_type, entry in self.price_entries.items():
                self.settings['fuel_prices'][fuel_type] = float(entry.get())
            
            # Thresholds
            self.settings['alert_thresholds']['default'] = float(self.default_threshold.get())
            self.settings['alert_thresholds']['critical'] = float(self.critical_threshold.get())
            
            # Periods
            for period_name, entries in self.period_entries.items():
                self.settings['work_periods'][period_name] = {
                    'start': entries['start'].get(),
                    'end': entries['end'].get()
                }
            
            # Notifications
            for key, var in self.notification_vars.items():
                self.settings['notifications'][key] = var.get()
            
            # Backup frequency
            self.settings['backup_frequency'] = int(self.backup_freq.get())
            
            if self.save_settings():
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save settings")
        
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value entered: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
    
    def backup_database(self):
        """
        Crée une sauvegarde de la base de données
        """
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialfile="station_backup.db"
            )
            
            if filepath:
                import shutil
                shutil.copy2('data/station.db', filepath)
                messagebox.showinfo("Success", f"Database backed up to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_database(self):
        """
        Restaure la base de données depuis une sauvegarde
        """
        if not messagebox.askyesno("Warning", 
            "This will replace your current database. Are you sure?"):
            return
        
        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if filepath:
                import shutil
                shutil.copy2(filepath, 'data/station.db')
                messagebox.showinfo("Success", 
                    "Database restored successfully!\nPlease restart the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def clear_database(self):
        """
        Supprime toutes les données de la base
        """
        if not messagebox.askyesno("Warning", 
            "This will delete ALL data permanently. Are you sure?"):
            return
        
        # Double confirmation
        if not messagebox.askyesno("Final Warning", 
            "This action cannot be undone. Proceed?"):
            return
        
        try:
            os.remove('data/station.db')
            messagebox.showinfo("Success", 
                "Database cleared successfully!\nThe application will reinitialize on next start.")
            # Reinitialize
            self.db.initialize_database()
        except Exception as e:
            messagebox.showerror("Error", f"Clear failed: {str(e)}")