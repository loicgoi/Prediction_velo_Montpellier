from nicegui import ui, app
import requests
from typing import Dict, Optional, List
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# CONFIGURATION & DONNÉES
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


def get_mock_backend_data():
    return {
        "prediction_today": np.random.randint(200, 800),
        "yesterday": {
            "predicted": np.random.randint(200, 800),
            "real": np.random.randint(200, 800),
        },
        "history_30_days": np.random.randint(150, 700, 30).tolist(),
        "accuracy_7_days": {
            "real": np.random.randint(300, 600, 7).tolist(),
            "pred": np.random.randint(300, 600, 7).tolist(),
        },
        "weekly_averages": np.random.randint(400, 650, 7).tolist(),
        "weekly_totals": np.random.randint(2500, 4500, 12).tolist(),
    }


# FONCTIONS UTILITAIRES
def get_real_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,wind_speed_10m&timezone=auto"
        res = requests.get(url, timeout=1)
        if res.status_code == 200:
            d = res.json().get("current", {})
            return {
                "temp": f"{d.get('temperature_2m')}°C",
                "precip": f"{d.get('precipitation')}mm",
                "wind": f"{d.get('wind_speed_10m')}km/h",
            }
    except:
        pass
    return {"temp": "--", "precip": "--", "wind": "--"}


def get_counter_by_id(station_id):
    return next((c for c in MOCK_COUNTERS if c["station_id"] == station_id), None)


# VISUALISATION
# Note : Chaque fonction prend maintenant un argument 'ax'
def plot_history_30d(ax, data, prediction_today):
    days = np.arange(len(data))
    ax.plot(days, data, color="#94a3b8", label="Réel (30j)")
    ax.fill_between(days, data, color="#94a3b8", alpha=0.1)
    ax.plot(
        len(data),
        prediction_today,
        marker="o",
        color="#2563eb",
        markersize=8,
        label="Prév. J",
    )
    ax.set_title("Tendance 30 jours + Prévision", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.5)


def plot_accuracy_7d(ax, real, pred):
    days = ["J-7", "J-6", "J-5", "J-4", "J-3", "J-2", "Hier"]
    x = np.arange(len(days))
    width = 0.35
    ax.bar(x - width / 2, pred, width, label="Prédit", color="#cbd5e1")
    ax.bar(x + width / 2, real, width, label="Réel", color="#3b82f6")
    ax.set_xticks(x)
    ax.set_xticklabels(days, fontsize=7)
    ax.set_title("Fiabilité (7j)", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)


def plot_weekly_averages(ax, averages):
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    colors = ["#cbd5e1"] * 7
    colors[datetime.now().weekday()] = "#2563eb"
    bars = ax.bar(days, averages, color=colors)
    ax.set_title("Profil Hebdo", fontsize=10, fontweight="bold")
    ax.tick_params(axis="x", labelsize=8)
    ax.yaxis.set_ticks([])  # Enlever l'axe Y pour plus de clarté
    # Petit chiffre au dessus des barres
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height(),
            f"{int(bar.get_height())}",
            ha="center",
            va="bottom",
            fontsize=7,
        )


def plot_weekly_totals(ax, totals):
    weeks = np.arange(len(totals))
    ax.plot(weeks, totals, marker="o", linestyle="-", color="#2563eb", linewidth=1.5)
    ax.set_title("Volume (12 sem.)", fontsize=10, fontweight="bold")
    ax.set_xlabel("Semaines", fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.5)


