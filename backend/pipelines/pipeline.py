import logging
import sys
from pathlib import Path

# Configuration du path pour importer depuis backend
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from backend.data_loder.load_local_data import collect_all_data, load_local_data, explore_data

logging.basicConfig(level=logging.INFO)

def main():
    loaded_dfs = None

    while True:
        print("\n=== PIPELINE VELO MONTPELLIER ===")
        print("1 - Collecter les données (API -> CSV)")
        print("2 - Charger les fichiers locaux")
        print("3 - Explorer les données")
        print("4 - Quitter")

        choice = input("\nVotre choix : ")

        if choice == "1":
            collect_all_data()
        
        elif choice == "2":
            loaded_dfs = load_local_data()
            
        elif choice == "3":
            if loaded_dfs:
                explore_data(loaded_dfs)
            else:
                print("Veuillez charger les données d'abord (Option 2).")
        
        elif choice == "4":
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()