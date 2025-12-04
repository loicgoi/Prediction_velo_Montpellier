import pandas as pd
import json
from datetime import datetime, timedelta

# Core imports
from core.dependencies import db_manager
from database.service import DatabaseService
from utils.logging_config import logger

# Domain imports
from download.daily_weather_api import OpenMeteoDailyAPIC
from utils.weather_utils import extract_daily_values
from features.features_engineering import FeaturesEngineering
from modeling.predictor import TrafficPredictor

def run_prediction_pipeline():
    """
    Orchestrates the Daily Prediction Pipeline (J0).
    1. Fetch today's weather forecast.
    2. Build the dataset by fetching stations and historical lags from DB.
    3. Apply Feature Engineering (Stateless).
    4. Run Inference (Prediction).
    5. Save Prediction + Context to DB.
    """
    logger.info("Starting Daily Prediction Pipeline (J0)")
    
    session = db_manager.get_session()
    service = DatabaseService(session)
    predictor = TrafficPredictor() # Loads the model

    if not predictor.model:
        logger.error("Stop: Model not loaded.")
        return

    # Key Dates
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    j_minus_7 = today - timedelta(days=7)
    
    today_str = today.strftime("%Y-%m-%d")
    logger.info(f"Target Date: {today_str}")

    try:
        # --- STEP 1: WEATHER FORECAST (J0) ---
        logger.info("1. Fetching Weather Forecast...")
        weather_client = OpenMeteoDailyAPIC()
        
        # Ensure variable order matches extraction logic
        vars_list = ["temperature_2m_mean", "wind_speed_10m_mean", "precipitation_sum"]
        
        # Coordinates for Montpellier Center
        responses = weather_client.get_weather_json(
            latitude=43.61, longitude=3.87, 
            start_date=today_str, end_date=today_str,
            daily_variables=vars_list,
            timezone="Europe/Paris"
        )
        
        # Extract scalar values
        weather_data = extract_daily_values(responses[0])
        logger.info(f"Weather for today: {weather_data}")

        # --- STEP 2: BUILD DATASET (Hybrid: DB + Weather) ---
        logger.info("2. Fetching Stations and Historical Lags from DB...")
        stations = service.get_all_stations()
        
        rows = []
        for station in stations:
            # Manual Lag Retrieval (The Mirror Strategy)
            lag_1 = service.get_bike_count(station.station_id, yesterday)
            lag_7 = service.get_bike_count(station.station_id, j_minus_7)
            
            # Skip if historical data is missing (e.g. new counter or breakdown)
            if lag_1 is None or lag_7 is None:
                continue
            
            row = {
                "date": today,
                "station_id": station.station_id,
                "latitude": float(station.latitude),
                "longitude": float(station.longitude),
                # Broadcasted Weather
                "avg_temp": weather_data['avg_temp'],
                "precipitation_mm": weather_data['precipitation_mm'],
                "vent_max": weather_data['vent_max'],
                # Injected Lags
                "lag_1": lag_1,
                "lag_7": lag_7,
                "intensity": 0 # Placeholder target
            }
            rows.append(row)
            
        if not rows:
            logger.warning("No complete station data found (missing lags).")
            return

        df_input = pd.DataFrame(rows)
        logger.info(f"Raw dataset ready: {len(df_input)} rows.")

        # --- STEP 3: FEATURE ENGINEERING ---
        fe = FeaturesEngineering(df_input)
        fe.add_week_month_year() \
          .Cycliques() \
          .add_weather_featuers() \
          .add_holidays_feature()
          # .lag() -> NE PAS DECOMMENTER
        
        df_ready = fe.get_data()

        # --- STEP 4: INFERENCE & SAVE ---
        logger.info("3. Running Inference & Saving...")
        df_pred = predictor.predict_batch(df_ready)
        
        if df_pred is not None:
            count = 0
            for _, row in df_pred.iterrows():
                # Prepare Prediction Object
                pred_data = {
                    "prediction_date": today,
                    "station_id": row['station_id'],
                    "prediction_value": int(row['predicted_intensity']),
                    "model_version": "xgboost_v1"
                }
                
                # Prepare Context JSON
                # Remove technical columns to keep JSON clean
                cols_drop = ['predicted_intensity', 'date', 'station_id', 'intensity']
                features_dict = row.drop(cols_drop, errors='ignore').to_dict()
                
                # Convert timestamps to string for JSON serialization
                features_clean = {
                    k: str(v) if isinstance(v, (pd.Timestamp, datetime)) else v 
                    for k, v in features_dict.items()
                }
                
                if service.save_prediction_single_with_context(pred_data, features_clean):
                    count += 1
            
            logger.info(f"Completed: {count} predictions saved.")

    except Exception as e:
        logger.error(f"Critical Error in Daily Pipeline: {e}", exc_info=True)
    finally:
        session.close()

if __name__ == "__main__":
    run_prediction_pipeline()