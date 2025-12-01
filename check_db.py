import sys
import os
from dotenv import load_dotenv
from sqlalchemy import func

load_dotenv()

# Correction du PATH pour trouver le dossier backend
current_dir = os.getcwd()
sys.path.append(os.path.join(current_dir, "backend"))

# Imports du backend
from database.database import DatabaseManager, BikeCount, CounterInfo


def check_tables():
    # On vérifie visuellement quelle URL est utilisée (en masquant le mot de passe)
    url = os.getenv("DATABASE_URL", "Non trouvé")
    safe_url = url.split("@")[1] if "@" in url else "Mode SQLite (local)"
    print(f"📡 Connexion vers : ...@{safe_url}")

    try:
        db = DatabaseManager()
        session = db.get_session()

        print("--- RAPPORT DE LA BASE DE DONNÉES ---")

        # Compter les compteurs
        nb_compteurs = session.query(CounterInfo).count()
        print(f"Compteurs : {nb_compteurs}")

        # Compter les relevés
        nb_releves = session.query(BikeCount).count()
        print(f"Relevés trafic : {nb_releves}")

        if nb_releves == 0:
            print("\nLa base est connectée mais VIDE.")
            print("Relancez l'étape 6 du menu (main.py) pour insérer les données.")
        else:
            print("\nLes données sont bien présentes !")

        session.close()

    except Exception as e:
        print(f"Erreur : {e}")


if __name__ == "__main__":
    check_tables()
