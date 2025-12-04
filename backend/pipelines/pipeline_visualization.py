import pandas as pd
from utils.paths import OUTPUT_PATH
from features.features_visualization import FeaturesVisualization
from utils.logging_config import logger


def create_features_from_csv(filename="dataset_final.csv"):
    """
    Load CSV file and return FeaturesVisualization instance.

    Args:
        filename (str): Name of the CSV file in OUTPUT_PATH.

    Returns:
        FeaturesVisualization instance or None if file not found.
    """
    file_path = OUTPUT_PATH / filename
    try:
        df = pd.read_csv(file_path)
        logger.info(f"CSV loaded successfully: {file_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None

    fv = FeaturesVisualization(df)
    return fv


def visualize_feature(fv_instance, user_choice):
    """
    Show plots based on user input.

    Args:
        fv_instance (FeaturesVisualization): Instance with loaded data.
        user_choice (str): Choice of plot, either ID ("1"-"6") or name ("temporal", etc.)
    """
    if fv_instance is None:
        logger.warning("No data available to visualize.")
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
        logger.error(f"Invalid plot choice: {user_choice}")


def main():
    """
    Main function to run feature visualization interactively.
    """
    fv_instance = create_features_from_csv()

    if fv_instance is None:
        logger.error("Cannot proceed without data. Exiting.")
        return

    print("\nChoose which plot to display:")
    print("1: Temporal Features")
    print("2: Weather Features")
    print("3: Spatial Features")
    print("4: Station Effect")
    print("5: Correlation Heatmap")
    print("6: All Plots")
    user_choice = input("Enter the number or name of the plot: ").strip().lower()

    visualize_feature(fv_instance, user_choice)


if __name__ == "__main__":
    main()
