from nicegui import ui

from data import get_counter_by_id, get_mock_backend_data, get_real_weather
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
    bd = get_mock_backend_data()  # Dummy data (to be connected to the backend)

    # KPI calculation
    pred, real = bd["yesterday"]["predicted"], bd["yesterday"]["real"]
    delta = real - pred
    delta_percent = (delta / pred) * 100 if pred else 0
    delta_color = "text-red-500" if abs(delta_percent) > 15 else "text-green-600"

    # Header
    ui.label(f"{counter['name']}").classes("text-xl font-bold text-primary mb-2")

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
                        ax_dict["A"], bd["history_30_days"], bd["prediction_today"]
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
