import xgboost as xgb
import joblib
from pathlib import Path
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error
from backend.utils.logging_config import logger 
from backend.utils.paths import MODELS_PATH

class ModelTrainer:
    def __init__(self):
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=1000,
            n_jobs=-1
        )
        self.best_model = None

    def train(self, X, y):
        """Entraînement avec validation croisée temporelle."""
        logger.info("--- Démarrage de l'entraînement XGBoost ---")
        
        # Définition des hyperparamètres à tester pour le GridSearchCV
        param_grid = {
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1],
            'n_estimators': [100, 500, 1000]
        }
        # Validation croisée temporelle (=/= train_test_split, non adapté aux séries temporelles)
        tscv = TimeSeriesSplit(n_splits=3)
        # Recherche des hyperparamètres via GridSearchCV
        grid_search = GridSearchCV(
            estimator=self.model,
            param_grid=param_grid,
            cv=tscv,
            scoring='neg_root_mean_squared_error',
            verbose=0,
            n_jobs=-1
        )
        
        logger.info("Recherche des meilleurs hyperparamètres (GridSearch)...")
        grid_search.fit(X, y)
        
        self.best_model = grid_search.best_estimator_
        
        logger.info(f"Meilleurs paramètres trouvés : {grid_search.best_params_}")
        logger.info(f"Meilleur score (RMSE) : {-grid_search.best_score_:.2f}")

    def evaluate(self, X_test, y_test):
        """Évaluation sur le jeu de test."""
        if not self.best_model:
            logger.error("Tentative d'évaluation sans modèle entraîné.")
            return

        predictions = self.best_model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        
        logger.info("--- Résultats de l'évaluation ---")
        logger.info(f"RMSE (Erreur quadratique moyenne) : {rmse:.2f}")
        logger.info(f"MAE (Erreur absolue moyenne)    : {mae:.2f}")
        
        return rmse

    def save(self, filename="xgboost_model.pkl"):
            """
            Sauvegarde le modèle entraîné.
            Si 'filename' est un nom simple, utilise MODELS_PATH.
            """
            if self.best_model:
                try:
                    path_obj = Path(filename)
                    
                    # Si le chemin n'a pas de dossier parent
                    if len(path_obj.parts) == 1:
                        target_path = MODELS_PATH / filename
                    else:
                        target_path = path_obj
                    
                    # Création du dossier parent si besoin
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    joblib.dump(self.best_model, target_path)
                    logger.info(f"Modèle sauvegardé sous : {target_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde du modèle : {e}")
            else:
                logger.warning("Aucun modèle à sauvegarder (entraînement non effectué ou échoué).")