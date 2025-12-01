from download.ecocounters_ids import EncountersIDsLoader
from download.weeather_api import WeatherHistoryLoader
from src.data_exploration import Statistics
from src.data_cleaner import drop_duplicate, agregate
from src.api_data_processing import (
    extract_station_metadata,
    fetch_and_extract_timeseries,
    extract_weather_fields,
)
from src.data_merger import merge_trafic_with_metadata, merge_trafic_with_weather


def fetch_data_from_apis():
    """Fetch trafic, weather, and metadata from APIs"""
    print("Fetching data...")
    df_metadata, ids = extract_station_metadata(EncountersIDsLoader().fetch_data())
    if not ids:
        print("No station IDs found.")
        return None, None, None
    df_trafic = fetch_and_extract_timeseries(ids)
    df_weather = extract_weather_fields(WeatherHistoryLoader().fetch_data())
    print("Data fetching done.\n")
    return df_trafic, df_weather, df_metadata


def explore_data(df_trafic, df_weather):
    """Explore trafic and weather data"""
    print("Exploring data...\n")
    stats = Statistics(
        [df_trafic, df_weather], names=["Trafic History", "Weather History"]
    )
    stats.info()
    stats.describe()
    stats.isna()
    stats.duplicated()
    print("Data exploration done.\n")


def clean_and_aggregate(df_trafic):
    """Drop duplicates and aggregate trafic data"""
    df_clean = drop_duplicate(df_trafic)
    df_agg = agregate(df_clean)
    print("Data aggregation done.\n")
    return df_agg


def merge_data(df_agg, df_metadata, df_weather):
    """Merge trafic, metadata, and weather"""
    df_trafic_coords = merge_trafic_with_metadata(df_agg, df_metadata)
    df_final = merge_trafic_with_weather(df_trafic_coords, df_weather)
    print(f"Data merged. Final shape: {df_final.shape}")
    return df_final
