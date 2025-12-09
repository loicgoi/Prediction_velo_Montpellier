# Pipeline de Réentrainement Mensuel

## Objectif

Le trafic cyclable évolue : de nouvelles pistes ouvrent, les habitudes changent, et de nouveaux compteurs sont installés. Un modèle entrainé en 2023 sera moins performant en 2025.

Ce pipeline a pour but de **régénérer automatiquement** les fichiers du modèle (`xgboost_v1.pkl` et `preprocessor_v1.pkl`) en utilisant **l'integralité de l'historique disponible** en base de données au moment de l'exécution.

## Déclencheurs (Triggers)

Le processus peut être lancé de deux manières :

1. **Automatique (Planifié) :**
   * **Fréquence :** Le 1er de chaque mois a 02h00 du matin.
   * **Composant :** `backend/core/scheduler.py` (APScheduler).

2. **Manuel (Administration) :**
   * **Action :** Requête POST sur l'endpoint `/api/train`.
   * **Mecanisme :** Utilisation de `BackgroundTasks` FastAPI pour ne pas bloquer la reponse HTTP.

## Flux de Données (Workflow)

Le processus est orchestré par le module `training_orchestrator.py`. Voici les étapes séquentielles :

1. **Extraction (SQL -> Pandas) :**
   * Récuperation de tout l'historique `bike_count` (Target).
   * Récuperation de tout l'historique `weather` (Features contextuelles).
   * Récuperation du reférentiel `counters_info` (Lat/Lon).
   * **Fusion :** Merge des trois sources en un seul DataFrame cohérent.

2. **Transformation (Feature Engineering) :**
   * Nettoyage des donnees (calcul de `avg_temp` si manquant).
   * Suppression des compteurs suspects ("Blacklist").
   * Création des variables temporelles, cycliques et météorologiques.
   * Création des Lags (J-1, J-7).

3. **Entrainement & Sauvegarde :**
   * Le Dataset prépare est envoyé au pipeline d'entrainement (`model_training.py`).
   * Le modèle est entraine sur 100% des données (pas de split de test en mode production).
   * Les artefacts `.pkl` sont écrasés dans le dossier `backend/data/models/`.

### Diagramme de Séquence

```mermaid
sequenceDiagram
    autonumber
    participant Scheduler as Scheduler / API
    participant Orch as Training Orchestrator
    participant DB as Database
    participant Feature as Feature Engineer
    participant Trainer as Model Trainer
    participant Storage as Disk (Models)

    Note over Scheduler: Declenchement (1er du mois ou POST /train)

    Scheduler->>Orch: run_model_training()
    
    rect rgb(240, 248, 255)
        Note right of Orch: 1. Chargement des Donnees
        Orch->>DB: SELECT * FROM bike_count
        Orch->>DB: SELECT * FROM weather
        Orch->>DB: SELECT * FROM counters_info
        DB-->>Orch: DataFrames bruts
        Orch->>Orch: Merge DataFrames
    end

    rect rgb(255, 250, 240)
        Note right of Orch: 2. Feature Engineering
        Orch->>Feature: Instanciation
        Feature->>Feature: Nettoyage + Creation Variables
        Feature-->>Orch: Dataset Final (X, y)
    end

    rect rgb(240, 255, 240)
        Note right of Orch: 3. Entrainement
        Orch->>Trainer: train_model_pipeline(df)
        Trainer->>Trainer: Preprocessing.fit()
        Trainer->>Trainer: XGBoost.train()
        Trainer->>Storage: Overwrite .pkl files
    end

    Orch-->>Scheduler: Succes (Logs)
```

## Fichiers Impliqués

| Fichier | Rôle Technique |
| :--- | :--- |
| **`core/scheduler.py`** | Configure la tache CRON (`APScheduler`) qui tourne en arrière-plan de l'API. Définit l'heure et la fréquence. |
| **`api/endpoints.py`** | Expose la route POST `/train` et incremente les metriques Prometheus (`training_started_total`). |
| **`core/training_orchestrator.py`** | **Le chef de chantier.** Il fait le lien entre la base de données brute et le pipeline d'entrainement technique. Il gere la logique de fusion des tables SQL. |
| **`pipelines/model_training.py`** | Le script technique qui contient la logique Scikit-Learn/XGBoost (Fit, GridSearch, Save). |

## Points de Vigilance

1. **Temps d'exécution :** Ce processus peut etre long (plusieurs minutes). C'est pourquoi il est exécute de manière asynchrone (Background Task) pour ne pas bloquer l'API.
2. **Disponibilité des données :** Si la base de données est vide ou si la meteo est manquante, l'orchestrateur avorte le processus (`Aborting training`) pour ne pas écraser un bon modèle par un modèle vide.
3. **Redemarrage du Serveur :** Le scheduler est configuré avec `replace_existing=True`. Si le serveur redémarre, la tache planifiée est correctement réenregistrée.