from fastapi import FastAPI
from api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app  # Corrected to use ASGI app
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(
    title="Prévision du Trafic Cyclable Montpellier",
    description="API pour fournir des prédictions de trafic et gérer les modèles.",
    version="1.0.0",
)

# Configuration du CORS pour autoriser les requêtes du frontend
origins = [
    "http://localhost:8080",  # Port par défaut de NiceGUI
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose Prometheus metrics through ASGI
app.mount("/metrics", make_asgi_app())


# Ajout d'une route à la racine de l'application
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Bienvenue sur l'API de prédiction de trafic vélo. Accédez à /docs pour la documentation."
    }


# Inclut les routes définies dans endpoints.py avec un préfixe
app.include_router(api_router, prefix="/api", tags=["API"])
