"""
Générateur de Rapports PDF
Module pour créer des rapports PDF avec graphiques et tableaux
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
from typing import Dict, List
import os

class PDFReportGenerator:
    """
    Classe pour générer des rapports PDF
    
    Attributes:
        db (DatabaseManager): Gestionnaire de base de données
        styles: Styles pour le document
    """
    
    def __init__(self):
        """
        Initialise le générateur de rapports
        """
        self.db = DatabaseManager()
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()
    
    def create_custom_styles(self):
        """
        Crée des styles personnalisés pour les rapports
        """
        # Style pour le titre
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#424242'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generer_rapport_pompiste(self, pompiste_id: int, mois: str, annee: str, 
                                  output_path: str = 'rapports/rapport_pompiste.pdf'):
        """
        Génère un rapport mensuel pour un pompiste
        
        Args:
            pompiste_id (int): ID du pompiste
            mois (str): Mois (format MM)
            annee (str): Année (format YYYY)
            output_path (str): Chemin de sortie du fichier PDF
            
        Returns:
            str: Chemin du fichier généré
        """
        # Créer le dossier s'il n'existe pas
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Créer le document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        
        # Récupérer les informations du pompiste
        pompiste = self.db.obtenir_pompistes()
        pompiste_data = next((p for p in pompiste if p['id'] == pompiste_id), None)
        
        if not pompiste_data:
            return None
        
        # Titre
        titre = f"RAPPORT MENSUEL - {pompiste_data['prenom']} {pompiste_data['nom']}"
        elements.append(Paragraph(titre, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informations générales
        info_text = f"""
        <b>Période:</b> {mois}/{annee}<br/>
        <b>Employé:</b> {pompiste_data['prenom']} {pompiste_data['nom']}<br/>
        <b>Téléphone:</b> {pompiste_data['telephone']}<br/>
        <b>Date du rapport:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        elements.append(Paragraph(info_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Récupérer les ventes du mois
        ventes = self.get_ventes_mois(pompiste_id, mois, annee)
        
        # Section: Résumé des ventes
        elements.append(Paragraph("RÉSUMÉ DES VENTES", self.styles['CustomHeading']))
        
        resume_data = self.calculer_resume_ventes(ventes)
        
        resume_table_data = [
            ['Indicateur', 'Valeur'],
            ['Nombre de ventes', str(resume_data['nombre_ventes'])],
            ['Quantité totale vendue', f"{resume_data['quantite_totale']:,.0f} L"],
            ['Montant total', f"{resume_data['montant_total']:,.2f} FCFA"],
            ['Heures travaillées', f"{resume_data['heures_travaillees']:.1f} h"],
            ['Ventes par période - Matin', f"{resume_data['ventes_matin']:,.2f} FCFA"],
            ['Ventes par période - Soir', f"{resume_data['ventes_soir']:,.2f} FCFA"],
            ['Ventes par période - Nuit', f"{resume_data['ventes_nuit']:,.2f} FCFA"],
        ]
        
        resume_table = Table(resume_table_data, colWidths=[3*inch, 2*inch])
        resume_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(resume_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Section: Détail des ventes quotidiennes
        elements.append(Paragraph("DÉTAIL DES VENTES QUOTIDIENNES", self.styles['CustomHeading']))
        
        if ventes:
            detail_data = [['Date', 'Période', 'Carburant', 'Quantité (L)', 'Montant (FCFA)']]
            
            for vente in ventes:
                detail_data.append([
                    vente['date'],
                    vente['periode'].title(),
                    vente['type_carburant'],
                    f"{vente['quantite_vendue']:,.0f}",
                    f"{vente['montant_total']:,.2f}"
                ])
            
            detail_table = Table(detail_data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 1.2*inch, 1.4*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(detail_table)
        else:
            elements.append(Paragraph("Aucune vente enregistrée pour cette période.", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Ajouter un graphique (si des données existent)
        if ventes:
            elements.append(Paragraph("GRAPHIQUE DES VENTES PAR PÉRIODE", self.styles['CustomHeading']))
            chart = self.create_bar_chart(resume_data)
            elements.append(chart)
        
        # Pied de page
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"""
        <para align=center>
        <i>Rapport généré automatiquement par le Système de Gestion TOTAL</i><br/>
        <i>{datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</i>
        </para>
        """
        elements.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Générer le PDF
        doc.build(elements)
        
        return output_path
    
    def get_ventes_mois(self, pompiste_id: int, mois: str, annee: str) -> List[Dict]:
        """
        Récupère toutes les ventes d'un pompiste pour un mois
        
        Args:
            pompiste_id (int): ID du pompiste
            mois (str): Mois (format MM)
            annee (str): Année (format YYYY)
            
        Returns:
            List[Dict]: Liste des ventes
        """
        # Calculer la plage de dates
        date_debut = f"{annee}-{mois}-01"
        
        # Dernier jour du mois
        if mois == '12':
            date_fin = f"{int(annee)+1}-01-01"
        else:
            date_fin = f"{annee}-{int(mois)+1:02d}-01"
        
        # Simulation - À adapter avec une vraie requête SQL
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.*, r.type_carburant
            FROM ventes v
            JOIN reservoirs r ON v.reservoir_id = r.id
            WHERE v.pompiste_id = ? 
            AND v.date >= ? 
            AND v.date < ?
            ORDER BY v.date, v.periode
        ''', (pompiste_id, date_debut, date_fin))
        
        ventes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return ventes
    
    def calculer_resume_ventes(self, ventes: List[Dict]) -> Dict:
        """
        Calcule un résumé des ventes
        
        Args:
            ventes (List[Dict]): Liste des ventes
            
        Returns:
            Dict: Résumé des statistiques
        """
        if not ventes:
            return {
                'nombre_ventes': 0,
                'quantite_totale': 0,
                'montant_total': 0,
                'heures_travaillees': 0,
                'ventes_matin': 0,
                'ventes_soir': 0,
                'ventes_nuit': 0
            }
        
        nombre_ventes = len(ventes)
        quantite_totale = sum(v['quantite_vendue'] for v in ventes)
        montant_total = sum(v['montant_total'] for v in ventes)
        
        # Calcul approximatif des heures (8h par shift)
        heures_travaillees = nombre_ventes * 8
        
        # Ventes par période
        ventes_matin = sum(v['montant_total'] for v in ventes if v['periode'] == 'matin')
        ventes_soir = sum(v['montant_total'] for v in ventes if v['periode'] == 'soir')
        ventes_nuit = sum(v['montant_total'] for v in ventes if v['periode'] == 'nuit')
        
        return {
            'nombre_ventes': nombre_ventes,
            'quantite_totale': quantite_totale,
            'montant_total': montant_total,
            'heures_travaillees': heures_travaillees,
            'ventes_matin': ventes_matin,
            'ventes_soir': ventes_soir,
            'ventes_nuit': ventes_nuit
        }
    
    def create_bar_chart(self, resume_data: Dict) -> Drawing:
        """
        Crée un graphique en barres des ventes par période
        
        Args:
            resume_data (Dict): Données résumées
            
        Returns:
            Drawing: Graphique à insérer dans le PDF
        """
        drawing = Drawing(400, 200)
        
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [[
            resume_data['ventes_matin'],
            resume_data['ventes_soir'],
            resume_data['ventes_nuit']
        ]]
        
        bc.categoryAxis.categoryNames = ['Matin', 'Soir', 'Nuit']
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(resume_data['ventes_matin'], 
                                     resume_data['ventes_soir'], 
                                     resume_data['ventes_nuit']) * 1.2
        
        bc.bars[0].fillColor = colors.HexColor('#4CAF50')
        
        drawing.add(bc)
        
        return drawing
    
    def generer_rapport_global(self, date_debut: str, date_fin: str, 
                               output_path: str = 'rapports/rapport_global.pdf'):
        """
        Génère un rapport global de la station pour une période
        
        Args:
            date_debut (str): Date de début (YYYY-MM-DD)
            date_fin (str): Date de fin (YYYY-MM-DD)
            output_path (str): Chemin de sortie du fichier PDF
            
        Returns:
            str: Chemin du fichier généré
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        
        # Titre
        elements.append(Paragraph("RAPPORT GLOBAL DE LA STATION", self.styles['CustomTitle']))
        elements.append(Paragraph(f"Période: {date_debut} au {date_fin}", self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Ajouter le contenu du rapport
        # ... (à compléter selon les besoins)
        
        doc.build(elements)
        
        return output_path