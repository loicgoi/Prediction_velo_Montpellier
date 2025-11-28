import pandas as pd
from download.trafic_history_api import EcoCounterTimeseriesLoader
from utils.paths import ARCHIVE_PATH
from typing import List, Dict


def extract_station_metadata(data: List[Dict]) -> List[str]:
    """
    Extract station metadata (IDs, latitude, longitude) from raw JSON data
    and save to CSV.

    Args:
        data (List[Dict]): JSON data from EncountersIDsLoader.

    Returns:
        List[str]: List of station IDs.
    """
    print("Extracting station metadata...")
    stations_list = []
    for item in data:
        if "id" not in item:
            continue
        station_data = {"station_id": item["id"], "latitude": None, "longitude": None}
        try:
            if (
                "location" in item
                and "value" in item["location"]
                and "coordinates" in item["location"]["value"]
            ):
                coords = item["location"]["value"]["coordinates"]
                station_data["longitude"] = coords[0]
                station_data["latitude"] = coords[1]
        except Exception:
            pass
        stations_list.append(station_data)

    df = pd.DataFrame(stations_list)
    output_path = ARCHIVE_PATH / "stations_metadata.csv"
    df.to_csv(output_path, index=False)
    print(f"Station metadata saved into: {output_path}")
    print("Sample of station metadata:")
    print(df.head())
    return df, df["station_id"].tolist()


def fetch_and_extract_timeseries(
    ids_list: List[str], start_date: str = "2023-01-01", end_date: str = "2025-10-31"
) -> pd.DataFrame:
    """
    Fetch timeseries data for each station ID and save to CSV.

    Args:
        ids_list (List[str]): List of station IDs.
        start_date (str): Start date of the timeseries.
        end_date (str): End date of the timeseries.

    Returns:
        pd.DataFrame: DataFrame containing all stations' timeseries data.
    """
    print("Fetching timeseries data for stations...")
    timeseries_loader = EcoCounterTimeseriesLoader()
    responses_dict = timeseries_loader.fetch_data(
        station_ids_list=ids_list,
        start_date=start_date,
        end_date=end_date,
        timeout=5,
        retries=3,
    )

    all_records = []
    for station_id, data in responses_dict.items():
        if not data or "index" not in data or "values" not in data:
            continue
        for d, v in zip(data["index"], data["values"]):
            all_records.append({"station_id": station_id, "date": d, "intensity": v})

    df_timeseries = pd.DataFrame(all_records)
    output_path = ARCHIVE_PATH / "trafic_history.csv"
    df_timeseries.to_csv(output_path, index=False)
    print(f"Timeseries data saved into: {output_path}")
    print("Sample of timeseries data:")
    print(df_timeseries.head())
    return df_timeseries


def extract_weather_fields(
    json_data: Dict, filename: str = "weather_history.csv"
) -> pd.DataFrame:
    """
    Extract required weather fields from JSON and save into CSV.

    Args:
        json_data (Dict): Raw JSON data from WeatherHistoryLoader.
        filename (str): Name of the output CSV file.

    Returns:
        pd.DataFrame: DataFrame containing weather data.
    """
    if json_data is None:
        raise ValueError("json_data is None.")

    print("Extracting weather data...")
    daily = json_data.get("daily", {})

    dates = daily.get("time")
    avg_temp = daily.get("temperature_2m_mean")
    precipitation = daily.get("precipitation_sum")
    max_vent = daily.get("wind_speed_10m_max")

    if not (dates and avg_temp and precipitation and max_vent):
        raise ValueError("Missing required weather fields.")

    df = pd.DataFrame(
        {
            "date": dates,
            "avg_temp": avg_temp,
            "precipitation": precipitation,
            "max_vent": max_vent,
        }
    )

    output = ARCHIVE_PATH / filename
    df.to_csv(output, index=False)
    print(f"Weather data saved into: {output}")
    print("Sample of weather data:")
    print(df.head())
    return df
