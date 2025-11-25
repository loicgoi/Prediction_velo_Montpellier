from data_loder.data_loder import DataAPI, DATA_PATH


def main():
    api_client = DataAPI()
    api_client.load_csv(DATA_PATH / "stations_ids.csv")
    BASE_URL = "https://portail-api-data.montpellier3m.fr/ecocounter_timeseries"
    results = api_client.load_api(BASE_URL)
    if results:
        first_station = list(results.keys())[0]
        print(f"\nFirst station ({first_station}) sample data:")
        print(results[first_station].head())


if __name__ == "__main__":
    main()
