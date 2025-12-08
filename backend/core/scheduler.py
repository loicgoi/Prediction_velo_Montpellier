from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from apscheduler.triggers.cron import CronTrigger

from pipelines.scheduled_tasks import (
    run_full_daily_process,
)  # Assuming this file exists
from core.training_orchestrator import run_model_training
from utils.logging_config import logger

# Make a single instance of the scheduler
_scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Paris"))


def start_scheduler():
    """Configure and start the task scheduler."""
    logger.info("Initialize Scheduler")

    # Task 1: Daily data updates and predictions
    daily_trigger = CronTrigger(
        hour=8, minute=0, timezone=pytz.timezone("Europe/Paris")
    )
    # replace_existing=True allows the task to be updated if the server is restarted
    _scheduler.add_job(
        run_full_daily_process,
        trigger=daily_trigger,
        id="daily_pipeline_job",
        name="Update Data & Predict Traffic",
        replace_existing=True,
    )

    # Task 2: Monthly model retraining
    # Runs on the 1st day of the month at 2:00 AM
    monthly_trigger = CronTrigger(
        day="1", hour=2, minute=0, timezone=pytz.timezone("Europe/Paris")
    )
    _scheduler.add_job(
        run_model_training,
        trigger=monthly_trigger,
        id="monthly_training_job",
        name="Monthly Model Retraining",
        replace_existing=True,
    )

    # Launch
    try:
        _scheduler.start()
        logger.info("Scheduler started successfully.")

        # Log next run times for all jobs
        daily_job = _scheduler.get_job("daily_pipeline_job")
        monthly_job = _scheduler.get_job("monthly_training_job")
        if daily_job:
            logger.info(
                f"Daily update job scheduled. Next run: {daily_job.next_run_time}"
            )
        if monthly_job:
            logger.info(
                f"Monthly training job scheduled. Next run: {monthly_job.next_run_time}"
            )
    except Exception as e:
        logger.error(f"Error starting the scheduler: {e}")


def shutdown_scheduler():
    """Shutdown the scheduler."""
    logger.info("Shutdown Scheduler")
    try:
        _scheduler.shutdown()
        logger.info("Scheduler shutdown successfully.")
    except Exception as e:
        logger.error(f"Error shutting down the scheduler: {e}")
