"""
Ensemble Model: Combining Multiple Models for Better Predictions
"""

import logging
import yaml
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestRegressor, 
    GradientBoostingRegressor,
    VotingRegressor,
    StackingRegressor
)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import mlflow
import mlflow.sklearn
from datetime import datetime
import os

import sys
sys.path.append('.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnsembleModel:
    """Ensemble model combining multiple regressors"""
    
    def __init__(self, config_path: str = "config/config.yaml",
                 model_config_path: str = "config/model_config_improved.yaml"):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        with open(model_config_path, 'r') as f:
            self.model_config = yaml.safe_load(f)
        
        mlflow.set_tracking_uri(self.config['mlflow']['tracking_uri'])
        mlflow.set_experiment(self.config['mlflow']['experiment_name'])
        
        self.ensemble_model = None
    
    def create_voting_ensemble(self):
        """Create a voting ensemble"""
        
        logger.info("Creating voting ensemble...")
        
        # Base models with optimized parameters
        rf = RandomForestRegressor(**self.model_config['random_forest'])
        gb = GradientBoostingRegressor(**self.model_config['gradient_boosting'])
        
        # Voting ensemble
        ensemble = VotingRegressor(
            estimators=[
                ('random_forest', rf),
                ('gradient_boosting', gb)
            ],
            weights=[0.4, 0.6]  # GB typically performs better
        )
        
        return ensemble
    
    def create_stacking_ensemble(self):
        """Create a stacking ensemble (meta-learning)"""
        
        logger.info("Creating stacking ensemble...")
        
        # Base models
        rf = RandomForestRegressor(**self.model_config['random_forest'])
        gb = GradientBoostingRegressor(**self.model_config['gradient_boosting'])
        
        # Meta-learner (simpler model to avoid overfitting)
        meta_learner = Ridge(alpha=1.0)
        
        # Stacking ensemble
        ensemble = StackingRegressor(
            estimators=[
                ('random_forest', rf),
                ('gradient_boosting', gb)
            ],
            final_estimator=meta_learner,
            cv=5  # Cross-validation for base models
        )
        
        return ensemble
    
    def calculate_metrics(self, y_true, y_pred) -> dict:
        """Calculate regression metrics"""
        
        mae = mean_absolute_error(y_true, y_preda)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'mape': mape
        }
    
    def train(self, X_train, X_test, y_train, y_test, ensemble_type='stacking'):
        """Train ensemble model"""
        
        with mlflow.start_run(run_name=f"ensemble_{ensemble_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Create ensemble
            if ensemble_type == 'voting':
                self.ensemble_model = self.create_voting_ensemble()
            elif ensemble_type == 'stacking':
                self.ensemble_model = self.create_stacking_ensemble()
            else:
                raise ValueError(f"Unknown ensemble type: {ensemble_type}")
            
            # Log parameters
            mlflow.log_param("ensemble_type", ensemble_type)
            mlflow.log_param("n_base_models", len(self.ensemble_model.estimators))
            
            # Train
            logger.info(f"Training {ensemble_type} ensemble...")
            self.ensemble_model.fit(X_train, y_train)
            logger.info("Training complete!")
            
            # Predictions
            y_train_pred = self.ensemble_model.predict(X_train)
            y_test_pred = self.ensemble_model.predict(X_test)
            
            # Metrics
            train_metrics = self.calculate_metrics(y_train, y_train_pred)
            test_metrics = self.calculate_metrics(y_test, y_test_pred)
            
            # Log metrics
            for metric_name, metric_value in train_metrics.items():
                mlflow.log_metric(f"train_{metric_name}", metric_value)
                logger.info(f"Train {metric_name}: {metric_value:.4f}")
            
            for metric_name, metric_value in test_metrics.items():
                mlflow.log_metric(f"test_{metric_name}", metric_value)
                logger.info(f"Test {metric_name}: {metric_value:.4f}")
            
            # Calculate improvement over baseline
            baseline_test_rmse = 50403.94  # Your current model's test RMSE
            improvement = ((baseline_test_rmse - test_metrics['rmse']) / baseline_test_rmse) * 100
            mlflow.log_metric("improvement_percentage", improvement)
            logger.info(f"\nImprovement over baseline: {improvement:.2f}%")
            
            # Log model
            mlflow.sklearn.log_model(self.ensemble_model, "model")
            
            # Save model
            os.makedirs('models', exist_ok=True)
            model_path = f"models/ensemble_{ensemble_type}_model.pkl"
            joblib.dump(self.ensemble_model, model_path)
            logger.info(f"\nModel saved to {model_path}")
            
            return self.ensemble_model


def main():
    """Train ensemble models"""
    from src.data.ingestion import DataIngestion
    from src.data.preprocessing_improved import EnhancedDataPreprocessor
    
    logger.info("="*60)
    logger.info("ENSEMBLE MODEL TRAINING")
    logger.info("="*60)
    
    # Load and preprocess data
    logger.info("\n[1/2] Loading and preprocessing data...")
    ingestion = DataIngestion()
    df = ingestion.ingest()
    
    preprocessor = EnhancedDataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.preprocess(df)
    preprocessor.save_preprocessor("models/preprocessor_enhanced.pkl")
    
    # Train ensemble models
    logger.info("\n[2/2] Training ensemble models...")
    
    ensemble = EnsembleModel()
    
    # Try both voting and stacking
    logger.info("\n--- Voting Ensemble ---")
    voting_model = ensemble.train(X_train, X_test, y_train, y_test, ensemble_type='voting')
    
    logger.info("\n--- Stacking Ensemble ---")
    stacking_model = ensemble.train(X_train, X_test, y_train, y_test, ensemble_type='stacking')
    
    logger.info("\n" + "="*60)
    logger.info("ENSEMBLE TRAINING COMPLETE!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
