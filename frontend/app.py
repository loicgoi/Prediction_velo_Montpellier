from nicegui import ui, app
import requests
from typing import Dict, Optional
import numpy as np
import matplotlib.pyplot as plt

# Données factices pour test
MOCK_COUNTERS = [
    {"station_id": "counter-01", "name": "Albert 1er", "lat": 43.615, "lon": 3.872},
    {"station_id": "counter-02", "name": "Lattes", "lat": 43.567, "lon": 3.908},
    {
        "station_id": "counter-03",
        "name": "Place de la Comédie",
        "lat": 43.608,
        "lon": 3.879,
    },
]

MOCK_DATA = {
    "counter-01": {
        "prediction": 150,
        "weather": {"temp": 18.5, "precip": 0.2, "wind": 15},
    },
    "counter-02": {
        "prediction": 220,
        "weather": {"temp": 19.0, "precip": 0.0, "wind": 25},
    },
    "counter-03": {
        "prediction": 450,
        "weather": {"temp": 17.9, "precip": 1.5, "wind": 10},
    },
}


# FONCTIONS UTILITAIRES
def get_street_name(lat: float, lon: float) -> str:
    """Récupère l'adresse via Nominatim."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {"User-Agent": "VeloMontpellierApp/1.0"}
        # Timeout court pour ne pas bloquer l'UI trop longtemps
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            return response.json().get("display_name", "Adresse inconnue")
    except Exception:
        pass
    return "Adresse non disponible"


def get_counter_by_id(station_id: str) -> Optional[Dict]:
    return next((c for c in MOCK_COUNTERS if c["station_id"] == station_id), None)


# COMPOSANTS UI
@ui.refreshable
def render_counter_content(station_id: str):
    """Affiche le contenu principal (rechargé quand l'ID change)."""

    counter = get_counter_by_id(station_id)
    if not counter:
        ui.label("Veuillez sélectionner un compteur.").classes("text-gray-500 italic")
        return

    data = MOCK_DATA.get(station_id, {})
    weather = data.get("weather", {})
    lat, lon = counter["lat"], counter["lon"]

    # Titre de l'emplacement
    ui.label(f"{counter['name']}").classes("text-xl font-bold text-primary mb-2")

    # SYSTÈME D'ONGLETS
    with ui.tabs().classes("w-full") as tabs:
        info_tab = ui.tab("Informations")
        graph_tab = ui.tab("Graphiques")

    with ui.tab_panels(tabs, value=info_tab).classes("w-full p-2"):
        # ONGLET 1 : INFOS
        with ui.tab_panel(info_tab):
            with ui.row().classes("w-full gap-4 wrap"):
                # Carte
                with ui.card().classes("min-w-[300px] flex-grow"):
                    ui.label("Localisation").classes("font-bold mb-2")
                    m = ui.leaflet(center=(lat, lon), zoom=15).classes("h-64 w-full")
                    m.marker(latlng=(lat, lon))

                # Colonne Info (Météo + Prédiction)
                with ui.column().classes("flex-grow gap-4"):
                    # Prédiction
                    with ui.card().classes("w-full bg-blue-50"):
                        ui.label("Prédiction Trafic (24h)").classes(
                            "text-sm text-gray-600"
                        )
                        with ui.row().classes("items-baseline"):
                            ui.icon("directions_bike", size="lg").classes(
                                "text-blue-600"
                            )
                            ui.label(f"{data.get('prediction', '?')}").classes(
                                "text-4xl font-bold text-blue-800"
                            )
                            ui.label("vélos").classes("text-lg")

                    # Météo
                    with ui.card().classes("w-full"):
                        ui.label("Météo du jour").classes("font-bold mb-2")
                        with ui.grid(columns=3).classes("w-full gap-2"):
                            with ui.column().classes("items-center"):
                                ui.icon("thermostat", size="md")
                                ui.label(f"{weather.get('temp')}°C")
                            with ui.column().classes("items-center"):
                                ui.icon("water_drop", size="md")
                                ui.label(f"{weather.get('precip')} mm")
                            with ui.column().classes("items-center"):
                                ui.icon("air", size="md")
                                ui.label(f"{weather.get('wind')} km/h")

        # ONGLET 2 : GRAPHIQUES
        with ui.tab_panel(graph_tab):
            ui.label(f"Statistiques pour {counter['name']}").classes(
                "text-lg font-bold mb-4"
            )

            # Exemple de Graphique Matplotlib
            with ui.matplotlib(figsize=(8, 4)).figure as fig:
                # Génération de fausses données pour l'exemple
                days = np.arange(1, 31)
                values = np.random.randint(100, 600, size=30) + (np.sin(days) * 50)

                ax = fig.gca()
                ax.plot(days, values, "b-o", alpha=0.7, label="Passages")
                ax.set_title("Évolution journalière (Mois en cours)")
                ax.set_xlabel("Jour du mois")
                ax.set_ylabel("Nombre de vélos")
                ax.grid(True, linestyle="--", alpha=0.5)
                ax.legend()


# UI
@ui.page("/")
def index():
    # Initialisation du stockage si vide
    if "selected_station_id" not in app.storage.client:
        app.storage.client["selected_station_id"] = MOCK_COUNTERS[0]["station_id"]

    ui.header().classes(replace="row items-center")
    with ui.header().classes("bg-blue-900 text-white p-4 shadow-md"):
        ui.icon("pedal_bike", size="xl")
        ui.label("Vélo Montpellier IA").classes("text-2xl font-bold ml-2")

    with ui.column().classes("w-full max-w-5xl mx-auto p-4 mt-20"):
        # Sélecteur de compteur
        options = {c["station_id"]: c["name"] for c in MOCK_COUNTERS}

        ui.select(
            options=options,
            label="Choisir un compteur",
            value=app.storage.client["selected_station_id"],
            on_change=lambda e: (
                app.storage.client.update({"selected_station_id": e.value}),
                render_counter_content.refresh(e.value),
            ),
        ).classes("w-full md:w-1/2 mb-6 shadow-sm bg-white rounded-lg p-2")

        # Affichage du contenu rafraîchissable
        render_counter_content(app.storage.client["selected_station_id"])


ui.run(storage_secret="SECRET_KEY_ROBUSTE_123")
