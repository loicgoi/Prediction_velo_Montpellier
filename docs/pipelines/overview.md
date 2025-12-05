# Orchestration et Pipelines

Cette section décrit les différents processus d'exécution du projet. Nous distinguons les processus d'initialisation (One-shot) des processus récurrents (Batchs quotidiens).

## Les Points d'Entrée

L'application dispose de deux points d'entrée principaux situés à la racine du module backend :

### main_initialize.py : Script d'installation.

Initialise la base de données.

Récupère tout l'historique (2023-Aujourd'hui).

Entraîne le premier modèle.

### main.py : Interface CLI (Menu) pour le débogage et l'exécution manuelle des tâches quotidiennes.

Le Flux Quotidien (Daily Batch)

**En production, le système exécute deux scripts séquentiellement chaque matin :**

```mermaid
graph TD
    A[Déclencheur (CRON 07:00)] --> B[daily_update.py]
    B --> C{Données J-1 dispo ?}
    C -->|Oui| D[Mise à jour BDD]
    D --> E[Monitoring Performance]
    C -->|Non| F[Log Warning & Arrêt]
    E --> G[daily_prediction.py]
    G --> H[Récupération Météo J0]
    H --> I[Construction Lags via BDD]
    I --> J[Inférence & Sauvegarde]
   
```

Mise à Jour (daily_update) : Récupère la vérité terrain de la veille.

Prédiction (daily_prediction) : Estime le trafic du jour en utilisant les données fraîchement insérées.