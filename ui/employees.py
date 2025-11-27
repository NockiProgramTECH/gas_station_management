"""
Gestion des employés et du planning
Interface pour gérer les pompistes et leur planning hebdomadaire
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog
from typing import Dict
from PIL import Image, ImageTk
import os
import shutil

class EmployeesFrame(ctk.CTkFrame):
    """
    Frame de gestion des employés
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le frame des employés
        
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
        self.show_employees_list()
    
    def create_widgets(self):
        """
        Crée tous les widgets de la page
        """
        # Header
        header = ctk.CTkFrame(self, fg_color=self.colors['warning'], height=100)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="👥 Employee Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=30)
        
        # Add employee button
        add_btn = ctk.CTkButton(
            header,
            text="+ New Employee",
            command=self.show_add_employee_dialog,
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
        
        self.tab_list = ctk.CTkButton(
            tab_frame,
            text="Employee List",
            command=self.show_employees_list,
            width=150,
            height=40,
            fg_color=self.colors['primary']
        )
        self.tab_list.pack(side="left", padx=5)
        
        self.tab_schedule = ctk.CTkButton(
            tab_frame,
            text="Weekly Schedule",
            command=self.show_schedule,
            width=150,
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color=self.colors['primary'],
            text_color=self.colors['primary']
        )
        self.tab_schedule.pack(side="left", padx=5)
        
        # Content area
        self.content_area = ctk.CTkScrollableFrame(content, fg_color=self.colors['white'])
        self.content_area.grid(row=1, column=0, sticky="nsew")
    
    def switch_tab(self, tab_name: str):
        """
        Change l'onglet actif
        
        Args:
            tab_name (str): Nom de l'onglet
        """
        if tab_name == "list":
            self.tab_list.configure(
                fg_color=self.colors['primary'],
                text_color="white",
                border_width=0
            )
            self.tab_schedule.configure(
                fg_color="transparent",
                text_color=self.colors['primary'],
                border_width=2
            )
        else:
            self.tab_schedule.configure(
                fg_color=self.colors['primary'],
                text_color="white",
                border_width=0
            )
            self.tab_list.configure(
                fg_color="transparent",
                text_color=self.colors['primary'],
                border_width=2
            )
    
    def show_employees_list(self):
        """
        Affiche la liste des employés
        """
        self.switch_tab("list")
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        pompistes = self.db.obtenir_pompistes()
        
        if not pompistes:
            label = ctk.CTkLabel(
                self.content_area,
                text="No employees registered. Click 'New Employee' to add one.",
                font=ctk.CTkFont(size=16),
                text_color=self.colors['dark']
            )
            label.pack(pady=50)
            return
        
        # Obtenir date et heure actuelles pour déterminer qui est actif
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_hour = now.hour
        current_day = now.strftime('%A')  # Monday, Tuesday, etc.
        
        # Déterminer la période actuelle
        if 6 <= current_hour < 14:
            current_period = "matin"
        elif 14 <= current_hour < 22:
            current_period = "soir"
        else:
            current_period = "nuit"
        
        for pompiste in pompistes:
            # Vérifier si le pompiste est actuellement en service
            is_on_duty = self.check_if_on_duty(pompiste['id'], current_day, current_period)
            
            card = ctk.CTkFrame(
                self.content_area,
                fg_color=self.colors['white'],
                border_width=2,
                border_color=self.colors['light']
            )
            card.pack(fill="x", pady=10, padx=20)
            
            main_container = ctk.CTkFrame(card, fg_color="transparent")
            main_container.pack(fill="x", padx=20, pady=20)
            main_container.grid_columnconfigure(1, weight=1)
            
            # Photo de profil
            photo_frame = ctk.CTkFrame(main_container, fg_color=self.colors['light'], 
                                      width=100, height=100, corner_radius=50)
            photo_frame.grid(row=0, column=0, rowspan=3, padx=20, pady=10)
            photo_frame.grid_propagate(False)
            
            # Charger la photo si elle existe
            photo_path = pompiste.get('photo_path', '')
            if photo_path and os.path.exists(photo_path):
                try:
                    img = Image.open(photo_path)
                    img = img.resize((90, 90), Image.Resampling.LANCZOS)
                    photo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(90, 90))
                    photo_label = ctk.CTkLabel(photo_frame, image=photo_img, text="")
                    photo_label.image = photo_img
                    photo_label.pack(expand=True)
                except Exception as e:
                    print(f"Erreur chargement photo: {e}")
                    ctk.CTkLabel(
                        photo_frame,
                        text="👤",
                        font=ctk.CTkFont(size=48),
                        text_color=self.colors['dark']
                    ).pack(expand=True)
            else:
                ctk.CTkLabel(
                    photo_frame,
                    text="👤",
                    font=ctk.CTkFont(size=48),
                    text_color=self.colors['dark']
                ).pack(expand=True)
            
            # Employee info
            info_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=20)
            info_frame.grid_columnconfigure(0, weight=1)
            
            # Name
            name_label = ctk.CTkLabel(
                info_frame,
                text=f"{pompiste['prenom']} {pompiste['nom']}",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=self.colors['dark']
            )
            name_label.grid(row=0, column=0, sticky="w", pady=5)
            
            # Status badge - ACTIF si en service, PASSIF sinon
            if is_on_duty:
                status_text = "🟢 ACTIF"
                status_color = self.colors['success']
            else:
                status_text = "⚫ PASSIF"
                status_color = self.colors['dark']
            
            status_badge = ctk.CTkLabel(
                info_frame,
                text=status_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                fg_color=status_color,
                corner_radius=5,
                padx=10,
                pady=5
            )
            status_badge.grid(row=0, column=1, padx=10)
            
            # Contact info
            if pompiste['telephone']:
                phone_label = ctk.CTkLabel(
                    info_frame,
                    text=f"📞 {pompiste['telephone']}",
                    font=ctk.CTkFont(size=13),
                    text_color=self.colors['dark']
                )
                phone_label.grid(row=1, column=0, sticky="w", pady=2)
            
            if pompiste['email']:
                email_label = ctk.CTkLabel(
                    info_frame,
                    text=f"✉️ {pompiste['email']}",
                    font=ctk.CTkFont(size=13),
                    text_color=self.colors['dark']
                )
                email_label.grid(row=2, column=0, sticky="w", pady=2)
    
    def check_if_on_duty(self, pompiste_id: int, jour: str, periode: str) -> bool:
        """
        Vérifie si un pompiste est en service pour un jour et une période donnés
        
        Args:
            pompiste_id (int): ID du pompiste
            jour (str): Jour de la semaine (Monday, Tuesday, etc.)
            periode (str): Période (matin, soir, nuit)
            
        Returns:
            bool: True si en service, False sinon
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM planning
                WHERE pompiste_id = ?
                AND jour_semaine = ?
                AND periode = ?
            ''', (pompiste_id, jour, periode))
            
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] > 0 if result else False
        except Exception as e:
            print(f"Erreur vérification service: {e}")
            return False
    
    def show_schedule(self):
        """
        Affiche le planning hebdomadaire
        """
        self.switch_tab("schedule")
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Week selector
        week_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        week_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            week_frame,
            text="Week Starting:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        self.week_entry = ctk.CTkEntry(week_frame, width=150)
        self.week_entry.insert(0, week_start.strftime('%Y-%m-%d'))
        self.week_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(
            week_frame,
            text="Load",
            width=100,
            command=self.load_weekly_schedule,
            fg_color=self.colors['primary']
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            week_frame,
            text="+ Add Shift",
            width=120,
            command=self.show_add_shift_dialog,
            fg_color=self.colors['success']
        ).pack(side="right", padx=10)
        
        # Schedule table
        self.schedule_container = ctk.CTkFrame(self.content_area, fg_color=self.colors['white'])
        self.schedule_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.load_weekly_schedule()
    
    def load_weekly_schedule(self):
        """
        Charge le planning de la semaine
        """
        for widget in self.schedule_container.winfo_children():
            widget.destroy()
        
        date_str = self.week_entry.get()
        planning = self.db.obtenir_planning_semaine(date_str)
        
        # Days of week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        periods = ['matin', 'soir', 'nuit']
        
        # Create grid
        for i, day in enumerate(days):
            day_label = ctk.CTkLabel(
                self.schedule_container,
                text=day,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=self.colors['primary'],
                text_color="white",
                corner_radius=5
            )
            day_label.grid(row=0, column=i+1, padx=5, pady=5, sticky="ew")
        
        for i, period in enumerate(periods):
            period_icons = {'matin': '☀️', 'soir': '🌆', 'nuit': '🌙'}
            period_label = ctk.CTkLabel(
                self.schedule_container,
                text=f"{period_icons[period]} {period.title()}",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors['light'],
                corner_radius=5
            )
            period_label.grid(row=i+1, column=0, padx=5, pady=5, sticky="ew")
        
        # Fill schedule
        for shift in planning:
            day_idx = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(shift['jour_semaine'])
            period_idx = periods.index(shift['periode'])
            
            shift_label = ctk.CTkLabel(
                self.schedule_container,
                text=f"{shift['prenom']} {shift['nom']}\n{shift['heure_debut']}-{shift['heure_fin']}",
                font=ctk.CTkFont(size=11),
                fg_color=self.colors['white'],
                text_color=self.colors['dark'],
                corner_radius=5,
                justify="center"
            )
            shift_label.grid(row=period_idx+1, column=day_idx+1, padx=5, pady=5, sticky="nsew")
    
    def show_add_employee_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter un employé
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Employee")
        dialog.geometry("500x700")
        dialog.transient(self)
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color=self.colors['warning'], height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="👤 New Employee",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title.pack(pady=15)
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=self.colors['light'])
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        content_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        content_frame.pack(fill="both", padx=30, pady=20)
        
        # Photo preview
        self.selected_photo_path = None
        
        photo_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        photo_container.pack(pady=10)
        
        photo_frame = ctk.CTkFrame(photo_container, fg_color=self.colors['light'], 
                                  width=120, height=120, corner_radius=60)
        photo_frame.pack()
        photo_frame.pack_propagate(False)
        
        self.photo_display = ctk.CTkLabel(
            photo_frame,
            text="👤",
            font=ctk.CTkFont(size=64),
            text_color=self.colors['dark']
        )
        self.photo_display.pack(expand=True)
        
        # Upload button
        upload_btn = ctk.CTkButton(
            content_frame,
            text="📷 Upload Photo",
            command=lambda: self.select_photo(dialog),
            width=150,
            height=35,
            fg_color=self.colors['primary']
        )
        upload_btn.pack(pady=10)
        
        form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_frame.pack(fill="both", pady=10)
        
        # First name
        ctk.CTkLabel(form_frame, text="First Name:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        prenom_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., John", height=35)
        prenom_entry.pack(fill="x", pady=(0, 10))
        
        # Last name
        ctk.CTkLabel(form_frame, text="Last Name:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        nom_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Doe", height=35)
        nom_entry.pack(fill="x", pady=(0, 10))
        
        # Phone
        ctk.CTkLabel(form_frame, text="Phone:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        phone_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., +226 XX XX XX XX", height=35)
        phone_entry.pack(fill="x", pady=(0, 10))
        
        # Email
        ctk.CTkLabel(form_frame, text="Email:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        email_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., john.doe@example.com", height=35)
        email_entry.pack(fill="x", pady=(0, 10))
        
        # Spacer
        ctk.CTkFrame(form_frame, fg_color="transparent", height=10).pack()
        
        # Buttons at bottom of dialog (fixed position)
        btn_container = ctk.CTkFrame(dialog, fg_color=self.colors['light'])
        btn_container.pack(fill="x", side="bottom", padx=0, pady=0)
        
        btn_frame = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)
        
        def save_employee():
            prenom = prenom_entry.get()
            nom = nom_entry.get()
            phone = phone_entry.get()
            email = email_entry.get()
            
            if not prenom or not nom:
                messagebox.showerror("Error", "Please enter first and last name")
                return
            
            # Copier la photo dans le dossier data/photos
            photo_save_path = ""
            if self.selected_photo_path:
                try:
                    os.makedirs('data/photos', exist_ok=True)
                    filename = f"employee_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                    photo_save_path = f"data/photos/{filename}"
                    shutil.copy2(self.selected_photo_path, photo_save_path)
                except Exception as e:
                    print(f"Erreur copie photo: {e}")
            
            self.db.ajouter_pompiste(nom, prenom, phone, email)
            messagebox.showinfo("Success", "Employee added successfully!")
            dialog.destroy()
            self.show_employees_list()
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save",
            command=save_employee,
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
    
    def select_photo(self, dialog):
        """
        Ouvre un dialogue pour sélectionner une photo
        
        Args:
            dialog: Dialogue parent
        """
        filepath = filedialog.askopenfilename(
            title="Select Employee Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            try:
                self.selected_photo_path = filepath
                # Afficher la prévisualisation
                img = Image.open(filepath)
                img = img.resize((110, 110), Image.Resampling.LANCZOS)
                photo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(110, 110))
                self.photo_display.configure(image=photo_img, text="")
                self.photo_display.image = photo_img
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def show_add_shift_dialog(self):
        """
        Affiche la boîte de dialogue pour ajouter un horaire
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Shift")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color=self.colors['primary'], height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="📅 Schedule Shift",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title.pack(pady=15)
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=self.colors['light'])
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        form_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_frame.pack(fill="both", padx=30, pady=20)
        
        # Employee
        ctk.CTkLabel(form_frame, text="Employee:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        pompistes = self.db.obtenir_pompistes()
        pompiste_names = [f"{p['prenom']} {p['nom']}" for p in pompistes]
        pompiste_var = ctk.StringVar(value=pompiste_names[0] if pompiste_names else "")
        pompiste_menu = ctk.CTkOptionMenu(form_frame, values=pompiste_names, variable=pompiste_var, height=35)
        pompiste_menu.pack(fill="x", pady=(0, 10))
        
        # Date
        ctk.CTkLabel(form_frame, text="Date:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        date_entry = ctk.CTkEntry(form_frame, height=35)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack(fill="x", pady=(0, 10))
        
        # Day of week
        ctk.CTkLabel(form_frame, text="Day of Week:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        day_var = ctk.StringVar(value="Monday")
        day_menu = ctk.CTkOptionMenu(
            form_frame,
            values=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            variable=day_var,
            height=35
        )
        day_menu.pack(fill="x", pady=(0, 10))
        
        # Period
        ctk.CTkLabel(form_frame, text="Period:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        period_var = ctk.StringVar(value="matin")
        period_menu = ctk.CTkOptionMenu(form_frame, values=["matin", "soir", "nuit"], variable=period_var, height=35)
        period_menu.pack(fill="x", pady=(0, 10))
        
        # Time
        ctk.CTkLabel(form_frame, text="Working Hours:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 5))
        time_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=5)
        time_frame.grid_columnconfigure((0, 1), weight=1)
        
        start_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        start_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(start_frame, text="Start:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 3))
        start_entry = ctk.CTkEntry(start_frame, placeholder_text="HH:MM", height=35)
        start_entry.pack(fill="x")
        
        end_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        end_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(end_frame, text="End:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 3))
        end_entry = ctk.CTkEntry(end_frame, placeholder_text="HH:MM", height=35)
        end_entry.pack(fill="x")
        
        # Spacer
        ctk.CTkFrame(form_frame, fg_color="transparent", height=10).pack()
        
        # Buttons at bottom of dialog (fixed position)
        btn_container = ctk.CTkFrame(dialog, fg_color=self.colors['light'])
        btn_container.pack(fill="x", side="bottom", padx=0, pady=0)
        
        btn_frame = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=15)
        
        def save_shift():
            try:
                pompiste_idx = pompiste_names.index(pompiste_var.get())
                
                self.db.ajouter_planning(
                    pompistes[pompiste_idx]['id'],
                    date_entry.get(),
                    day_var.get(),
                    period_var.get(),
                    start_entry.get(),
                    end_entry.get()
                )
                
                messagebox.showinfo("Success", "Shift scheduled successfully!")
                dialog.destroy()
                self.load_weekly_schedule()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save",
            command=save_shift,
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


# Placeholder frames for Reports and Settings
class ReportsFrame(ctk.CTkFrame):
    """Frame pour les rapports"""
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors['light'])
        ctk.CTkLabel(
            self,
            text="📊 Reports & Analytics - Coming Soon",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(expand=True)


class SettingsFrame(ctk.CTkFrame):
    """Frame pour les paramètres"""
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors['light'])
        ctk.CTkLabel(
            self,
            text="⚙️ Settings - Coming Soon",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(expand=True)