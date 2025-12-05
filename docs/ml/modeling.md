# Modélisation IA

Cette section détaille les classes responsables de l'entraînement et de l'inférence.

## Le Prédicteur (Inférence)

C'est la classe utilisée par le script journalier pour prédire J0.

::: modeling.predictor.TrafficPredictor
handler: python
options:
members:
- predict_daily_batch
- save_predictions_to_db
show_root_heading: true
show_source: true

## L'Entraîneur (Training)

Classe responsable de la GridSearch et de la validation croisée.

::: modeling.trainer.ModelTrainer
handler: python
options:
show_root_heading: true