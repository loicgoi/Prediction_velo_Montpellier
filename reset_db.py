import sys, os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.getcwd(), "backend"))
from backend.database.database import DatabaseManager, Base

print("Reconstruction du schéma de base de données...")
db = DatabaseManager()
Base.metadata.drop_all(
    bind=db.engine
)  # Supprime tout (y compris la contrainte bloquante)
Base.metadata.create_all(bind=db.engine)  # Recrée tout (sans la contrainte)
print("Schéma mis à jour (Tables vides).")
