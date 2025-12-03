from nicegui import ui, app

from components import render_counter_content
from data import MOCK_COUNTERS


# UI
@ui.page("/")
def index():
    """Main entry point of the application and definition of the layout."""
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
        # The content is rendered here and will be refreshed by the on_change event of the select element.
        render_counter_content(app.storage.client["selected_station_id"])


ui.run()
