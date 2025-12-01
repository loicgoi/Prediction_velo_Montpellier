from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError

from .database import (
    Base,
    CounterInfo,
    BikeCount,
    Prediction,
    Weather,
    ModelMetrics,
)
from utils.logging_config import logger


class DatabaseService:
    """
    Service layer for database operations.
    This class abstracts the database session and provides
    methods to interact with the data models.
    """

    def __init__(self, session: Session):
        self.session = session

    def _bulk_add(self, model: Base, data: List[Dict[str, Any]]) -> bool:  # type: ignore
        """
        Generic method to bulk insert a list of dictionaries into a table.

        :param model: The SQLAlchemy model class (e.g., BikeCount).
        :param data: A list of dictionaries, where each dictionary represents a row.
        :return: True if successful, False otherwise.
        """
        if not data:
            logger.info(f"No data provided for model {model.__tablename__}. Skipping.")
            return True

        try:
            self.session.bulk_insert_mappings(model, data)
            self.session.commit()
            logger.info(
                f"Successfully inserted {len(data)} records into {model.__tablename__}."
            )
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                f"Error bulk inserting into {model.__tablename__}: {e}", exc_info=True
            )
            return False

    def add_counter_infos(self, counters_data: List[Dict[str, Any]]) -> bool:
        """
        Adds multiple counter information records to the database.
        It checks for existence based on (longitude, latitude) to prevent duplicates,
        as the counter 'id' might not be a stable unique identifier.
        """
        if not counters_data:
            logger.info("No counter data provided. Skipping.")
            return True

        try:
            # Fetch all existing coordinates into a set for fast lookups.
            existing_coords = {
                (c.longitude, c.latitude)
                for c in self.session.query(
                    CounterInfo.longitude, CounterInfo.latitude
                ).all()
            }

            # Filter the incoming data to find only the truly new counters.
            new_counters = [
                counter
                for counter in counters_data
                if (
                    Decimal(str(counter.get("longitude"))),
                    Decimal(str(counter.get("latitude"))),
                )
                not in existing_coords
            ]

            if not new_counters:
                logger.info("All provided counters already exist in the database.")
                return True

            # Bulk insert only the new counters.
            self.session.bulk_insert_mappings(CounterInfo, new_counters)  # type: ignore
            self.session.commit()
            logger.info(f"Successfully inserted {len(new_counters)} new counters.")
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error adding new counter info: {e}", exc_info=True)
            return False

    def add_bike_counts(self, counts_data: List[Dict[str, Any]]) -> bool:
        """Adds multiple bike count records to the database."""
        return self._bulk_add(BikeCount, counts_data)

    def add_weather_data(self, weather_data: List[Dict[str, Any]]) -> bool:
        """Adds multiple weather records to the database."""
        return self._bulk_add(Weather, weather_data)

    def add_predictions(self, predictions_data: List[Dict[str, Any]]) -> bool:
        """Add multiple predictions records to the database"""
        return self._bulk_add(Prediction, predictions_data)

    def add_model_metrics(self, model_metrics: List[Dict[str, Any]]) -> bool:
        """Add multiples model metrics records to the database"""
        return self._bulk_add(ModelMetrics, model_metrics)

    def get_latest_prediction_for_counter(
        self, station_id: str
    ) -> Optional[Prediction]:
        """
        Retrieves the most recent prediction for a given counter.
        """
        try:
            result = (
                self.session.query(Prediction)
                .filter(Prediction.station_id == station_id)
                .order_by(Prediction.prediction_date.desc())
                .first()
            )
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error fetching prediction for counter {station_id}: {e}")
            return None
