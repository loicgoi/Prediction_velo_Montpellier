# Architecture projet

Le projet est divisé en deux blocs principaux conteneurisés via Docker :

1. **Backend** : Le moteur de l'application gérant la collecte, le traitement des données ainsi que sa mise à disposition pour l'entraînement du modèle (XGBoost).

2. **Frontend** : L'interface utilisateur pour visualiser les données et les prédictions.

## Arborescence

```

backend/
├── api/                            # Couche d'exposition (API REST)
│   ├── api.py                      # Point d'entree de l'application FastAPI
│   ├── endpoints.py                # Definition des routes (GET /predict, etc.)
│   └── server.py                   # Configuration du serveur Uvicorn/Gunicorn
├── core/                           # Configuration coeur
│   ├── dependencies.py             # Gestion des instances (Singleton BDD)
│   └── training.py                 # Constantes liees a l'entrainement
├── data/                           # Stockage local (Volume Docker)
│   ├── raw/                        # Fichiers CSV bruts temporaires
│   ├── models/                     # Artefacts ML (fichiers .pkl)
│   └── output/                     # Exports de donnees traitees
├── database/                       # Couche de stockage
│   ├── database.py                 # Modeles SQLAlchemy (Tables SQL)
│   ├── fetch_prediction.py         # Requetes specifiques de lecture
│   └── service.py                  # CRUD complet (Create, Read, Update, Delete)
├── download/                       # Connecteurs aux APIs externes (Extract)
│   ├── abstract_loader.py          # Classe mere abstraite pour les loaders
│   ├── daily_weather_api.py        # Client API OpenMeteo (Previsions J0)
│   ├── ecocounters_ids.py          # Recuperation de la liste des compteurs
│   ├── geocoding_service.py        # Service de conversion Adresse <-> GPS
│   ├── trafic_history_api.py       # Client API EcoCompteur (Historique avec pagination)
│   └── weeather_api.py             # Client API OpenMeteo (Archive historique)
├── features/                       # Ingenierie des fonctionnalites (Transform)
│   ├── features_engineering.py     # Transformation Donnee brute -> Variables ML
│   └── features_vizualization.py   # Outils graphiques pour analyser les features
├── modeling/                       # Coeur du Machine Learning
│   ├── predictor.py                # Moteur d'inference (Charge le modele et predit)
│   ├── preprocessor.py             # Transformation (Scaling, Encodage)
│   └── trainer.py                  # Entrainement (GridSearch, CrossVal, Save)
├── monitoring/                     # Suivi de la qualite
│   └── performance.py              # Calcul des metriques (MAE, RMSE) reel vs predit
├── pipelines/                      # Scripts d'orchestration (Workflows)
│   ├── daily_predictor.py          # Pipeline journalier : Prediction J0
│   ├── daily_update.py             # Pipeline journalier : Mise a jour J-1 + Monitoring
│   ├── data_insertion.py           # Logique d'insertion securisee en BDD
│   ├── initialize_project.py       # Script d'installation initiale (Historique complet)
│   ├── model_training.py           # Pipeline de re-entrainement complet
│   ├── pipeline.py                 # Menu interactif (CLI)
│   └── pipeline_visualization.py   # Generation de graphes pour le pipeline
├── src/                            # Utilitaires de traitement de donnees
│   ├── api_data_processing.py      # Nettoyage specifique aux retours API
│   ├── data_cleaner.py             # Fonctions de nettoyage (dedoublonnage, types)
│   ├── data_exploration.py         # Classe pour generer des stats descriptives
│   └── data_merger.py              # Logique de fusion (Merge Trafic + Meteo)
├── tests/                          # Tests unitaires et d'integration
│   ├── conftest.py                 # Configuration Pytest (Fixtures)
│   ├── test_api.py                 # Tests des endpoints API
│   ├── test_data_insertion.py      # Tests des ecritures en BDD
│   ├── test_database_service.py    # Tests des requetes SQL
│   └── test_train.py               # Tests du pipeline d'entrainement
├── utils/                          # Outils transverses
│   ├── logging_config.py           # Configuration centralisee des logs
│   ├── paths.py                    # Gestion des chemins absolus
│   └── weather_utils.py            # Parsing des reponses OpenMeteo
├── .dockerignore                   # Fichiers exclus du build Docker
├── Dockerfile                      # Definition de l'image Backend
├── main.py                         # Point d'entree CLI (Menu principal)
├── main_initialize.py              # Raccourci pour l'initialisation
└── requirements.txt                # Dependances Python
frontend/
├── app.py                          # Point d'entree de l'application Web
├── components.py                   # Widgets graphiques reutilisables
├── data.py                         # Connecteur pour recuperer les donnees du Backend
├── plots.py                        # Fonctions de generation de graphiques
├── requirements.txt                # Dependances Frontend
├── .dockerignore
└── Dockerfile                      # Definition de l'image Frontend
.gitignore                          # Fichiers exclus de Git
README.md                           # Documentation du projet
docker-compose.yml                  # Orchestration des conteneurs
logique_predict_daily.md            # Doc specifique sur la logique J0
prometheus.yml                      # Configuration monitoring infrastructure
reset_db.py                         # Script utilitaire pour vider la base
```

