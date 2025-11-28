from pipelines.pipeline import (
    fetch_data_from_apis,
    explore_data,
    clean_and_aggregate,
    merge_data,
)


def main():
    print("=== Modular Pipeline Runner ===\n")

    # Data placeholders
    df_trafic, df_weather, df_metadata = None, None, None
    df_agg, df_final = None, None

    while True:
        print("\nSelect a step to run:")
        print("1 - Fetch data from APIs")
        print("2 - Explore data")
        print("3 - Clean and aggregate trafic data")
        print("4 - Merge data (trafic + metadata + weather)")
        print("5 - Quit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            df_trafic, df_weather, df_metadata = fetch_data_from_apis()

        elif choice == "2":
            if df_trafic is not None and df_weather is not None:
                explore_data(df_trafic, df_weather)
            else:
                print("Data not available. Please fetch data from APIs first.")

        elif choice == "3":
            if df_trafic is not None:
                df_agg = clean_and_aggregate(df_trafic)
            else:
                print("Trafic data not available. Please fetch data first.")

        elif choice == "4":
            if (
                df_agg is not None
                and df_metadata is not None
                and df_weather is not None
            ):
                df_final = merge_data(df_agg, df_metadata, df_weather)
                print(f"Merge completed. Final dataset is ready{df_final.shape}.")
            else:
                print("Required data missing. Make sure to fetch and clean data first.")

        elif choice == "5":
            print("Exiting pipeline runner.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
