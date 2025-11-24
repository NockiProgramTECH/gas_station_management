"""
Interface des Rapports et Analytics
Page pour générer et visualiser les rapports
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from reports.pdf_generator import PDFReportGenerator
from datetime import datetime
from tkinter import messagebox, filedialog
from typing import Dict
import os

class ReportsFrame(ctk.CTkFrame):
    """
    Frame de génération de rapports
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
        pdf_gen (PDFReportGenerator): Générateur de PDF
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le frame des rapports
        
        Args:
            parent: Widget parent
            colors (Dict): Dictionnaire des couleurs
        """
        super().__init__(parent, fg_color=colors['white'])
        self.colors = colors
        self.db = DatabaseManager()
        self.pdf_gen = PDFReportGenerator()
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
    
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
            text="📊 Reports & Analytics",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=30)
        
        # Main content
        content = ctk.CTkScrollableFrame(self, fg_color=self.colors['light'])
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Section: Rapports individuels
        section1 = ctk.CTkFrame(content, fg_color=self.colors['white'], corner_radius=15)
        section1.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section1,
            text="📄 Rapport Individuel Pompiste",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form1 = ctk.CTkFrame(section1, fg_color="transparent")
        form1.pack(fill="x", padx=40, pady=20)
        
        # Employee selection
        ctk.CTkLabel(
            form1,
            text="Sélectionner un pompiste:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(10, 5))
        
        pompistes = self.db.obtenir_pompistes()
        pompiste_names = [f"{p['prenom']} {p['nom']}" for p in pompistes]
        self.pompiste_var = ctk.StringVar(value=pompiste_names[0] if pompiste_names else "Aucun employé")
        
        pompiste_menu = ctk.CTkOptionMenu(
            form1,
            values=pompiste_names if pompiste_names else ["Aucun employé"],
            variable=self.pompiste_var,
            width=300
        )
        pompiste_menu.pack(anchor="w", pady=(0, 15))
        
        # Month selection
        date_frame = ctk.CTkFrame(form1, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)
        date_frame.grid_columnconfigure((0, 1), weight=1)
        
        month_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        month_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        ctk.CTkLabel(
            month_frame,
            text="Mois:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        months = [f"{i:02d}" for i in range(1, 13)]
        current_month = datetime.now().strftime('%m')
        self.month_var = ctk.StringVar(value=current_month)
        
        month_menu = ctk.CTkOptionMenu(
            month_frame,
            values=months,
            variable=self.month_var,
            width=150
        )
        month_menu.pack(anchor="w")
        
        year_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        year_frame.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(
            year_frame,
            text="Année:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 1)]
        self.year_var = ctk.StringVar(value=str(current_year))
        
        year_menu = ctk.CTkOptionMenu(
            year_frame,
            values=years,
            variable=self.year_var,
            width=150
        )
        year_menu.pack(anchor="w")
        
        # Generate button
        btn_frame = ctk.CTkFrame(form1, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="📥 Générer Rapport PDF",
            command=self.generer_rapport_individuel,
            width=200,
            height=40,
            fg_color=self.colors['success'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="👁️ Prévisualiser",
            command=self.previsualiser_rapport_individuel,
            width=150,
            height=40,
            fg_color=self.colors['primary'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        # Separator
        separator = ctk.CTkFrame(content, fg_color=self.colors['dark'], height=2)
        separator.pack(fill="x", pady=20, padx=20)
        
        # Section: Rapport global
        section2 = ctk.CTkFrame(content, fg_color=self.colors['white'], corner_radius=15)
        section2.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section2,
            text="📊 Rapport Global de la Station",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        form2 = ctk.CTkFrame(section2, fg_color="transparent")
        form2.pack(fill="x", padx=40, pady=20)
        
        # Period selection
        period_frame = ctk.CTkFrame(form2, fg_color="transparent")
        period_frame.pack(fill="x", pady=10)
        period_frame.grid_columnconfigure((0, 1), weight=1)
        
        start_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        start_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        ctk.CTkLabel(
            start_frame,
            text="Date de début:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.start_date = ctk.CTkEntry(start_frame, width=200, placeholder_text="YYYY-MM-DD")
        self.start_date.insert(0, datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        self.start_date.pack(anchor="w")
        
        end_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        end_frame.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(
            end_frame,
            text="Date de fin:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.end_date = ctk.CTkEntry(end_frame, width=200, placeholder_text="YYYY-MM-DD")
        self.end_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.end_date.pack(anchor="w")
        
        # Generate button
        ctk.CTkButton(
            form2,
            text="📥 Générer Rapport Global PDF",
            command=self.generer_rapport_global,
            width=250,
            height=40,
            fg_color=self.colors['warning'],
            hover_color=self.colors['dark'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20, anchor="w")
        
        # Section: Statistiques rapides
        section3 = ctk.CTkFrame(content, fg_color=self.colors['white'], corner_radius=15)
        section3.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            section3,
            text="📈 Statistiques Rapides",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        ).pack(pady=20, padx=20, anchor="w")
        
        stats_frame = ctk.CTkFrame(section3, fg_color="transparent")
        stats_frame.pack(fill="x", padx=40, pady=20)
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total sales
        self.create_stat_card(stats_frame, "Ventes Totales", "0 FCFA", self.colors['success'], 0)
        
        # Total volume
        self.create_stat_card(stats_frame, "Volume Total", "0 L", self.colors['primary'], 1)
        
        # Active employees
        pompistes_actifs = len(self.db.obtenir_pompistes())
        self.create_stat_card(stats_frame, "Employés Actifs", str(pompistes_actifs), self.colors['warning'], 2)
    
    def create_stat_card(self, parent, title: str, value: str, color: str, col: int):
        """
        Crée une carte de statistique
        
        Args:
            parent: Widget parent
            title (str): Titre de la statistique
            value (str): Valeur à afficher
            color (str): Couleur de fond
            col (int): Colonne dans le grid
        """
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=100)
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False)
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13),
            text_color="white"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=5)
    
    def generer_rapport_individuel(self):
        """
        Génère un rapport PDF pour un pompiste
        """
        if not self.pompiste_var.get() or self.pompiste_var.get() == "Aucun employé":
            messagebox.showerror("Erreur", "Veuillez sélectionner un employé")
            return
        
        try:
            pompistes = self.db.obtenir_pompistes()
            pompiste_names = [f"{p['prenom']} {p['nom']}" for p in pompistes]
            pompiste_idx = pompiste_names.index(self.pompiste_var.get())
            pompiste_id = pompistes[pompiste_idx]['id']
            
            mois = self.month_var.get()
            annee = self.year_var.get()
            
            # Demander où sauvegarder
            filename = f"rapport_{pompistes[pompiste_idx]['prenom']}_{pompistes[pompiste_idx]['nom']}_{mois}_{annee}.pdf"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=filename
            )
            
            if filepath:
                output_path = self.pdf_gen.generer_rapport_pompiste(
                    pompiste_id, mois, annee, filepath
                )
                
                if output_path:
                    messagebox.showinfo(
                        "Succès",
                        f"Rapport généré avec succès!\n\nFichier: {output_path}"
                    )
                    
                    # Demander si ouvrir le fichier
                    if messagebox.askyesno("Ouvrir le fichier", "Voulez-vous ouvrir le rapport maintenant?"):
                        os.startfile(output_path)
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la génération du rapport")
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération: {str(e)}")
    
    def previsualiser_rapport_individuel(self):
        """
        Prévisualise les données d'un rapport individuel
        """
        if not self.pompiste_var.get() or self.pompiste_var.get() == "Aucun employé":
            messagebox.showerror("Erreur", "Veuillez sélectionner un employé")
            return
        
        # Créer une fenêtre de prévisualisation
        preview = ctk.CTkToplevel(self)
        preview.title("Prévisualisation du Rapport")
        preview.geometry("800x600")
        preview.transient(self)
        
        pompistes = self.db.obtenir_pompistes()
        pompiste_names = [f"{p['prenom']} {p['nom']}" for p in pompistes]
        pompiste_idx = pompiste_names.index(self.pompiste_var.get())
        pompiste_id = pompistes[pompiste_idx]['id']
        
        mois = self.month_var.get()
        annee = self.year_var.get()
        
        # Récupérer les données
        ventes = self.pdf_gen.get_ventes_mois(pompiste_id, mois, annee)
        resume = self.pdf_gen.calculer_resume_ventes(ventes)
        
        # Titre
        ctk.CTkLabel(
            preview,
            text=f"Rapport - {self.pompiste_var.get()}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            preview,
            text=f"Période: {mois}/{annee}",
            font=ctk.CTkFont(size=16)
        ).pack(pady=10)
        
        # Résumé
        scroll = ctk.CTkScrollableFrame(preview, fg_color=self.colors['light'])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = f"""
        Nombre de ventes: {resume['nombre_ventes']}
        Quantité totale: {resume['quantite_totale']:,.0f} L
        Montant total: {resume['montant_total']:,.2f} FCFA
        Heures travaillées: {resume['heures_travaillees']:.1f} h
        
        Ventes Matin: {resume['ventes_matin']:,.2f} FCFA
        Ventes Soir: {resume['ventes_soir']:,.2f} FCFA
        Ventes Nuit: {resume['ventes_nuit']:,.2f} FCFA
        """
        
        ctk.CTkLabel(
            scroll,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(pady=20, padx=20)
        
        # Bouton fermer
        ctk.CTkButton(
            preview,
            text="Fermer",
            command=preview.destroy,
            width=150,
            fg_color=self.colors['danger']
        ).pack(pady=20)
    
    def generer_rapport_global(self):
        """
        Génère un rapport global de la station
        """
        try:
            date_debut = self.start_date.get()
            date_fin = self.end_date.get()
            
            filename = f"rapport_global_{date_debut}_to_{date_fin}.pdf"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=filename
            )
            
            if filepath:
                output_path = self.pdf_gen.generer_rapport_global(
                    date_debut, date_fin, filepath
                )
                
                messagebox.showinfo(
                    "Succès",
                    f"Rapport global généré avec succès!\n\nFichier: {output_path}"
                )
                
                if messagebox.askyesno("Ouvrir le fichier", "Voulez-vous ouvrir le rapport maintenant?"):
                    os.startfile(output_path)
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération: {str(e)}")


class SettingsFrame(ctk.CTkFrame):
    """Frame des paramètres de l'application"""
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le frame des paramètres
        
        Args:
            parent: Widget parent
            colors (Dict): Dictionnaire des couleurs
        """
        super().__init__(parent, fg_color=colors['light'])
        self.colors = colors
        
        # Header
        header = ctk.CTkFrame(self, fg_color=self.colors['dark'], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=30)
        
        # Content
        content = ctk.CTkScrollableFrame(self, fg_color=colors['white'])
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sections
        sections = [
            ("🎨 Appearance", "Configure l'apparence de l'application"),
            ("🔔 Notifications", "Gérer les alertes et notifications"),
            ("💾 Database", "Options de sauvegarde et restauration"),
            ("🔐 Security", "Paramètres de sécurité"),
            ("ℹ️ About", "Informations sur l'application")
        ]
        
        for title, desc in sections:
            card = ctk.CTkFrame(content, fg_color=colors['light'], corner_radius=10)
            card.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=colors['dark']
            ).pack(pady=(15, 5), padx=20, anchor="w")
            
            ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=13),
                text_color=colors['dark']
            ).pack(pady=(0, 15), padx=20, anchor="w")