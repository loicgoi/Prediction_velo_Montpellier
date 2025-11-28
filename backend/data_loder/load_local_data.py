import logging
from pathlib import Path
from datetime import date
import pandas as pd
from backend.data_loder.data_loder import MontpellierAPILoader
from backend.data_loder.weather_loader import WeatherLoader
from backend.data_exploration.data_exploration import Statistics

# Configuration du Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data/raw"

def collect_all_data():
    """
    Lance la collecte API pour le Trafic et la Météo.
    """
    logger.info("--- DEMARRAGE COLLECTE API ---")
    
    # 1. Trafic
    logger.info("1. Lancement du module Trafic...")
    trafic_loader = MontpellierAPILoader()
    trafic_loader.run_full_extraction()
    
    # 2. Météo
    logger.info("2. Lancement du module Météo...")
    weather_loader = WeatherLoader()
    today_str = date.today().strftime("%Y-%m-%d")
    weather_loader.fetch_history(start_date="2023-01-01", end_date=today_str)
    
    logger.info("Collecte terminée.")

def load_local_data(folder_path=DATA_RAW_DIR):
    """
    Charge tous les CSV du dossier spécifié.
    """
    logger.info(f"--- CHARGEMENT LOCAL DEPUIS : {folder_path} ---")
    
    dfs = {}
    DATA_FOLDER = Path(folder_path)
    
    if not DATA_FOLDER.exists():
        logger.error(f"Le dossier {DATA_FOLDER} n'existe pas. Lancez la collecte d'abord.")
        return dfs

    files = list(DATA_FOLDER.glob("*.[cC][sS][vV]"))
    
    if not files:
        logger.warning(f"Aucun fichier CSV trouvé dans {DATA_FOLDER}.")
        return dfs

    for file in files:
        name = file.stem
        try:
            df = pd.read_csv(file)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            dfs[name] = df
            logger.info(f"Chargé : {name}.csv ({len(df)} lignes)")
        except Exception as e:
            logger.error(f"Erreur de lecture sur {name}: {e}")
            
    return dfs

def explore_data(dfs_dict):
    """
    Affiche les informations pour chaque DataFrame contenu dans le dictionnaire.
    Utilise la classe Statistics de data_exploration.py
    """
    if not dfs_dict:
        print("Aucune donnee a explorer.")
        return

    print("--- EXPLORATION ---")
    
    for name, df in dfs_dict.items():
        print(f"\n=== JEU DE DONNEES : {name} ===")
        # Utilisation de la classe issue de data_exploration.py
        stats = Statistics(df)
        stats.info()
        stats.describe()
        stats.isna()
        stats.duplicated()