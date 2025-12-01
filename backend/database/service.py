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

    def _bulk_add(self, model: Base, data: List[Dict[str, Any]]):  # type: ignore
        """
        Generic method to bulk insert a list of dictionaries into a table.
        """
        if not data:
            logger.info(f"No data provided for model {model.__tablename__}. Skipping.")
            return
        self.session.bulk_insert_mappings(model, data)
        logger.info(f"Prepared {len(data)} records for {model.__tablename__}.")

    def add_counter_infos(self, counters_data: List[Dict[str, Any]]):
        """
        Add counters if they do not already exist (based on station_id).
        """
        if not counters_data:
            logger.info("No counter data provided. Skipping.")
            return

        # Retrieve all existing IDs in the database
        existing_ids = {
            res[0] for res in self.session.query(CounterInfo.station_id).all()
        }

        # Filter the incoming list
        new_counters = []
        seen_ids_in_batch = set()

        for counter in counters_data:
            s_id = counter.get("station_id")

            # If the ID already exists in the database -> Ignore
            if s_id in existing_ids:
                continue

            # If it has already been seen in the current file -> Ignore (CSV duplicate)
            if s_id in seen_ids_in_batch:
                continue

            # It's a real new counter.
            seen_ids_in_batch.add(s_id)
            new_counters.append(counter)

        if not new_counters:
            logger.info("All provided counters already exist.")
            return

        # Insertion
        try:
            self.session.bulk_insert_mappings(CounterInfo, new_counters)
            logger.info(f"Successfully inserted {len(new_counters)} new counters.")
        except SQLAlchemyError as e:
            logger.error(f"Error bulk inserting counters: {e}")
            raise e

    def add_bike_counts(self, counts_data: List[Dict[str, Any]]):
        """Adds multiple bike count records to the database."""
        return self._bulk_add(BikeCount, counts_data)

    def add_weather_data(self, weather_data: List[Dict[str, Any]]):
        """Adds multiple weather records to the database."""
        return self._bulk_add(Weather, weather_data)

    def add_predictions(self, predictions_data: List[Dict[str, Any]]):
        """Add multiple predictions records to the database"""
        return self._bulk_add(Prediction, predictions_data)

    def add_model_metrics(self, model_metrics: List[Dict[str, Any]]):
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
