from data_loder.data_loder import DataAPI
from data_exploration.data_exploration import Statistics
from data_loder.load_local_data import load_local_data
from pathlib import Path

BASE_URL = "https://portail-api-data.montpellier3m.fr/ecocounter_timeseries"


dfs = {}


def load_api():
    global dfs
    api_client = DataAPI()
    api_client.load_api(BASE_URL)
    print("API data loaded successfully!")


def load_local():
    global dfs
    # path relative to pipeline.py
    folder_path = Path(__file__).parent.parent / "data/output"
    local_dfs = load_local_data(folder_path)
    if not local_dfs:
        print("No CSV files found in the folder!")
        return
    dfs.update(local_dfs)
    print("Local CSV data loaded successfully!")


def explore_data():
    if not dfs:
        print("No data found. Load API or local data first.")
        return

    for name, df in dfs.items():
        print(f"\n=== STATISTICS FOR {name} ===")
        stats = Statistics(df)
        stats.info()
        stats.describe()
        stats.isna()
        stats.duplicated()
        stats.outliers_rolling()


def main():
    print("\n=== PIPELINE MENU ===")
    print("1 - Load API")
    print("2 - Load Local CSVs")
    print("3 - Explore Data")
    print("4 - Load API + Explore Data")
    print("5 - Load Local + Explore Data")

    choice = input("\nEnter your choice (1-5): ")

    if choice == "1":
        load_api()
    elif choice == "2":
        load_local()
    elif choice == "3":
        explore_data()
    elif choice == "4":
        load_api()
        explore_data()
    elif choice == "5":
        load_local()
        explore_data()
    else:
        print("Invalid option!")


if __name__ == "__main__":
    main()
