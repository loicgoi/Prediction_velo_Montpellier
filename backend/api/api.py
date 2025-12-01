from fastapi import FastAPI
from backend.api.endpoints import router as api_router

app = FastAPI(
    title="Prévision du Trafic Cyclable Montpellier",
    description="API pour fournir des prédictions de trafic et gérer les modèles.",
    version="1.0.0",
)

app.include_router(api_router)
