from pipelines.daily_update import run_daily_update
from pipelines.daily_predictor import run_prediction_pipeline
if __name__ == "__main__":
    run_daily_update()
    run_prediction_pipeline()
