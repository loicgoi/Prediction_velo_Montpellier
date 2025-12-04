from pipelines.initialize_project import (
    fetch_data_from_apis,
    explore_data,
    clean_and_aggregate,
    insert_data_into_db,
    merge_data,
    run_features_engineering,
)
from pipelines.model_training import train_model_pipeline


def main():
    df_trafic, df_weather, df_metadata = fetch_data_from_apis()
    explore_data(df_trafic, df_weather)
    df_agg = clean_and_aggregate(df_trafic)
    insert_data_into_db(df_agg, df_weather, df_metadata)
    df_final = merge_data(df_agg, df_metadata, df_weather)
    df_features = run_features_engineering(df_final)
    train_model_pipeline(df_features)


if __name__ == "__main__":
    main()
