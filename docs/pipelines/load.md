# Gestion de la Base de Données (Load)

Toutes les interactions SQL sont centralisées dans le DatabaseService.

## Modèle de Données

L'application utilise 4 tables principales :

**counters_info** : Référentiel des stations.

**bike_count** : Historique réel (Trafic).

**weather** : Historique météo.

**predictions** : Résultats du modèle.

## Stratégies d'Insertion

Nous utilisons deux approches selon le contexte :

**Insertion de Masse (Bulk)** : Utilisée pour l'historique. Rapide, mais ne retourne pas les IDs générés.

**Insertion Transactionnelle (Single)** : Utilisée pour les prédictions quotidiennes. Plus lente, mais permet de récupérer l'ID de la prédiction pour y lier le contexte (Features JSON).

::: database.service.DatabaseService
handler: python
options:
members:
- add_bike_counts
- save_prediction_single_with_context
- get_bike_count
show_root_heading: true