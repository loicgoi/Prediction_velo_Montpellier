from typing import List, Dict, Any, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from .database import (
    Base,
    CounterInfo,
    BikeCount,
    Prediction,
    Weather,
    ModelMetrics,
    FeaturesData,
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

    def _bulk_add(self, model: Type[Base], data: List[Dict[str, Any]]) -> bool:
        """
        Generic method to bulk insert a list of dictionaries into a table.
        """
        if not data:
            logger.info(f"No data provided for model {model.__tablename__}. Skipping.")
            return True
        try:
            self.session.bulk_insert_mappings(model, data)
            logger.info(f"Prepared {len(data)} records for {model.__tablename__}.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error during bulk insert for {model.__tablename__}: {e}")
            return False

    def add_counter_infos(self, counters_data: List[Dict[str, Any]]) -> bool:
        """
        Add counters if they do not already exist (based on station_id).
        """
        if not counters_data:
            logger.info("No counter data provided. Skipping.")
            return True

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
            return True

        # Insertion
        try:
            self.session.bulk_insert_mappings(CounterInfo, new_counters)
            logger.info(f"Successfully inserted {len(new_counters)} new counters.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error bulk inserting counters: {e}")
            return False

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

    # --- Logique de récupération des données ---

    def get_all_stations(self) -> List[CounterInfo]:
        """Retrieves all active stations from the database."""
        return self.session.query(CounterInfo).all()

    def get_weather_for_date(self, target_date: datetime) -> Optional[Weather]:
        """Retrieves weather forecast/data for a specific date."""
        # Assuming date is stored at midnight or date-only format in DB
        return self.session.query(Weather).filter(Weather.date == target_date).first()

    def get_bike_count(self, station_id: str, target_date: datetime) -> Optional[int]:
        """
        Retrieves the real intensity for a specific station and date.
        Used to reconstruct Lags (J-1, J-7) for prediction.
        """
        result = (
            self.session.query(BikeCount.intensity)
            .filter(BikeCount.station_id == station_id)
            .filter(BikeCount.date == target_date)
            .first()
        )
        return result[0] if result else None

    def get_most_recent_bike_count(self, station_id: str) -> Optional[BikeCount]:
        """Retrieves the most recent bike count record for a station."""
        try:
            return (
                self.session.query(BikeCount)
                .filter(BikeCount.station_id == station_id)
                .order_by(BikeCount.date.desc())
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error fetching most recent count for {station_id}: {e}")
            return None

    def save_prediction_single_with_context(
        self, pred_data: Dict, features_data: Dict
    ) -> bool:
        """
        Saves ONE prediction AND its associated JSON context in a single transaction.
        Uses .flush() to retrieve the generated prediction ID before creating the context entry.
        """
        try:
            # 1. Create Prediction Object
            prediction = Prediction(**pred_data)
            self.session.add(prediction)

            # 2. Flush: Send to DB to generate prediction.id (transaction remains open)
            self.session.flush()

            # 3. Create linked FeaturesData Object
            features = FeaturesData(
                prediction_id=prediction.id,  # The Foreign Key is now available
                station_id=pred_data["station_id"],
                date=pred_data["prediction_date"],
                features=features_data,  # SQLAlchemy automatically handles Dict -> JSON conversion
                target_intensity=None,
            )
            self.session.add(features)

            # 4. Final Commit (Both rows saved together)
            self.session.commit()
            return True

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                f"Transaction failed for prediction {pred_data.get('station_id')}: {e}"
            )
            return False

    # --- Monitoring ---#

    def get_predictions_by_date(self, target_date: datetime) -> List[Prediction]:
        """
        Retrieves all predictions made for a target date.
        """
        # Filter by date
        return (
            self.session.query(Prediction)
            .filter(Prediction.prediction_date == target_date)
            .all()
        )

    def get_actuals_by_date(self, target_date: datetime) -> List[BikeCount]:
        """
        Retrieves actual counts for a given date.
        Useful for monitoring (the reality on the ground).
        """
        return self.session.query(BikeCount).filter(BikeCount.date == target_date).all()

    def get_dashboard_stats(self, station_id: str) -> Dict[str, Any]:
        """
        Retrieves and aggregates all statistics for the frontend dashboard.
        """
        today = datetime.now().date()

        # 30-day history (BikeCount)
        start_30d = today - timedelta(days=30)
        rows_30d = (
            self.session.query(BikeCount.date, BikeCount.intensity)
            .filter(BikeCount.station_id == station_id)
            .filter(BikeCount.date >= start_30d)
            .order_by(BikeCount.date.asc())
            .all()
        )
        # We just extract the intensities.
        # Note: If days are missing, the graph will be short; ideally, the gaps should be filled in.
        history_30_days = [r.intensity for r in rows_30d]

        # 7-day accuracy (Actual vs. Forecast comparison)
        start_7d = today - timedelta(days=7)

        # Past predictions
        preds_7d = (
            self.session.query(Prediction.prediction_date, Prediction.prediction_value)
            .filter(Prediction.station_id == station_id)
            .filter(Prediction.prediction_date >= start_7d)
            .filter(Prediction.prediction_date < today)  # Strictly before today
            .all()
        )
        # Real past
        reals_7d = (
            self.session.query(BikeCount.date, BikeCount.intensity)
            .filter(BikeCount.station_id == station_id)
            .filter(BikeCount.date >= start_7d)
            .filter(BikeCount.date < today)
            .all()
        )

        # Alignment via dictionary (Date -> Value)
        # We use .date() to ensure that we are comparing days, not hours.
        dict_pred = {p.prediction_date.date(): p.prediction_value for p in preds_7d}
        dict_real = {r.date.date(): r.intensity for r in reals_7d}

        dates_last_7 = [start_7d + timedelta(days=i) for i in range(7)]
        acc_real = [dict_real.get(d, 0) for d in dates_last_7]
        acc_pred = [dict_pred.get(d, 0) for d in dates_last_7]

        # Averages per day of the week (Weekly Profile)
        # We take a broad historical view (90 days)
        start_90d = today - timedelta(days=90)
        rows_90d = (
            self.session.query(BikeCount.date, BikeCount.intensity)
            .filter(BikeCount.station_id == station_id)
            .filter(BikeCount.date >= start_90d)
            .all()
        )

        week_sums = [0] * 7
        week_counts = [0] * 7

        for r in rows_90d:
            wd = r.date.weekday()  # 0=Monday, 6=Sunday
            week_sums[wd] += r.intensity
            week_counts[wd] += 1

        weekly_averages = [
            int(s / c) if c > 0 else 0 for s, c in zip(week_sums, week_counts)
        ]

        # Weekly Totals (12-week volume)
        # For now, if there is insufficient historical data, an empty safe list is returned.
        weekly_totals = [0] * 12

        return {
            "history_30_days": history_30_days,
            "accuracy_7_days": {"real": acc_real, "pred": acc_pred},
            "weekly_averages": weekly_averages,
            "weekly_totals": weekly_totals,
        }
