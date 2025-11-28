import pandas as pd
from pathlib import Path
from datetime import date

# Imports internes
from backend.data_loder.data_loder import MontpellierAPILoader
from backend.data_loder.weather_loader import WeatherLoader
from backend.data_exploration.data_exploration import Statistics

# Configuration du chemin vers backend/data/raw
# On remonte de backend/data_loder/ vers backend/
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data/raw"

def collect_all_data():
    """
    Execute les scripts de collecte pour le Trafic et la Meteo.
    """
    print("\n--- EXECUTION DE LA COLLECTE API ---")
    
    # 1. Trafic
    print("1. Lancement du module Trafic...")
    trafic_loader = MontpellierAPILoader()
    trafic_loader.run_full_extraction()
    
    # 2. Meteo
    print("2. Lancement du module Meteo...")
    weather_loader = WeatherLoader()
    # On arrete l'historique a la date du jour
    today_str = date.today().strftime("%Y-%m-%d")
    weather_loader.fetch_history(start_date="2023-01-01", end_date=today_str)
    
    print("Processus de collecte termine.")

def load_local_data(folder_path=DATA_RAW_DIR):
    """
    Charge tous les fichiers CSV presents dans le dossier specifie.
    Retourne un dictionnaire {nom_fichier: dataframe}.
    """
    print(f"\n--- CHARGEMENT DES DONNEES LOCALES DEPUIS {folder_path} ---")
    
    dfs = {}
    DATA_FOLDER = Path(folder_path)
    
    if not DATA_FOLDER.exists():
        print(f"Erreur: Le dossier {DATA_FOLDER} n'existe pas. Veuillez lancer la collecte d'abord.")
        return dfs

    files = list(DATA_FOLDER.glob("*.[cC][sS][vV]"))
    
    if not files:
        print("Aucun fichier CSV trouve dans le dossier.")
        return dfs

    for file in files:
        name = file.stem
        try:
            df = pd.read_csv(file)
            # Conversion standard de la date si presente
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            dfs[name] = df
            print(f"Fichier charge: {name}.csv ({len(df)} lignes)")
        except Exception as e:
            print(f"Erreur de lecture sur {name}: {e}")
            
    return dfs

def explore_data(dfs_dict):
    """
    Utilise la classe Statistics pour afficher un rapport sur chaque DataFrame.
    """
    if not dfs_dict:
        print("Aucune donnee en memoire a explorer.")
        return

    print("\n--- EXPLORATION DES DONNEES ---")
    
    for name, df in dfs_dict.items():
        print(f"\n=== ANALYSE DU FICHIER : {name} ===")
        # On instancie la classe de ton collegue pour eviter la duplication de code
        stats = Statistics(df)
        stats.info()
        stats.describe()
        stats.isna()
        stats.duplicated()