# [file name]: enhanced_dashboard.py
# [file content begin]
"""
Dashboard Amélioré avec Graphiques et Analytics en Temps Réel
"""

import customtkinter as ctk
from database.db_manager import DatabaseManager
from analytics_engine import AnalyticsEngine
from datetime import datetime, timedelta
from typing import Dict
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')

class EnhancedDashboard(ctk.CTkFrame):
    """
    Dashboard amélioré avec analytics et graphiques
    
    Attributes:
        colors (Dict): Dictionnaire des couleurs
        db (DatabaseManager): Gestionnaire de base de données
        analytics (AnalyticsEngine): Moteur d'analytics
        chart_canvases (dict): Stocke les canvas des graphiques pour les supprimer
    """
    
    def __init__(self, parent, colors: Dict):
        """
        Initialise le dashboard amélioré
        
        Args:
            parent: Widget parent
            colors (Dict): Dictionnaire des couleurs
        """
        super().__init__(parent, fg_color=colors['light'])
        self.colors = colors
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine()
        self.chart_canvases = {}  # Pour stocker les références aux canvas
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_data()
        
        # Auto-refresh toutes les 30 secondes
        self.after(30000, self.auto_refresh)
    
    def create_widgets(self):
        """Crée tous les widgets du dashboard"""
        # Header avec heure en temps réel
        header_frame = ctk.CTkFrame(self, fg_color=self.colors['dark'], height=100)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo et titre
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        ctk.CTkLabel(
            title_container,
            text="📊",
            font=ctk.CTkFont(size=32)
        ).pack(side="left", padx=(0, 15))
        
        title_text = ctk.CTkFrame(title_container, fg_color="transparent")
        title_text.pack(side="left")
        
        ctk.CTkLabel(
            title_text,
            text="DASHBOARD ANALYTICS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['warning']
        ).pack(anchor="w")
        
        self.time_label = ctk.CTkLabel(
            title_text,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.time_label.pack(anchor="w")
        self.update_time()
        
        # Boutons d'action
        action_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_container.grid(row=0, column=1, sticky="e", padx=30, pady=20)
        
        ctk.CTkButton(
            action_container,
            text="🔄 Refresh",
            command=self.load_data,
            width=100,
            height=35,
            fg_color=self.colors['primary']
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            action_container,
            text="📊 Analyze",
            command=self.show_analytics_dialog,
            width=100,
            height=35,
            fg_color=self.colors['success']
        ).pack(side="right", padx=5)
        
        # Content avec scroll
        content = ctk.CTkScrollableFrame(self, fg_color=self.colors['light'])
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Section 1: KPIs Principaux
        kpi_frame = ctk.CTkFrame(content, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 20))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.kpi_sales = self.create_kpi_card(kpi_frame, "💰", "Ventes Totales", "0 FCFA", self.colors['success'], 0)
        self.kpi_volume = self.create_kpi_card(kpi_frame, "⛽", "Volume Total Vendu", "0 L", self.colors['primary'], 1)
        self.kpi_losses = self.create_kpi_card(kpi_frame, "⚠️", "Pertes Totales", "0 L", self.colors['danger'], 2)
        self.kpi_employees = self.create_kpi_card(kpi_frame, "👥", "Employés Actifs", "0", self.colors['warning'], 3)
        
        # Section 2: Graphiques
        charts_container = ctk.CTkFrame(content, fg_color="transparent")
        charts_container.pack(fill="both", expand=True, pady=20)
        charts_container.grid_columnconfigure((0, 1), weight=1)
        charts_container.grid_rowconfigure((0, 1), weight=1)
        
        # Chart 1: Ventes par type de carburant
        self.sales_chart_frame = ctk.CTkFrame(charts_container, fg_color=self.colors['white'], corner_radius=15)
        self.sales_chart_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            self.sales_chart_frame,
            text="📈 Ventes par Type de Carburant",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Chart 2: Évolution mensuelle
        self.weekly_chart_frame = ctk.CTkFrame(charts_container, fg_color=self.colors['white'], corner_radius=15)
        self.weekly_chart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            self.weekly_chart_frame,
            text="📊 Évolution Mensuelle",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Chart 3: Niveaux de stock
        self.stock_chart_frame = ctk.CTkFrame(charts_container, fg_color=self.colors['white'], corner_radius=15)
        self.stock_chart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            self.stock_chart_frame,
            text="⛽ Niveaux de Stock Actuels",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Chart 4: Performance pompistes
        self.performance_chart_frame = ctk.CTkFrame(charts_container, fg_color=self.colors['white'], corner_radius=15)
        self.performance_chart_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            self.performance_chart_frame,
            text="🏆 Top Performers (Tous Temps)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Section 3: Alertes et Prédictions
        alerts_frame = ctk.CTkFrame(content, fg_color=self.colors['white'], corner_radius=15)
        alerts_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            alerts_frame,
            text="🔔 Alertes et Prédictions",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15, padx=20, anchor="w")
        
        self.alerts_container = ctk.CTkScrollableFrame(alerts_frame, fg_color="transparent", height=200)
        self.alerts_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_kpi_card(self, parent, icon: str, title: str, value: str, color: str, col: int) -> Dict:
        """
        Crée une carte KPI animée
        
        Args:
            parent: Widget parent
            icon (str): Emoji icône
            title (str): Titre
            value (str): Valeur
            color (str): Couleur
            col (int): Colonne
            
        Returns:
            Dict: Références aux labels
        """
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15, height=120)
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(15, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        title_label.pack()
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=(5, 15))
        
        return {
            'card': card,
            'icon': icon_label,
            'title': title_label,
            'value': value_label
        }
    
    def load_data(self):
        """Charge toutes les données du dashboard"""
        # KPIs - Toutes les données historiques
        self.load_kpis()
        
        # Graphiques
        self.load_sales_chart()
        self.load_monthly_chart()
        self.load_stock_chart()
        self.load_performance_chart()
        
        # Alertes
        self.load_alerts()
    
    def load_kpis(self):
        """
        Charge les KPIs avec toutes les données historiques
        """
        # Obtenir toutes les ventes
        all_ventes = self.obtenir_toutes_ventes()
        total_ventes = sum(v['montant_total'] for v in all_ventes)
        total_volume = sum(v['quantite_vendue'] for v in all_ventes)
        
        # Calculer les pertes totales
        total_pertes = self.calculer_pertes_totales()
        
        # Employés actifs
        pompistes = self.db.obtenir_pompistes()
        
        # Mise à jour
        self.kpi_sales['value'].configure(text=f"{total_ventes:,.0f} FCFA")
        self.kpi_volume['value'].configure(text=f"{total_volume:,.0f} L")
        self.kpi_losses['value'].configure(text=f"{total_pertes:.1f} L")
        self.kpi_employees['value'].configure(text=str(len(pompistes)))
    
    def obtenir_toutes_ventes(self) -> list[Dict]:
        """
        Récupère toutes les ventes de la base de données
        
        Returns:
            List[Dict]: Liste de toutes les ventes
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ventes
        ''')
        
        ventes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return ventes
    
    def calculer_pertes_totales(self) -> float:
        """
        Calcule les pertes totales depuis le début
        
        Returns:
            float: Pertes totales en litres
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Obtenir toutes les dates uniques avec des ventes
        cursor.execute('SELECT DISTINCT date FROM ventes ORDER BY date')
        dates = [row['date'] for row in cursor.fetchall()]
        
        total_pertes = 0.0
        
        for date in dates:
            # Pour chaque date, calculer les pertes
            pertes_date = self.analytics.calculer_pertes_automatiques(date)
            total_pertes += pertes_date.get('pertes_totales_litres', 0)
        
        conn.close()
        return total_pertes
    
    def load_sales_chart(self):
        """Charge le graphique des ventes par type de carburant"""
        all_ventes = self.obtenir_toutes_ventes()
        
        # Agréger par type de carburant
        ventes_par_type = {}
        for vente in all_ventes:
            # Obtenir le type de carburant du réservoir
            reservoir = self.db.obtenir_reservoir(vente['reservoir_id'])
            if reservoir:
                type_carb = reservoir['type_carburant']
                if type_carb not in ventes_par_type:
                    ventes_par_type[type_carb] = 0
                ventes_par_type[type_carb] += vente['montant_total']
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#FFFFFF')
        
        types = list(ventes_par_type.keys())
        values = list(ventes_par_type.values())
        colors_bar = ['#FF9800', '#1976D2', '#4CAF50', '#F44336', '#9C27B0']
        
        if types and values:
            bars = ax.bar(types, values, color=colors_bar[:len(types)], alpha=0.8)
            ax.set_ylabel('Montant (FCFA)', fontsize=10)
            ax.set_title('', fontsize=12, weight='bold')
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:,.0f}',
                       ha='center', va='bottom', fontsize=9)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée de vente', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
        
        plt.tight_layout()
        
        # Intégrer dans le frame
        self._embed_chart(fig, self.sales_chart_frame, 'sales')
    
    def load_monthly_chart(self):
        """Charge le graphique d'évolution mensuelle"""
        all_ventes = self.obtenir_toutes_ventes()
        
        if not all_ventes:
            # Créer un graphique vide
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, 'Aucune donnée de vente', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            plt.tight_layout()
            self._embed_chart(fig, self.weekly_chart_frame, 'monthly')
            return
        
        # Agréger par mois
        ventes_par_mois = {}
        for vente in all_ventes:
            date_vente = datetime.strptime(vente['date'], '%Y-%m-%d')
            mois_cle = date_vente.strftime('%Y-%m')
            if mois_cle not in ventes_par_mois:
                ventes_par_mois[mois_cle] = 0
            ventes_par_mois[mois_cle] += vente['montant_total']
        
        # Trier par mois
        mois_tries = sorted(ventes_par_mois.keys())
        valeurs_triees = [ventes_par_mois[mois] for mois in mois_tries]
        
        # Formater les labels de mois
        labels_mois = [datetime.strptime(mois, '%Y-%m').strftime('%b %Y') for mois in mois_tries]
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#FFFFFF')
        
        ax.plot(labels_mois, valeurs_triees, marker='o', linewidth=2, color='#4CAF50', markersize=8)
        ax.fill_between(range(len(labels_mois)), valeurs_triees, alpha=0.3, color='#4CAF50')
        ax.set_ylabel('Ventes (FCFA)', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45, fontsize=8)
        plt.tight_layout()
        
        self._embed_chart(fig, self.weekly_chart_frame, 'monthly')
    
    def load_stock_chart(self):
        """Charge le graphique des niveaux de stock"""
        reservoirs = self.db.obtenir_reservoirs()
        today = datetime.now().strftime('%Y-%m-%d')
        
        names = []
        percentages = []
        colors_stock = []
        
        for reservoir in reservoirs:
            niveau = self.db.obtenir_niveau_quotidien(reservoir['id'], today)
            
            if niveau:
                quantite = niveau['quantite_debut'] + niveau['quantite_entree']
                pct = (quantite / reservoir['capacite_max']) * 100
            else:
                pct = 0
            
            names.append(reservoir['nom'])
            percentages.append(pct)
            
            # Couleur selon niveau
            if pct < 20:
                colors_stock.append('#F44336')
            elif pct < 50:
                colors_stock.append('#FF9800')
            else:
                colors_stock.append('#4CAF50')
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#FFFFFF')
        
        if names and percentages:
            bars = ax.barh(names, percentages, color=colors_stock, alpha=0.8)
            ax.set_xlabel('Niveau (%)', fontsize=10)
            ax.set_xlim(0, 100)
            
            # Ajouter les pourcentages
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                       f'{width:.0f}%',
                       ha='left', va='center', fontsize=9)
        else:
            ax.text(0.5, 0.5, 'Aucun réservoir configuré', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
        
        plt.tight_layout()
        
        self._embed_chart(fig, self.stock_chart_frame, 'stock')
    
    def load_performance_chart(self):
        """Charge le graphique de performance des pompistes (tous temps)"""
        all_ventes = self.obtenir_toutes_ventes()
        
        if not all_ventes:
            # Créer un graphique vide
            fig, ax = plt.subplots(figsize=(5, 3))
            fig.patch.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, 'Aucune donnée de performance', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            plt.tight_layout()
            self._embed_chart(fig, self.performance_chart_frame, 'performance')
            return
        
        # Agréger les ventes par pompiste
        performance_pompistes = {}
        for vente in all_ventes:
            pompiste_id = vente['pompiste_id']
            if pompiste_id not in performance_pompistes:
                # Obtenir les infos du pompiste
                pompiste_info = self.obtenir_info_pompiste(pompiste_id)
                nom_complet = f"{pompiste_info.get('prenom', '')} {pompiste_info.get('nom', '')}".strip()
                performance_pompistes[pompiste_id] = {
                    'nom_complet': nom_complet,
                    'total_montant': 0
                }
            performance_pompistes[pompiste_id]['total_montant'] += vente['montant_total']
        
        # Trier par performance
        top_performers = sorted(performance_pompistes.values(), 
                               key=lambda x: x['total_montant'], reverse=True)[:5]
        
        if not top_performers:
            return
        
        names = [p['nom_complet'].split()[0] if p['nom_complet'] else f"Pompiste {i+1}" 
                for i, p in enumerate(top_performers)]
        amounts = [p['total_montant'] for p in top_performers]
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#FFFFFF')
        
        colors_perf = ['#FFD700', '#C0C0C0', '#CD7F32', '#1976D2', '#1976D2']
        bars = ax.bar(names, amounts, color=colors_perf[:len(names)], alpha=0.8)
        ax.set_ylabel('Ventes (FCFA)', fontsize=10)
        
        # Ajouter les valeurs
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=9)
        
        plt.xticks(rotation=45, fontsize=9)
        plt.tight_layout()
        
        self._embed_chart(fig, self.performance_chart_frame, 'performance')
    
    def obtenir_info_pompiste(self, pompiste_id: int) -> Dict:
        """
        Récupère les informations d'un pompiste
        
        Args:
            pompiste_id (int): ID du pompiste
            
        Returns:
            Dict: Informations du pompiste
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pompistes WHERE id = ?', (pompiste_id,))
        pompiste = cursor.fetchone()
        conn.close()
        
        return dict(pompiste) if pompiste else {}
    
    def load_alerts(self):
        """Charge les alertes et prédictions"""
        for widget in self.alerts_container.winfo_children():
            widget.destroy()
        
        # Alertes de pertes totales
        total_pertes = self.calculer_pertes_totales()
        if total_pertes > 0:
            self.create_alert_card(
                f"Pertes totales détectées: {total_pertes:.1f} L",
                'warning'
            )
        
        # Prédictions de stock
        reservoirs = self.db.obtenir_reservoirs()
        for reservoir in reservoirs:
            prediction = self.analytics.predire_stock(reservoir['id'], 7)
            
            if 'jours_restants' in prediction:
                if prediction['jours_restants'] < 7:
                    self.create_alert_card(
                        f"{reservoir['nom']}: {prediction['recommandation']} "
                        f"(~{prediction['jours_restants']} jours restants)",
                        'warning' if prediction['jours_restants'] >= 3 else 'danger'
                    )
        
        # Alertes BDD
        alertes_db = self.db.obtenir_alertes_non_lues()
        for alerte in alertes_db[:5]:
            self.create_alert_card(alerte['message'], 'info')
        
        # Si aucune alerte
        if not self.alerts_container.winfo_children():
            self.create_alert_card("Aucune alerte - Toutes les opérations sont normales", 'info')
    
    def create_alert_card(self, message: str, alert_type: str):
        """
        Crée une carte d'alerte
        
        Args:
            message (str): Message
            alert_type (str): Type (danger, warning, info)
        """
        colors_alert = {
            'danger': self.colors['danger'],
            'warning': self.colors['warning'],
            'info': self.colors['primary']
        }
        
        icons = {
            'danger': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        card = ctk.CTkFrame(
            self.alerts_container,
            fg_color=colors_alert.get(alert_type, self.colors['primary']),
            corner_radius=10
        )
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            card,
            text=f"{icons.get(alert_type, '•')} {message}",
            font=ctk.CTkFont(size=13),
            text_color="white",
            anchor="w"
        ).pack(pady=10, padx=15, fill="x")
    
    def _embed_chart(self, fig, parent_frame, chart_key: str):
        """
        Intègre un graphique matplotlib dans un frame
        
        Args:
            fig: Figure matplotlib
            parent_frame: Frame parent
            chart_key (str): Clé pour identifier le graphique
        """
        # Supprimer ancien canvas si existant
        if chart_key in self.chart_canvases:
            old_canvas = self.chart_canvases[chart_key]
            if old_canvas and old_canvas.get_tk_widget().winfo_exists():
                old_canvas.get_tk_widget().destroy()
        
        # Supprimer aussi les widgets matplotlib existants
        for widget in parent_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg) or hasattr(widget, '_tkcanvas'):
                widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Stocker la référence
        self.chart_canvases[chart_key] = canvas
        
        plt.close(fig)
    
    def update_time(self):
        """Met à jour l'heure affichée"""
        try:
            now = datetime.now()
            time_str = now.strftime('%A %d %B %Y - %H:%M:%S')
            if self.time_label.winfo_exists():
                self.time_label.configure(text=time_str)
                self.after(1000, self.update_time)
        except Exception:
            # Ignorer les erreurs si le widget n'existe plus
            pass
    
    def auto_refresh(self):
        """Rafraîchissement automatique"""
        try:
            if self.winfo_exists():
                self.load_data()
                self.after(30000, self.auto_refresh)
        except Exception:
            # Ignorer les erreurs si le widget n'existe plus
            pass
    
    def show_analytics_dialog(self):
        """Affiche une fenêtre d'analytics détaillés"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Analytics Détaillés")
        dialog.geometry("900x700")
        dialog.transient(self)
        dialog.grab_set()  # Rend la fenêtre modale
        
        # Obtenir toutes les données
        all_ventes = self.obtenir_toutes_ventes()
        total_ventes = sum(v['montant_total'] for v in all_ventes)
        total_volume = sum(v['quantite_vendue'] for v in all_ventes)
        total_pertes = self.calculer_pertes_totales()
        
        scroll = ctk.CTkScrollableFrame(dialog, fg_color=self.colors['light'])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            scroll,
            text="📊 RAPPORT COMPLET",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)
        
        # Afficher les stats globales
        info_text = f"""
        📈 STATISTIQUES GLOBALES:
        
        💰 VENTES TOTALES:
        - Montant total: {total_ventes:,.0f} FCFA
        - Volume total: {total_volume:,.0f} L
        - Nombre de transactions: {len(all_ventes)}
        
        ⚠️ PERTES TOTALES:
        - Volume perdu: {total_pertes:.1f} L
        
        👥 EMPLOYÉS:
        - Pompistes actifs: {len(self.db.obtenir_pompistes())}
        - Réservoirs: {len(self.db.obtenir_reservoirs())}
        """
        
        ctk.CTkLabel(
            scroll,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(pady=20, padx=20)
        
        ctk.CTkButton(
            dialog,
            text="Fermer",
            command=dialog.destroy,
            width=150,
            fg_color=self.colors['primary']
        ).pack(pady=20)
