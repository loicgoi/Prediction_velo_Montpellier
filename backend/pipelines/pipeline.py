# pipelines/pipeline.py
from pathlib import Path
import pandas as pd
import logging

# On importe le nouveau loader consolidé
# Assure-toi que le dossier s'appelle bien data_loader et pas data_loder (faute de frappe fréquente)
from backend.data_loder.data_loder import MontpellierAPILoader
# from src.data_exploration.data_exploration import Statistics (A adapter plus tard)

# Configuration logs
logging.basicConfig(level=logging.INFO)

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_OUTPUT = BASE_DIR / "data/raw"

def load_api_process():
    """Lance le téléchargement complet (Metadata + Trafic)"""
    loader = MontpellierAPILoader()
    print("\n--- ÉTAPE 1 : COLLECTE API ---")
    df = loader.run_full_extraction()
    if df is not None:
        print("✅ Données collectées et sauvegardées !")
    else:
        print("❌ Échec de la collecte.")

def load_local_process():
    """Charge le fichier consolidé unique"""
    print("\n--- ÉTAPE 2 : CHARGEMENT LOCAL ---")
    file_path = DATA_OUTPUT / "trafic_history.csv"
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        print(f"✅ Chargé {len(df)} lignes depuis {file_path.name}")
        return df
    else:
        print("❌ Fichier introuvable. Lancez l'API d'abord.")
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
    
    # Ici, tu pourras réactiver la classe Statistics de ton collègue
    # Mais attention : elle doit être capable de gérer un DF avec une colonne 'station_id'
    # stats = Statistics(df) ...

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