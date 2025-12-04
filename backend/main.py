from pipelines.pipeline import (
    fetch_data_from_apis,
    explore_data,
    clean_and_aggregate,
    merge_data,
    run_features_engineering,
)
from pipelines.pipeline_visualization import create_features_from_csv, visualize_feature
from core.dependencies import db_manager
from pipelines.data_insertion import insert_data_to_db
from pipelines.model_training import train_model_pipeline


def main():
    print("=== Modular Pipeline Runner ===\n")
    df_trafic, df_weather, df_metadata = None, None, None
    df_agg, df_final = None, None

    # Variable pour stocker le résultat du Feature Engineering (Input du modèle)
    final_df = None
    fv_instance = None

    while True:
        print("\nSelect a step:")
        print("1 - Fetch data from APIs")
        print("2 - Explore data")
        print("3 - Clean and aggregate trafic data")
        print("4 - Merge data (trafic + metadata + weather)")
        print("5 - Load CSV for Visualization")
        print("6 - Feature Visualization")
        print("7 - Insert fetched data into Azure SQL Database")
        print("8 - Run Feature Engineering")
        print("9 - Train Model (XGBoost)")
        print("10 - Quit")

        choice = input("Enter your choice (1-10): ").strip()

        # 1. Fetch Data
        if choice == "1":
            df_trafic, df_weather, df_metadata = fetch_data_from_apis()
            print("Data fetched successfully.")

        # 2. Explore Data
        elif choice == "2":
            if df_trafic is not None and df_weather is not None:
                explore_data(df_trafic, df_weather)
            else:
                print("Data not available. Please fetch data first.")

        # 3. Clean & Aggregate Traffic
        elif choice == "3":
            if df_trafic is not None:
                df_agg = clean_and_aggregate(df_trafic)
                print("Trafic data cleaned and aggregated.")
            else:
                print("Fetch data first.")

        # 4. Merge Data
        elif choice == "4":
            if (
                df_agg is not None
                and df_metadata is not None
                and df_weather is not None
            ):
                df_final = merge_data(df_agg, df_metadata, df_weather)
                print(f"Merge completed. Final dataset shape: {df_final.shape}.")
            else:
                print("Required data missing. Run steps 1 and 3 first.")

        # 5. Load CSV for Visualization
        elif choice == "5":
            fv_instance = create_features_from_csv()
            if fv_instance is not None:
                print("CSV loaded successfully for visualization.")
            else:
                print("CSV not found. Make sure 'dataset_final.csv' exists.")

        # 6. Visualization (ONLY if CSV already loaded)
        elif choice == "6":
            if fv_instance is None:
                print("No CSV loaded. Please run step 5 first.")
                continue

            while True:
                print("\nSelect plot to show:")
                print("1 - Intensity vs.(Day of Week, Weekend, Holidays, Season)")
                print("2 - Intensity vs.(Temperature, Rain, Wind)")
                print("3 - Geographic Map (Intensity Heatmap by Location)")
                print("4 - Comparison (Intensity Distribution per Station)")
                print("5 - Correlation Matrix")
                print("6 - Show Full Dashboard")
                print("7 - Back to Main Menu")

                plot_choice = input("Choice: ").strip()
                if plot_choice == "7":
                    break

                visualize_feature(fv_instance, plot_choice)

        # 7. Insert Data into Azure SQL
        elif choice == "7":
            if (
                df_agg is not None
                and df_weather is not None
                and df_metadata is not None
            ):
                print("\n--- Step 7: Azure SQL Database ---")

                print("1. Checking database structure...")
                try:
                    db_manager.init_db()
                    print("Database structure validated.")
                except Exception as e:
                    print(f"Critical DB error: {e}")
                    continue

                print("2. Inserting data...")
                insert_data_to_db(df_agg, df_weather, df_metadata)

            else:
                print("Missing data. Run steps 1, 3, and 4 first.")

        # 8. Run Feature Engineering
        elif choice == "8":
            if df_final is not None:
                final_df = run_features_engineering(df_final)

                print(
                    f"[INFO] Feature engineering completed. Final dataset shape: {final_df.shape}"
                )
            else:
                print("[WARNING] Merged data not available. Run step 4 first.")

        # 9. Train Model
        elif choice == "9":
            if final_df is not None:
                print("[INFO] Starting Model Training Pipeline...")
                train_model_pipeline(final_df)
                print("\n" + "=" * 40)
                print("Training done successfully !")
                print("Trained model & processor saved in 'backend/data/models/.")
                print("=" * 40 + "\n")
            else:
                print(
                    "[WARNING] No processed data found. Run step 8 (Feature Engineering) first."
                )

        # 10. Quit
        elif choice == "10":
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice. Please choose a number between 1 and 10.")


if __name__ == "__main__":
    main()