## Modélisation (C4)

### Diagramme de Contexte

```mermaid
C4Context
    title Diagramme de Contexte - Système de Prévision Vélo

    Person(user, "Utilisateur Final", "Urbaniste ou Citoyen de Montpellier")
    
    System(system, "Application Prévision Vélo", "Permet de visualiser l'historique et les prédictions de trafic cyclable.")

    System_Ext(api_mmm, "API Open Data Montpellier", "Fournit les comptages réels (J-1)")
    System_Ext(api_meteo, "API OpenMeteo", "Fournit l'historique et les prévisions météo (J0)")

    Rel(user, system, "Consulte les dashboards", "HTTPS")
    Rel(system, api_mmm, "Récupère les données trafic", "JSON/HTTPS")
    Rel(system, api_meteo, "Récupère la météo", "JSON/HTTPS")
```

### Diagramme de Conteneur

```mermaid
C4Container
    title Diagramme de Conteneurs - Architecture Docker/Azure

    Person(user, "Utilisateur", "Navigateur Web")

    Container_Boundary(azure, "Azure Cloud") {
        
        Container(frontend, "Frontend", "Python, NiceGUI", "Interface utilisateur interactive pour la visualisation.")
        
        Container(backend, "Backend API & Worker", "Python, FastAPI", "Gère l'ETL, l'entraînement du modèle et l'exposition des données.")
        
        ContainerDb(database, "Base de Données", "Azure SQL Database", "Stocke l'historique, les métadonnées et les prédictions.")
        
        Container(storage, "Stockage Local / Volume", "Système de Fichiers", "Stocke les modèles entraînés (.pkl) et les CSV temporaires.")
    }

    System_Ext(apis, "APIs Externes", "Montpellier & Météo")

    Rel(user, frontend, "Visite", "HTTPS")
    Rel(frontend, backend, "Requête les données", "HTTP/JSON")
    
    Rel(backend, database, "Lit/Ecrit les données", "SQL/SQLAlchemy")
    Rel(backend, storage, "Charge/Sauvegarde les modèles", "File System")
    Rel(backend, apis, "Télécharge les données", "HTTPS")
```

### Diagramme de Composant

```mermaid
C4Component
    title Diagramme de Composants - Backend Python

    Container_Boundary(backend, "Backend Application") {
        
        Component(orchestrator, "Pipelines Orchestrator", "daily_prediction.py, daily_update.py", "Coordonne les tâches planifiées (CRON).")
        
        Component(loader, "Data Loaders", "download/*", "Gère la connexion et la pagination avec les APIs externes.")
        
        Component(feature_eng, "Feature Engineer", "features_engineering.py", "Transforme les données brutes en vecteurs (Lags, Sinus, Météo).")
        
        Component(predictor, "ML Predictor", "modeling/predictor.py", "Charge le modèle XGBoost et effectue l'inférence.")
        
        Component(trainer, "ML Trainer", "modeling/trainer.py", "Entraîne et sauvegarde le modèle (Optionnel en prod).")
        
        Component(db_service, "Database Service", "database/service.py", "Abstraction CRUD pour parler à la BDD.")
        
        Component(api_routes, "API Endpoints", "api/endpoints.py", "Expose les résultats au Frontend.")
    }

    ContainerDb(db, "Database", "SQL Server")
    System_Ext(ext_api, "External APIs")

    Rel(orchestrator, loader, "Déclenche la collecte")
    Rel(loader, ext_api, "Requête")
    
    Rel(orchestrator, db_service, "Sauvegarde/Lit l'historique")
    Rel(db_service, db, "SQL Query")
    
    Rel(orchestrator, feature_eng, "Transforme les données")
    Rel(orchestrator, predictor, "Demande une prédiction")
    
    Rel(predictor, feature_eng, "Utilise pour le preprocessing")
    Rel(api_routes, db_service, "Lit les résultats finaux")
```