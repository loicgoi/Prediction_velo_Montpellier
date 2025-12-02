import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from decimal import Decimal

from pipelines.data_insertion import insert_data_to_db
from database.database import CounterInfo, BikeCount, Weather


def test_insert_data_to_db(db_session):
    """
    Tests the data insertion pipeline function.
    It checks if the data from DataFrames is correctly inserted into the test database.
    """
    # Create sample data
    df_metadata = pd.DataFrame(
        [
            {
                "station_id": "counter-1",
                "name": "Counter One",
                "longitude": "4.835654",
                "latitude": "45.764043",
            },
            {
                "station_id": "counter-2",
                "name": "Counter Two",
                "longitude": "4.835655",
                "latitude": "45.764044",
            },
        ]
    )

    df_trafic = pd.DataFrame(
        [
            {
                "date": datetime(2023, 10, 26, 10, 0, 0),
                "station_id": "counter-1",
                "intensity": 150,
            },
            {
                "date": datetime(2023, 10, 26, 11, 0, 0),
                "station_id": "counter-1",
                "intensity": 120,
            },
        ]
    )

    df_weather = pd.DataFrame(
        [
            {
                "date": datetime(2023, 10, 26, 10, 0, 0),
                "avg_temp": 15.5,
                "precipitation_mm": 0.2,
                "vent_max": 25.0,
            }
        ]
    )

    # Mock the DatabaseManager
    # We intercept the creation of DatabaseManager to inject our test session.
    mock_db_manager = MagicMock()
    mock_db_manager.get_session.return_value = db_session

    # The 'patch' ensures that any call to DatabaseManager() inside the 'with' block
    # will return our mock_db_manager instead of creating a real one.
    with patch(
        "pipelines.data_insertion.DatabaseManager", return_value=mock_db_manager
    ):
        # Act: Call the function to be tested
        insert_data_to_db(df_trafic, df_weather, df_metadata)

    # Assert: Verify the data was inserted correctly
    # Query the test database to see what was actually inserted.
    counters_in_db = db_session.query(CounterInfo).all()
    counts_in_db = db_session.query(BikeCount).all()
    weather_in_db = db_session.query(Weather).all()

    # Check if the number of records is correct
    assert len(counters_in_db) == 2
    assert len(counts_in_db) == 2
    assert len(weather_in_db) == 1

    # Check some specific values to be sure
    assert counters_in_db[0].station_id == "counter-1"
    assert counters_in_db[0].name == "Counter One"
    assert counters_in_db[0].longitude == Decimal("4.835654")

    assert counts_in_db[0].station_id == "counter-1"
    assert counts_in_db[0].intensity == 150

    assert weather_in_db[0].avg_temp == 15.5
