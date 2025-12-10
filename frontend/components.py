from nicegui import ui

from datetime import datetime
from data import get_counter_by_id, get_dashboard_data, get_real_weather
from plots import (
    plot_accuracy_7d,
    plot_history_30d,
    plot_weekly_averages,
    plot_weekly_totals,
)


@ui.refreshable
def render_counter_content(station_id: str):
    """Displays dynamic content (KPIs, maps, graphs) for a given counter."""
    counter = get_counter_by_id(station_id)
    if not counter:
        ui.label("Compteur non trouvé (ID invalide ou API inaccessible).")
        return

    lat, lon = counter["latitude"], counter["longitude"]
    weather = get_real_weather(lat, lon)
    bd = get_dashboard_data(station_id)

    # --- NEW: Extract prediction info and check for staleness ---
    prediction_info = bd.get("prediction", {"value": 0, "date": None})
    prediction_value = prediction_info.get("value", 0)
    prediction_date_str = prediction_info.get("date")

    is_stale = False
    is_missing = False
    if prediction_date_str:
        prediction_date = datetime.fromisoformat(prediction_date_str).date()
        today = datetime.now().date()
        if prediction_date != today:
            is_stale = True
    else:
        # No date means no prediction was ever found for this counter
        is_missing = True

    # KPI calculation
    pred, real = bd["yesterday"]["predicted"], bd["yesterday"]["real"]
    delta = real - pred
    delta_percent = (delta / pred) * 100 if pred else 0
    delta_color = "text-red-500" if abs(delta_percent) > 15 else "text-green-600"

    # Header
    ui.label(f"{counter['name']}").classes("text-xl font-bold text-primary mb-2")

    # Display warning if data is stale or missing
    if is_stale:
        with ui.card().classes("w-full bg-amber-100 border-l-4 border-amber-500 mb-4"):
            with ui.row().classes("items-center"):
                ui.icon("warning", color="amber-500").classes("mr-2")
                ui.label(
                    f"Les données de l'API externe ne sont pas à jour. "
                    f"La prédiction affichée est basée sur les dernières données disponibles en date du {prediction_date.strftime('%d/%m/%Y')}."
                ).classes("text-amber-800")
    elif is_missing:
        with ui.card().classes("w-full bg-red-100 border-l-4 border-red-500 mb-4"):
            with ui.row().classes("items-center"):
                ui.icon("error", color="red-500").classes("mr-2")
                ui.label(
                    "Aucune prédiction n'est disponible pour ce compteur. "
                    "Les données historiques sont peut-être insuffisantes ou le service est indisponible."
                ).classes("text-red-800")

    with ui.tabs().classes("w-full") as tabs:
        info_tab = ui.tab("Tableau de Bord")
        graph_tab = ui.tab("Analyses & Stats")

    with ui.tab_panels(tabs, value=info_tab).classes("w-full p-2"):
        # Tab 1: Dashboard
        with ui.tab_panel(info_tab):
            with ui.row().classes("w-full gap-4 flex flex-col md:flex-row"):
                # Maps
                with ui.card().classes("w-full md:w-1/2 flex-grow"):
                    ui.label("Localisation").classes("font-bold mb-1")
                    maps = ui.leaflet(center=(lat, lon), zoom=15).classes("h-82 w-full")
                    maps.marker(latlng=(lat, lon))
                # Right column with KPIs
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
                            ui.label(f"{prediction_value}").classes(
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

        # Tab 2: Charts
        with ui.tab_panel(graph_tab):
            with ui.card().classes("w-full p-1"):
                with ui.matplotlib(figsize=(10, 8)).figure as fig:
                    ax_dict = fig.subplot_mosaic(
                        """
                        AA
                        BC
                        DD
                        """,
                        gridspec_kw={"hspace": 0.5, "wspace": 0.5},
                    )

                    plot_history_30d(
                        ax_dict["A"], bd["history_30_days"], prediction_value
                    )
                    plot_weekly_averages(ax_dict["B"], bd["weekly_averages"])
                    plot_accuracy_7d(
                        ax_dict["C"],
                        bd["accuracy_7_days"]["real"],
                        bd["accuracy_7_days"]["pred"],
                    )
                    plot_weekly_totals(ax_dict["D"], bd["weekly_totals"])

                    for ax in ax_dict.values():
                        ax.spines["top"].set_visible(False)
                        ax.spines["right"].set_visible(False)
