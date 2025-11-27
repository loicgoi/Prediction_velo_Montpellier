# pipelines/pipeline.py
from pathlib import Path
import pandas as pd
import logging
from backend.data_loder.data_loder import MontpellierAPILoader
from backend.data_loder.weather_loader import WeatherLoader
# Configuration logs
logging.basicConfig(level=logging.INFO)

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_OUTPUT = BASE_DIR / "data/raw"

def load_api_process():
    """Lance le téléchargement complet (Metadata + Trafic + Météo)"""
    trafic_loader = MontpellierAPILoader()
    weather_loader = WeatherLoader()
    print("\n--- ÉTAPE 1 : COLLECTE API ---")
    df_trafic = trafic_loader.run_full_extraction()
    df_weather = weather_loader.fetch_history(start_date="2023-01-01", end_date="2025-10-31")
    if df_trafic is not None and df_weather is not None:
        print("Données collectées et sauvegardées ! ")
    else:
        print("Échec de la collecte.")

def load_local_process():
    """Charge le fichier consolidé unique"""
    print("\n--- ÉTAPE 2 : CHARGEMENT LOCAL ---")
    file_path = DATA_OUTPUT / "trafic_history.csv"
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        print(f" Chargé {len(df)} lignes depuis {file_path.name}")
        return df
    else:
        print(" Fichier introuvable. Lancez l'API d'abord.")
        return None

def explore_data_process(df):
    """Exploration sur le Dataframe unique"""
    if df is None or df.empty:
        print("Rien à explorer.")
        return

    print("\n--- ÉTAPE 3 : EXPLORATION RAPIDE ---")
    print(df.info())
    print("\n--- Aperçu ---")
    print(df.head())
    
    print("\n--- Statistiques Globales ---")
    print(df.describe())


def main():
    while True:
        print("\n=== 🚲 PIPELINE VELO MONTPELLIER ===")
        print("1 - Télécharger depuis l'API (Mise à jour CSVs)")
        print("2 - Charger les CSVs locaux")
        print("3 - Explorer les données chargées")
        print("4 - Quitter")

        choice = input("\nVotre choix : ")

        if choice == "1":
            load_api_process()
        
        elif choice == "2":
            # On stocke le résultat en mémoire pour l'étape 3
            current_df = load_local_process()
            
        elif choice == "3":
            if 'current_df' in locals() and current_df is not None:
                explore_data_process(current_df)
            else:
                # Si l'utilisateur a sauté l'étape 2, on tente de charger
                current_df = load_local_process()
                explore_data_process(current_df)
        
        elif choice == "4":
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()