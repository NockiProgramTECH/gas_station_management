"""
Moteur d'Analytics Avancé
Calculs automatiques, prédictions et analyses en temps réel
"""

from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import math

class AnalyticsEngine:
    """
    Moteur d'analytics pour analyses avancées et prédictions
    
    Attributes:
        db (DatabaseManager): Gestionnaire de base de données
    """
    
    def __init__(self):
        """Initialise le moteur d'analytics"""
        self.db = DatabaseManager()
    
    def calculer_pertes_automatiques(self, date: str = None) -> Dict:
        """
        Calcule automatiquement les pertes pour tous les réservoirs
        
        Args:
            date (str): Date au format YYYY-MM-DD (aujourd'hui par défaut)
            
        Returns:
            Dict: Résultats détaillés des pertes par réservoir
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        reservoirs = self.db.obtenir_reservoirs()
        resultats = {
            'date': date,
            'reservoirs': [],
            'pertes_totales_litres': 0,
            'pertes_totales_argent': 0,
            'alertes': []
        }
        
        for reservoir in reservoirs:
            analyse = self._analyser_reservoir(reservoir['id'], date)
            
            if analyse and 'perte_litres' in analyse:
                resultats['reservoirs'].append({
                    'nom': reservoir['nom'],
                    'type': reservoir['type_carburant'],
                    'perte_litres': analyse['perte_litres'],
                    'perte_argent': analyse['perte_argent'],
                    'pourcentage_perte': analyse['pourcentage_perte'],
                    'niveau_actuel': analyse['niveau_actuel'],
                    'statut': analyse['statut']
                })
                
                resultats['pertes_totales_litres'] += analyse['perte_litres']
                resultats['pertes_totales_argent'] += analyse['perte_argent']
                
                # Créer alerte si perte significative (>2%)
                if analyse['pourcentage_perte'] > 2:
                    alerte = {
                        'reservoir': reservoir['nom'],
                        'type': 'perte_significative',
                        'message': f"Perte de {analyse['perte_litres']:.2f}L ({analyse['pourcentage_perte']:.1f}%)",
                        'severite': 'haute' if analyse['pourcentage_perte'] > 5 else 'moyenne'
                    }
                    resultats['alertes'].append(alerte)
                    
                    # Enregistrer dans la base de données
                    self.db.creer_alerte(
                        reservoir['id'],
                        'perte_detectee',
                        alerte['message']
                    )
        
        return resultats
    
    def _analyser_reservoir(self, reservoir_id: int, date: str) -> Dict:
        """
        Analyse détaillée d'un réservoir pour une date
        
        Args:
            reservoir_id (int): ID du réservoir
            date (str): Date d'analyse
            
        Returns:
            Dict: Résultats de l'analyse
        """
        try:
            # Récupérer les données
            reservoir = self.db.obtenir_reservoir(reservoir_id)
            niveau = self.db.obtenir_niveau_quotidien(reservoir_id, date)
            
            if not niveau:
                return None
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Ventes de la journée
            cursor.execute('''
                SELECT SUM(quantite_vendue) as total_vendu,
                       SUM(montant_total) as total_montant,
                       AVG(montant_total / quantite_vendue) as prix_moyen
                FROM ventes
                WHERE reservoir_id = ? AND date = ?
            ''', (reservoir_id, date))
            
            ventes = cursor.fetchone()
            
            # Niveau de fin de journée (sera mesuré manuellement)
            # Pour simulation, on peut estimer ou récupérer du jour suivant
            cursor.execute('''
                SELECT quantite_debut as niveau_fin
                FROM niveaux_quotidiens
                WHERE reservoir_id = ? AND date = ?
            ''', (reservoir_id, (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')))
            
            niveau_fin_row = cursor.fetchone()
            conn.close()
            
            quantite_debut = niveau['quantite_debut'] + niveau['quantite_entree']
            quantite_vendue = ventes['total_vendu'] if ventes['total_vendu'] else 0
            prix_moyen = ventes['prix_moyen'] if ventes['prix_moyen'] else 0
            
            # Calcul théorique
            niveau_theorique = quantite_debut - quantite_vendue
            
            # Niveau réel (si disponible)
            niveau_reel = niveau_fin_row['niveau_fin'] if niveau_fin_row else niveau_theorique
            
            # Calcul des pertes
            perte_litres = max(0, niveau_theorique - niveau_reel)
            perte_argent = perte_litres * prix_moyen
            pourcentage_perte = (perte_litres / quantite_debut * 100) if quantite_debut > 0 else 0
            
            # Statut
            if pourcentage_perte < 1:
                statut = 'excellent'
            elif pourcentage_perte < 2:
                statut = 'bon'
            elif pourcentage_perte < 5:
                statut = 'attention'
            else:
                statut = 'critique'
            
            return {
                'quantite_debut': quantite_debut,
                'quantite_vendue': quantite_vendue,
                'niveau_theorique': niveau_theorique,
                'niveau_reel': niveau_reel,
                'niveau_actuel': niveau_reel,
                'perte_litres': perte_litres,
                'perte_argent': perte_argent,
                'pourcentage_perte': pourcentage_perte,
                'prix_moyen': prix_moyen,
                'statut': statut
            }
        
        except Exception as e:
            print(f"Erreur analyse réservoir: {e}")
            return None
    
    def predire_stock(self, reservoir_id: int, jours: int = 7) -> Dict:
        """
        Prédit le niveau de stock pour les prochains jours
        
        Args:
            reservoir_id (int): ID du réservoir
            jours (int): Nombre de jours à prédire
            
        Returns:
            Dict: Prédictions avec dates d'épuisement estimées
        """
        try:
            # Récupérer l'historique des 30 derniers jours
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            date_fin = datetime.now().strftime('%Y-%m-%d')
            date_debut = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT date, SUM(quantite_vendue) as vente_jour
                FROM ventes
                WHERE reservoir_id = ? AND date >= ? AND date <= ?
                GROUP BY date
                ORDER BY date
            ''', (reservoir_id, date_debut, date_fin))
            
            historique = cursor.fetchall()
            conn.close()
            
            if not historique or len(historique) < 3:
                return {'erreur': 'Pas assez de données historiques'}
            
            # Calculer la moyenne mobile des ventes
            ventes_moyennes = sum(h['vente_jour'] for h in historique) / len(historique)
            
            # Niveau actuel
            reservoir = self.db.obtenir_reservoir(reservoir_id)
            niveau_actuel_row = self.db.obtenir_niveau_quotidien(reservoir_id, date_fin)
            
            if not niveau_actuel_row:
                return {'erreur': 'Niveau actuel inconnu'}
            
            niveau_actuel = niveau_actuel_row['quantite_debut'] + niveau_actuel_row['quantite_entree']
            
            # Prédictions
            predictions = []
            niveau = niveau_actuel
            date_epuisement = None
            
            for jour in range(jours):
                date_future = (datetime.now() + timedelta(days=jour+1)).strftime('%Y-%m-%d')
                niveau -= ventes_moyennes
                
                predictions.append({
                    'date': date_future,
                    'niveau_predit': max(0, niveau),
                    'pourcentage': max(0, (niveau / reservoir['capacite_max']) * 100)
                })
                
                # Déterminer date d'épuisement
                if niveau <= 0 and not date_epuisement:
                    date_epuisement = date_future
            
            # Jours avant épuisement
            jours_restants = math.ceil(niveau_actuel / ventes_moyennes) if ventes_moyennes > 0 else float('inf')
            
            return {
                'reservoir': reservoir['nom'],
                'niveau_actuel': niveau_actuel,
                'capacite_max': reservoir['capacite_max'],
                'vente_moyenne_jour': ventes_moyennes,
                'jours_restants': jours_restants,
                'date_epuisement_estimee': date_epuisement,
                'predictions': predictions,
                'recommandation': self._generer_recommandation(jours_restants)
            }
        
        except Exception as e:
            print(f"Erreur prédiction: {e}")
            return {'erreur': str(e)}
    
    def _generer_recommandation(self, jours_restants: float) -> str:
        """
        Génère une recommandation basée sur les jours restants
        
        Args:
            jours_restants (float): Nombre de jours avant épuisement
            
        Returns:
            str: Recommandation
        """
        if jours_restants < 3:
            return "🚨 URGENT: Commander immédiatement"
        elif jours_restants < 7:
            return "⚠️ ATTENTION: Commander cette semaine"
        elif jours_restants < 14:
            return "📋 INFO: Planifier commande prochainement"
        else:
            return "✅ OK: Stock suffisant"
    
    def analyser_performance_pompistes(self, mois: str, annee: str) -> List[Dict]:
        """
        Analyse la performance de tous les pompistes pour un mois
        
        Args:
            mois (str): Mois (MM)
            annee (str): Année (YYYY)
            
        Returns:
            List[Dict]: Classement des pompistes par performance
        """
        pompistes = self.db.obtenir_pompistes()
        performances = []
        
        date_debut = f"{annee}-{mois}-01"
        if mois == '12':
            date_fin = f"{int(annee)+1}-01-01"
        else:
            date_fin = f"{annee}-{int(mois)+1:02d}-01"
        
        for pompiste in pompistes:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as nb_ventes,
                    SUM(quantite_vendue) as total_litres,
                    SUM(montant_total) as total_montant,
                    AVG(montant_total) as vente_moyenne
                FROM ventes
                WHERE pompiste_id = ? AND date >= ? AND date < ?
            ''', (pompiste['id'], date_debut, date_fin))
            
            stats = cursor.fetchone()
            conn.close()
            
            if stats and stats['nb_ventes'] > 0:
                performances.append({
                    'pompiste_id': pompiste['id'],
                    'nom_complet': f"{pompiste['prenom']} {pompiste['nom']}",
                    'nb_ventes': stats['nb_ventes'],
                    'total_litres': stats['total_litres'],
                    'total_montant': stats['total_montant'],
                    'vente_moyenne': stats['vente_moyenne'],
                    'efficacite': self._calculer_score_efficacite(stats)
                })
        
        # Trier par montant total
        performances.sort(key=lambda x: x['total_montant'], reverse=True)
        
        # Ajouter le rang
        for i, perf in enumerate(performances, 1):
            perf['rang'] = i
            perf['badge'] = self._attribuer_badge(i, len(performances))
        
        return performances
    
    def _calculer_score_efficacite(self, stats: Dict) -> float:
        """
        Calcule un score d'efficacité (0-100)
        
        Args:
            stats (Dict): Statistiques du pompiste
            
        Returns:
            float: Score d'efficacité
        """
        # Score basé sur plusieurs critères
        score = 0
        
        # Nombre de ventes (max 40 points)
        score += min(40, (stats['nb_ventes'] / 30) * 40)
        
        # Montant total (max 40 points)
        score += min(40, (stats['total_montant'] / 1000000) * 40)
        
        # Vente moyenne (max 20 points)
        score += min(20, (stats['vente_moyenne'] / 50000) * 20)
        
        return round(score, 1)
    
    def _attribuer_badge(self, rang: int, total: int) -> str:
        """
        Attribue un badge selon le rang
        
        Args:
            rang (int): Rang du pompiste
            total (int): Nombre total de pompistes
            
        Returns:
            str: Emoji du badge
        """
        if rang == 1:
            return "🥇"
        elif rang == 2:
            return "🥈"
        elif rang == 3:
            return "🥉"
        elif rang <= total * 0.25:
            return "⭐"
        else:
            return "👍"
    
    def generer_rapport_hebdomadaire(self) -> Dict:
        """
        Génère un rapport automatique de la semaine
        
        Returns:
            Dict: Rapport complet de la semaine
        """
        aujourd_hui = datetime.now()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        date_debut = debut_semaine.strftime('%Y-%m-%d')
        date_fin = fin_semaine.strftime('%Y-%m-%d')
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Ventes totales
        cursor.execute('''
            SELECT 
                COUNT(*) as nb_transactions,
                SUM(quantite_vendue) as total_litres,
                SUM(montant_total) as total_montant
            FROM ventes
            WHERE date >= ? AND date <= ?
        ''', (date_debut, date_fin))
        
        ventes_globales = cursor.fetchone()
        
        # Ventes par carburant
        cursor.execute('''
            SELECT 
                r.type_carburant,
                SUM(v.quantite_vendue) as litres,
                SUM(v.montant_total) as montant
            FROM ventes v
            JOIN reservoirs r ON v.reservoir_id = r.id
            WHERE v.date >= ? AND v.date <= ?
            GROUP BY r.type_carburant
        ''', (date_debut, date_fin))
        
        ventes_par_type = cursor.fetchall()
        
        # Meilleur jour
        cursor.execute('''
            SELECT 
                date,
                SUM(montant_total) as montant_jour
            FROM ventes
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY montant_jour DESC
            LIMIT 1
        ''', (date_debut, date_fin))
        
        meilleur_jour = cursor.fetchone()
        
        conn.close()
        
        return {
            'periode': f"{date_debut} à {date_fin}",
            'ventes_globales': dict(ventes_globales) if ventes_globales else {},
            'ventes_par_type': [dict(v) for v in ventes_par_type],
            'meilleur_jour': dict(meilleur_jour) if meilleur_jour else {},
            'pertes_semaine': self._calculer_pertes_periode(date_debut, date_fin)
        }
    
    def _calculer_pertes_periode(self, date_debut: str, date_fin: str) -> Dict:
        """
        Calcule les pertes sur une période
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
            
        Returns:
            Dict: Pertes totales de la période
        """
        debut = datetime.strptime(date_debut, '%Y-%m-%d')
        fin = datetime.strptime(date_fin, '%Y-%m-%d')
        
        pertes_totales_litres = 0
        pertes_totales_argent = 0
        
        current_date = debut
        while current_date <= fin:
            date_str = current_date.strftime('%Y-%m-%d')
            pertes_jour = self.calculer_pertes_automatiques(date_str)
            
            pertes_totales_litres += pertes_jour['pertes_totales_litres']
            pertes_totales_argent += pertes_jour['pertes_totales_argent']
            
            current_date += timedelta(days=1)
        
        return {
            'pertes_litres': pertes_totales_litres,
            'pertes_argent': pertes_totales_argent
        }