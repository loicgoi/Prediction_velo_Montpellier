import pandas as pd
from pathlib import Path
from datetime import date
from backend.data_loder.data_loder import MontpellierAPILoader
from backend.data_loder.weather_loader import WeatherLoader

# Configuration du chemin data/raw (situé dans backend/data/raw)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data/raw"

def collect_all_data():
    """Lance les extractions API Trafic et Météo"""
    print("\n--- COLLECTE API ---")
    
    print("1. Trafic...")
    trafic_loader = MontpellierAPILoader()
    trafic_loader.run_full_extraction()
    
    print("2. Météo...")
    weather_loader = WeatherLoader()
    today_str = date.today().strftime("%Y-%m-%d")
    weather_loader.fetch_history(start_date="2023-01-01", end_date=today_str)
    
    print("Collecte terminée.")

def load_local_data(folder_path=DATA_RAW_DIR):
    """Charge les CSV depuis le dossier spécifié"""
    print(f"\n--- CHARGEMENT LOCAL DEPUIS {folder_path} ---")
    dfs = {}
    DATA_FOLDER = Path(folder_path)
    
    if not DATA_FOLDER.exists():
        print(f"Le dossier {DATA_FOLDER} n'existe pas. Lancez l'option 1.")
        return dfs

    files = list(DATA_FOLDER.glob("*.[cC][sS][vV]"))
    if not files:
        print("Aucun fichier CSV trouvé.")
        return dfs

    for file in files:
        name = file.stem
        try:
            df = pd.read_csv(file)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            dfs[name] = df
            print(f"Chargé {name}.csv ({len(df)} lignes)")
        except Exception as e:
            print(f"Erreur sur {name}: {e}")
    return dfs

def explore_data(dfs_dict):
    """Affiche les infos des DataFrames"""
    if not dfs_dict:
        print("Rien à explorer.")
        return

    print("\n--- EXPLORATION ---")
    for name, df in dfs_dict.items():
        print(f"\nFICHIER : {name}")
        print(df.info())
        print(df.head())