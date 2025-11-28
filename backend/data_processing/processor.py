import pandas as pd
from pathlib import Path
import logging

# Configuration du Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED_DIR = BASE_DIR / "data/processed"
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def process_data(dfs_dict):
    """
    Traite les données brutes : Agrégation + Fusion.
    """
    logger.info("--- DEBUT DU TRAITEMENT (Processing) ---")
    
    # Vérification
    if 'trafic_history' not in dfs_dict or 'weather_history' not in dfs_dict:
        logger.error("Fichiers manquants ('trafic_history' ou 'weather_history').")
        return None

    # Copie
    df_trafic = dfs_dict['trafic_history'].copy()
    df_meteo = dfs_dict['weather_history'].copy()

    # --- ETAPE 1 : AGREGATION ---
    logger.info("Etape 1 : Agrégation du trafic par jour...")
    
    try:
        # Conversion en datetime 
        df_trafic['date'] = pd.to_datetime(df_trafic['date'])

        # 1. Normalisation : On retire l'heure (et le fuseau horaire par sécurité)
        # .dt.normalize() met l'heure à 00:00:00
        # .dt.tz_localize(None) retire l'info UTC si elle existe
        try:
            df_trafic['date_day'] = df_trafic['date'].dt.tz_localize(None).dt.normalize()
        except TypeError:
            df_trafic['date_day'] = df_trafic['date'].dt.normalize()
        
        # 2. GroupBy : Somme par Station et par Jour
        df_trafic_daily = df_trafic.groupby(['station_id', 'date_day'])['intensity'].sum().reset_index()
        df_trafic_daily.rename(columns={'date_day': 'date'}, inplace=True)
        
        logger.info(f"Agrégation réussie : {len(df_trafic_daily)} lignes générées.")

    except Exception as e:
        logger.error(f"Erreur lors de l'agrégation : {e}")
        return None

    # --- ETAPE 2 : FUSION ---
    logger.info("Etape 2 : Fusion avec la météo...")
    
    try:
        # Préparation Météo
        df_meteo['date'] = pd.to_datetime(df_meteo['date'])
        
        # Normalisation du format date (sans fuseau)
        try:
            df_meteo['date'] = df_meteo['date'].dt.tz_localize(None).dt.normalize()
        except TypeError:
             df_meteo['date'] = df_meteo['date'].dt.normalize()

        # Fusion (Left Join)
        df_final = pd.merge(df_trafic_daily, df_meteo, on='date', how='left')
        
    except Exception as e:
        logger.error(f"Erreur lors du merge : {e}")
        return None
    
    # --- SAUVEGARDE ---
    output_path = DATA_PROCESSED_DIR / "dataset_final.csv"
    try:
        df_final.to_csv(output_path, index=False)
        logger.info(f"✅ Traitement terminé. Fichier sauvegardé : {output_path}")
        
        # Petit aperçu pour valider
        logger.info(f"Aperçu :\n{df_final.head()}")
        return df_final
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier : {e}")
        return None