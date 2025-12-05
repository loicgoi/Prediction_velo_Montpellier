from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from apscheduler.triggers.cron import CronTrigger

from pipelines.scheduled_tasks import run_full_daily_process
from utils.logging_config import logger

# Make a single instance of the scheduler
_scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Paris"))


def start_scheduler():
    """Configure and start the task scheduler."""
    logger.info("Initialize Scheduler")

    # Configure Trigger
    trigger = CronTrigger(hour=8, minute=0, timezone=pytz.timezone("Europe/Paris"))

    # Add job
    # replace_existing=True allows the task to be updated if the server is restarted
    _scheduler.add_job(
        run_full_daily_process,
        trigger=trigger,
        id="daily_pipeline_job",
        name="Update Data & Predict Traffic",
        replace_existing=True,
    )

    # Launch
    try:
        _scheduler.start()
        logger.info("Scheduler started successfully.")
        job = _scheduler.get_job("daily_pipeline_job")
        if job:
            logger.info(f"Next run: {job.next_run_time}")
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