# RENDU CONTENU
@ui.refreshable
def render_counter_content(station_id: str):
    counter = get_counter_by_id(station_id)
    if not counter:
        return

    lat, lon = counter["lat"], counter["lon"]
    weather = get_real_weather(lat, lon)
    bd = get_mock_backend_data()  # Mock Data

    # KPI Setup
    pred, real = bd["yesterday"]["predicted"], bd["yesterday"]["real"]
    delta = real - pred
    delta_percent = (delta / pred) * 100 if pred else 0
    delta_color = "text-red-500" if abs(delta_percent) > 15 else "text-green-600"

    # UI Header
    ui.label(f"{counter['name']}").classes("text-xl font-bold text-primary mb-2")

    with ui.tabs().classes("w-full") as tabs:
        info_tab = ui.tab("Tableau de Bord")
        graph_tab = ui.tab("Analyses & Stats")

    with ui.tab_panels(tabs, value=info_tab).classes("w-full p-2"):
        # ONGLET 1
        with ui.tab_panel(info_tab):
            with ui.row().classes("w-full gap-4 wrap"):
                # Carte
                with ui.card().classes("min-w-[500px] flex-grow"):
                    ui.label("Localisation").classes("font-bold mb-1")
                    maps = ui.leaflet(center=(lat, lon), zoom=15).classes("h-82 w-full")
                    maps.marker(latlng=(lat, lon))
                with ui.column().classes("flex-grow gap-4 min-w-[300px]"):
                    with ui.card().classes(
                        "w-full bg-blue-50 border-l-4 border-blue-500"
                    ):
                        ui.label("Prévision Aujourd'hui").classes(
                            "text-sm text-gray-600"
                        )
                        with ui.row().classes("items-center gap-4"):
                            ui.icon("directions_bike", size="xl").classes(
                                "text-blue-600"
                            )
                            ui.label(f"{bd['prediction_today']}").classes(
                                "text-4xl font-bold text-blue-900"
                            )
                    with ui.card().classes("w-full"):
                        ui.label("Bilan Hier").classes("font-bold text-gray-700")
                        with ui.row().classes("w-full justify-between items-end"):
                            ui.label(f"Prévu: {pred}").classes("text-gray-500")
                            ui.label(f"Réel: {real}").classes("font-bold text-gray-800")
                            ui.label(f"{delta:+} ({delta_percent:+.0f}%)").classes(
                                f"font-bold {delta_color}"
                            )
                    with ui.card().classes("w-full bg-gray-50"):
                        with ui.row().classes("w-full justify-between"):
                            for icon, val in [
                                ("thermostat", weather["temp"]),
                                ("water_drop", weather["precip"]),
                                ("air", weather["wind"]),
                            ]:
                                with ui.column().classes("items-center"):
                                    ui.icon(icon)
                                    ui.label(val).classes("font-bold")

        # ONGLET 2 : GRAPHIQUES
        with ui.tab_panel(graph_tab):
            with ui.card().classes("w-full p-1"):
                with ui.matplotlib(figsize=(10, 8)).figure as fig:
                    # A = Historique (Large en haut)
                    # B = Profil Hebdo, C = Fiabilité (Au milieu)
                    # D = Volume Hebdo (Large en bas)
                    ax_dict = fig.subplot_mosaic(
                        """
                        AA
                        BC
                        DD
                        """,
                        gridspec_kw={"hspace": 0.5, "wspace": 0.5},
                    )  # hspace/wspace gère l'espacement

                    # On appelle nos fonctions en leur donnant le bon sous-graphique (ax)
                    plot_history_30d(
                        ax_dict["A"], bd["history_30_days"], bd["prediction_today"]
                    )
                    plot_weekly_averages(ax_dict["B"], bd["weekly_averages"])
                    plot_accuracy_7d(
                        ax_dict["C"],
                        bd["accuracy_7_days"]["real"],
                        bd["accuracy_7_days"]["pred"],
                    )
                    plot_weekly_totals(ax_dict["D"], bd["weekly_totals"])

                    # Nettoyage global des bordures pour un look "Dashboard"
                    for ax in ax_dict.values():
                        ax.spines["top"].set_visible(False)
                        ax.spines["right"].set_visible(False)


# PAGE
@ui.page("/")
def index():
    if "selected_station_id" not in app.storage.client:
        app.storage.client["selected_station_id"] = MOCK_COUNTERS[0]["station_id"]
    options = {c["station_id"]: c["name"] for c in MOCK_COUNTERS}

    with ui.header().classes(
        "bg-blue-900 text-white p-4 flex justify-between items-center shadow-md"
    ):
        with ui.row().classes("items-center"):
            ui.icon("pedal_bike", size="xl")
            ui.label("Vélo Montpellier IA").classes("text-xl font-bold ml-2")
        ui.select(
            options=options,
            value=app.storage.client["selected_station_id"],
            on_change=lambda e: (
                app.storage.client.update({"selected_station_id": e.value}),
                render_counter_content.refresh(e.value),
            ),
        ).classes("w-48 bg-blue-50 text-white rounded px-2").props(
            'dense behavior="menu"'
        )

    with ui.column().classes("w-full max-w-5xl mx-auto p-4 mt-20"):
        render_counter_content(app.storage.client["selected_station_id"])


ui.run()
