import pandas as pd
from database.service import DatabaseService
from database.database import CounterInfo
from sqlalchemy.exc import SQLAlchemyError
from core.dependencies import db_manager
from utils.logging_config import logger
from download.geocoding_service import get_street_name_from_coords


def insert_data_to_db(
    df_agg: pd.DataFrame = None,
    df_weather: pd.DataFrame = None,
    df_metadata: pd.DataFrame = None,
):
    """
    Inserts data into the database. Handles None inputs safely.
    """
    # Setup database connection
    logger.info("Getting a database session...")
    session = db_manager.get_session()

    try:
        service = DatabaseService(session)

        # 1. Counters (Metadata) & Geocoding
        if df_metadata is not None and not df_metadata.empty:
            logger.info("Verification of new counters for geocoding...")

            # Retrieve all IDs already in the database to avoid unnecessary API calls.
            existing_ids = {
                res[0] for res in session.query(CounterInfo.station_id).all()
            }

            new_counters_list = []

            # We iterate over the DataFrame to process the counters one by one.
            for _, row in df_metadata.iterrows():
                station_id = str(row["station_id"])

                # If the counter is NOT in the database, it's a new one!
                if station_id not in existing_ids:
                    lat = row["latitude"]
                    lon = row["longitude"]

                    logger.info(f"Geocoding of the new counter: {station_id}...")

                    # Call to the Nominatim API (with pause included in the function)
                    street_name = get_street_name_from_coords(lat, lon)

                    # Fallback if API fails or finds nothing
                    final_name = (
                        street_name if street_name else f"Compteur {station_id}"
                    )

                    new_counters_list.append(
                        {
                            "station_id": station_id,
                            "latitude": lat,
                            "longitude": lon,
                            "name": final_name,
                        }
                    )

            # Insert only if new counters have been found
            if new_counters_list:
                logger.info(
                    f"Insertion of {len(new_counters_list)} new counters with street names..."
                )
                service.add_counter_infos(new_counters_list)
            else:
                logger.info("No new counter detected (no geocoding required).")

        else:
            logger.info("No metadata to insert (None or empty).")

        # 2. Traffic (BikeCount)
        if df_agg is not None and not df_agg.empty:
            counts_data = df_agg.to_dict(orient="records")
            logger.info(f"Envoi de {len(counts_data)} données de trafic...")
            service.add_bike_counts(counts_data)
        else:
            logger.info("No traffic data to insert.")

        # 3. Weather
        if df_weather is not None and not df_weather.empty:
            weather_data = df_weather.to_dict(orient="records")
            logger.info(f"Envoi de {len(weather_data)} données météo...")
            service.add_weather_data(weather_data)
        else:
            logger.info("No weather data to insert.")

        logger.info("Commit transaction...")
        session.commit()
        logger.info("Data insertion process completed successfully.")

    except SQLAlchemyError as e:
        logger.error(f"A database error has occurred: {e}", exc_info=True)
        session.rollback()
    except Exception as e:
        logger.error(f"An unexpected error has occurred: {e}", exc_info=True)
    finally:
        session.close()
        logger.info("Session closed.")