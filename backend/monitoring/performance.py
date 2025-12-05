import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from database.service import DatabaseService
from utils.logging_config import logger

class PerformanceMonitor:
    def __init__(self, session: Session):
        self.session = session
        self.service = DatabaseService(session)

    def run_daily_evaluation(self, evaluation_date: datetime):
        """
        Compare les prédictions vs la réalité pour une date donnée (J-1).
        Calcule les erreurs et remplit la table model_metrics.
        """
        date_str = evaluation_date.strftime('%Y-%m-%d')
        logger.info(f"Démarrage du Monitoring pour la date : {date_str}")

        # 1. Récupération des données (Prédictions vs Réalité)
        preds_list = self.service.get_predictions_by_date(evaluation_date)
        actuals_list = self.service.get_actuals_by_date(evaluation_date)

        # Sécurités de base
        if not preds_list:
            logger.warning(f"Aucune prédiction trouvée pour le {date_str}. Impossible d'évaluer.")
            return
        
        if not actuals_list:
            logger.warning(f"Aucune donnée réelle trouvée pour le {date_str}. Le pipeline de mise à jour a-t-il tourné ?")
            return

        # 2. Conversion en DataFrames 
        df_preds = pd.DataFrame([{
            "station_id": p.station_id, 
            "predicted_value": p.prediction_value,
            "model_version": p.model_version
        } for p in preds_list])

        df_actuals = pd.DataFrame([{
            "station_id": a.station_id, 
            "actual_value": a.intensity
        } for a in actuals_list])

        # 3. Fusion (Inner Join) : On ne note que ce qui est comparable
        # Cela élimine les stations qui ont une prédiction mais pas de donnée réelle (panne) et inversement
        df_metrics = pd.merge(df_preds, df_actuals, on="station_id", how="inner")
        
        if df_metrics.empty:
            logger.error("Erreur : Aucune station commune trouvée entre les prédictions et la réalité.")
            return

        # 4. Calcul des Erreurs Mathématiques
        # Erreur Absolue ( |Pred - Réel| )
        df_metrics['absolute_error'] = (df_metrics['predicted_value'] - df_metrics['actual_value']).abs()
        
        # MAE du Jour (Moyenne des erreurs absolues)
        # C'est l'indicateur clé : "En moyenne aujourd'hui, on s'est trompé de X vélos"
        daily_mae = df_metrics['absolute_error'].mean()

        logger.info(f"Performance du jour ({len(df_metrics)} stations) : MAE = {daily_mae:.2f}")

        # 5. Préparation pour la sauvegarde en BDD
        # On construit la liste de dictionnaires pour le bulk_insert
        metrics_to_save = []
        for _, row in df_metrics.iterrows():
            metrics_to_save.append({
                "date": evaluation_date,
                "station_id": row['station_id'],
                "actual_value": int(row['actual_value']),
                "predicted_value": int(row['predicted_value']),
                "absolute_error": float(row['absolute_error']),
                "mean_absolute_error": float(daily_mae), # On répète la métrique globale sur chaque ligne pour faciliter les requêtes SQL futures
                "model_version": row['model_version']
            })

        # 6. Appel au service pour insérer
        try:
            # Utilisation de la méthode existante add_model_metrics
            success = self.service.add_model_metrics(metrics_to_save)
            if success:
                self.session.commit()
                logger.info("Métriques sauvegardées avec succès dans 'model_metrics'.")
            else:
                logger.error("Echec de l'insertion des métriques.")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur critique lors du commit des métriques : {e}")