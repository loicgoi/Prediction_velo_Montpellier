from pipelines.pipeline import (
    fetch_data_from_apis,
    explore_data,
    clean_and_aggregate,
    merge_data,
)
from pipelines.pipeline_visualization import create_features_from_csv, visualize_feature
from pipelines.data_insertion import insert_data_to_db


def main():
    print("=== Modular Pipeline Runner ===\n")
    df_trafic, df_weather, df_metadata = None, None, None
    df_agg, df_final = None, None
    fv_instance = None

    while True:
        print("\nSelect a step:")
        print("1 - Fetch data from APIs")
        print("2 - Explore data")
        print("3 - Clean and aggregate trafic data")
        print("4 - Merge data (trafic + metadata + weather)")
        print("5 - Feature visualization (Updated)")
        print("6 - Insert fetched data into Azure SQL Database")
        print("7 - Quit")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            df_trafic, df_weather, df_metadata = fetch_data_from_apis()
            print("Data fetched successfully.")

        elif choice == "2":
            if df_trafic is not None and df_weather is not None:
                explore_data(df_trafic, df_weather)
            else:
                print("Data not available. Please fetch data first.")

        elif choice == "3":
            if df_trafic is not None:
                df_agg = clean_and_aggregate(df_trafic)
                print("Trafic data cleaned and aggregated.")
            else:
                print("Fetch data first.")

        elif choice == "4":
            if (
                df_agg is not None
                and df_metadata is not None
                and df_weather is not None
            ):
                df_final = merge_data(df_agg, df_metadata, df_weather)
                print(f"Merge completed. Final dataset shape: {df_final.shape}.")
            else:
                print("Required data missing.")

        elif choice == "5":
            fv_instance = create_features_from_csv()

            if fv_instance is not None:
                while True:
                    print("\nSelect plot to show:")
                    print("1 - Intensity vs.(Day of Week, Weekend, Holidays, Season)")
                    print("2 - Intensity vs.(Temperature, Rain, Wind)")
                    print("3 - Geographic Map (Intensity Heatmap by Location)")
                    print("4 - Comparison (Intensity Distribution per Station)")
                    print(
                        "5 - Correlation Matrix (Relationships between Numeric Variables)"
                    )
                    print("6 - Show Full Dashboard (All Plots)")
                    print("7 - Back to Main Menu")

                    plot_choice = input("Choice: ").strip()

                    if plot_choice == "7":
                        break
                    visualize_feature(fv_instance, plot_choice)

            else:
                print(
                    "CSV not found. Make sure 'dataset_final.csv' exists in OUTPUT_PATH."
                )

        elif choice == "6":
            if (
                df_trafic is not None
                and df_weather is not None
                and df_metadata is not None
            ):
                insert_data_to_db(df_trafic, df_weather, df_metadata)
            else:
                print("Data not available. Please fetch data first (step 1).")

        elif choice == "7":
            print("Exiting.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
