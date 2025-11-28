import logging
import sys
from pathlib import Path

# Ajout de la racine du projet au path pour les imports absolus
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# Import des fonctions unifiees depuis load_local_data
from backend.data_loder.load_local_data import (
    collect_all_data, 
    load_local_data, 
    explore_data
)

logging.basicConfig(level=logging.INFO)

def main():
    loaded_dfs = None

    while True:
        print("\n=== PIPELINE VELO MONTPELLIER ===")
        print("1 - Collecter les donnees (API -> CSV)")
        print("2 - Charger les fichiers locaux (CSV -> RAM)")
        print("3 - Explorer les donnees")
        print("4 - Quitter")

        choice = input("\nVotre choix : ")

        if choice == "1":
            collect_all_data()
        
        elif choice == "2":
            # Appel sans argument utilise le chemin par defaut defini dans la fonction
            loaded_dfs = load_local_data()
            
        elif choice == "3":
            if loaded_dfs:
                explore_data(loaded_dfs)
            else:
                print("Veuillez d'abord charger les donnees (Option 2).")
        
        elif choice == "4":
            print("Arret du programme.")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()