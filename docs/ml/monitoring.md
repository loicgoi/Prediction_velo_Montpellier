# Monitoring de Performance

Le monitoring est essentiel pour détecter une dérive du modèle (Data Drift ou Model Drift).

## Méthodologie

1. Le calcul de performance est déclenché à J+1, une fois que les données réelles sont disponibles.

2. Le système récupère les prédictions faites à la date D.

3. Le système récupère les données réelles de la date D.

4. Une jointure (Inner Join) est faite sur l'ID de station.

5. On calcule l'Erreur Absolue (|Predit - Reel|).

## Implémentation

::: monitoring.performance.PerformanceMonitor
handler: python
options:
members:
- run_daily_evaluation
show_root_heading: true

## Stockage

Les métriques sont stockées dans la table model_metrics. Cela permet de requêter facilement le MAE (Mean Absolute Error) moyen par jour pour visualiser la santé du modèle sur un dashboard.