"""Validate newly trained model before deployment."""

import argparse
import json
import logging
import sys
from pathlib import Path

import mlflow
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_test_data():
    """Load test dataset for validation."""
    # Add your test data loading logic
    # This is a placeholder
    import pandas as pd
    test_data = pd.read_csv("data/test/test_data.csv")
    X_test = test_data.drop('target', axis=1)
    y_test = test_data['target']
    return X_test, y_test


def validate_model(min_accuracy: float = 0.75, output_file: str = None) -> bool:
    """
    Validate the latest model from MLflow.
    
    Args:
        min_accuracy: Minimum required accuracy
        output_file: Path to save validation results
        
    Returns:
        True if validation passed
    """
    # Get latest run from MLflow
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("automated-retraining")
    
    if not experiment:
        logger.error("Experiment not found")
        return False
    
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1
    )
    
    if not runs:
        logger.error("No runs found")
        return False
    
    latest_run = runs[0]
    logger.info(f"Validating run: {latest_run.info.run_id}")
    
    # Load model
    model_uri = f"runs:/{latest_run.info.run_id}/model"
    model = mlflow.sklearn.load_model(model_uri)
    
    # Load test data
    X_test, y_test = load_test_data()
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        'run_id': latest_run.info.run_id
    }
    
    # Check if meets threshold
    validation_passed = metrics['accuracy'] >= min_accuracy
    metrics['validation_passed'] = validation_passed
    
    logger.info(f"Validation Results:")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"  F1 Score: {metrics['f1_score']:.4f}")
    logger.info(f"  Validation Passed: {validation_passed}")
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    return validation_passed


def main():
    parser = argparse.ArgumentParser(description='Validate trained model')
    parser.add_argument('--min-accuracy', type=float, default=0.75)
    parser.add_argument('--output', type=str, default='validation_results.json')
    
    args = parser.parse_args()
    
    passed = validate_model(args.min_accuracy, args.output)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
