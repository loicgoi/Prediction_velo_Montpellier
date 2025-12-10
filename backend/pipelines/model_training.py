import pandas as pd
from modeling.preprocessor import DataPreprocessor
from modeling.trainer import ModelTrainer
from utils.logging_config import logger

def train_model_pipeline(df: pd.DataFrame):
    """
    Orchestrates the complete training pipeline.
    
    Strategy:
    1. EVALUATION PHASE: Split data (Train/Test) to compute metrics (RMSE/MAE).
       -> This validates the model architecture.
    2. PRODUCTION PHASE: Re-train on 100% of data.
       -> This ensures the saved model knows ALL stations (including recent ones).
       -> This solves the "unknown label" issue for new counters.
    """
    logger.info("--- Starting Model Training Pipeline ---")

    # 0. Basic Validation
    if df is None or df.empty:
        logger.error("Empty dataset. Cannot train.")
        return

    # Ensure chronological order (Crucial for Time Series)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by=['date', 'station_id'])
    
    logger.info(f"Total Dataset size: {len(df)} rows.")

    # ==========================================
    # PHASE 1: EVALUATION (Train/Test Split)
    # ==========================================
    logger.info("--- PHASE 1: Evaluation (Split) ---")
    
    # Define split date (adjust based on your actual data range)
    cutoff_date = "2025-09-01"
    
    train_df = df[df['date'] < cutoff_date].copy()
    test_df = df[df['date'] >= cutoff_date].copy()
    
    if len(train_df) > 0 and len(test_df) > 0:
        logger.info(f"Split Date: {cutoff_date}")
        logger.info(f"Train set: {len(train_df)} | Test set: {len(test_df)}")

        try:
            # 1. Fit Preprocessor on TRAIN only (to avoid leakage during eval)
            eval_preprocessor = DataPreprocessor()
            eval_preprocessor.fit(train_df)
            
            X_train, y_train = eval_preprocessor.transform(train_df)
            # Note: transforming test_df might trigger warnings for new stations 
            # appearing after Sept 2025. This is expected behavior for evaluation.
            X_test, y_test = eval_preprocessor.transform(test_df)

            # 2. Train Evaluator Model
            eval_trainer = ModelTrainer()
            eval_trainer.train(X_train, y_train)
            
            # 3. Compute Metrics
            eval_trainer.evaluate(X_test, y_test)
            
        except Exception as e:
            logger.warning(f"Evaluation phase failed (non-blocking): {e}")
    else:
        logger.warning("Not enough data to perform a split. Skipping evaluation phase.")

    # ==========================================
    # PHASE 2: PRODUCTION (Full Retrain)
    # ==========================================
    logger.info("--- PHASE 2: Production Retraining (Full Dataset) ---")
    
    try:
        # 1. Instantiate NEW objects
        prod_preprocessor = DataPreprocessor()
        prod_trainer = ModelTrainer()
        
        # 2. Fit on FULL dataset
        # This is the critical step: the LabelEncoder will learn ALL station IDs here.
        logger.info("Fitting preprocessor on 100% of data...")
        prod_preprocessor.fit(df)
        
        X_full, y_full = prod_preprocessor.transform(df)
        
        # 3. Train on FULL dataset
        logger.info("Training XGBoost on 100% of data...")
        prod_trainer.train(X_full, y_full)
        
        # 4. Save Artifacts
        # These files will be used by the Predictor in daily operations
        prod_trainer.save("xgboost_v1.pkl")
        prod_preprocessor.save("preprocessor_v1.pkl")
        
        logger.info("Production model and preprocessor saved successfully.")
        logger.info("The model is now aware of all stations present in the dataset.")

    except Exception as e:
        logger.error(f"Critical error during production training: {e}")