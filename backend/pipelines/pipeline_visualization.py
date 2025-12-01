import pandas as pd
from utils.paths import OUTPUT_PATH
from features.features_visualization import FeaturesVisualization


def create_features_from_csv(filename="dataset_final.csv"):
    """
    Load CSV and return FeaturesVisualization instance.
    """
    file_path = OUTPUT_PATH / filename
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

    fv = FeaturesVisualization(df)
    return fv


def visualize_feature(fv_instance, user_choice):
    """
    Show plots based on user input (ID or name).
    Handles the mapping internally.
    """
    if fv_instance is None:
        print("No data available to visualize.")
        return

    mapping = {
        "1": "temporal",
        "2": "weather",
        "3": "spatial",
        "4": "station",
        "5": "correlation",
        "6": "all",
    }

    plot_type = mapping.get(user_choice, user_choice)

    if plot_type == "temporal":
        fv_instance.plot_temporal_features()
    elif plot_type == "weather":
        fv_instance.plot_weather_features()
    elif plot_type == "spatial":
        fv_instance.plot_spatial_features()
    elif plot_type == "station":
        fv_instance.plot_station_effect()
    elif plot_type == "correlation":
        fv_instance.plot_correlation_heatmap()
    elif plot_type == "all":
        fv_instance.show_all_plots()
    else:
        print(f"Invalid plot choice: {user_choice}")
