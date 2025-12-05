from nicegui import ui, app

from components import render_counter_content
from data import get_all_counters, get_counter_by_id


# UI
@ui.page("/")
def index():
    """Main entry point of the application and definition of the layout."""
    all_counters = get_all_counters()

    if not all_counters:
        with ui.column().classes("w-full max-w-5xl mx-auto p-4 mt-20"):
            ui.label(
                "Erreur: Impossible de charger les données des compteurs depuis le backend."
            ).classes("text-xl text-red-600 font-bold")
            ui.label(
                "Veuillez vérifier que l'API FastAPI est bien lancée sur http://localhost:8000/"
            ).classes("text-lg")
        return

    default_id = all_counters[0]["station_id"]

    if "selected_station_id" not in app.storage.client:
        app.storage.client["selected_station_id"] = default_id

    options = {counter["station_id"]: counter["name"] for counter in all_counters}

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
        # The content is rendered here and will be refreshed by the on_change event of the select element.
        render_counter_content(app.storage.client["selected_station_id"])


ui.run()
