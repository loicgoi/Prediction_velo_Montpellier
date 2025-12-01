from fastapi import FastAPI
from backend.api.endpoints import router as api_router

app = FastAPI(
    title="Prévision du Trafic Cyclable Montpellier",
    description="API pour fournir des prédictions de trafic et gérer les modèles.",
    version="1.0.0",
)


# Ajout d'une route à la racine de l'application
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Bienvenue sur l'API de prédiction de trafic vélo. Accédez à /docs pour la documentation."
    }


# Inclut les routes définies dans endpoints.py avec un préfixe
app.include_router(api_router, prefix="/api", tags=["API"])
