"""Script to run monitoring checks on production data."""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring.monitoring_service import MonitoringService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run monitoring on production data."""
    parser = argparse.ArgumentParser(description='Run model monitoring')
    parser.add_argument(
        '--data-path',
        type=str,
        required=True,
        help='Path to current production data (CSV or Parquet)'
    )
    parser.add_argument(
        '--predictions-path',
        type=str,
        help='Path to predictions file (optional)'
    )
    parser.add_argument(
        '--labels-path',
        type=str,
        help='Path to true labels file (optional)'
    )
    parser.add_argument(
        '--model-version',
        type=str,
        default='unknown',
        help='Current model version'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/monitoring_config.json',
        help='Path to monitoring config'
    )
    
    args = parser.parse_args()
    
    # Load data
    logger.info(f"Loading production data from {args.data_path}")
    data_path = Path(args.data_path)
    
    if data_path.suffix == '.csv':
        current_data = pd.read_csv(data_path)
    elif data_path.suffix == '.parquet':
        current_data = pd.read_parquet(data_path)
    else:
        raise ValueError(f"Unsupported file format: {data_path.suffix}")
    
    logger.info(f"Loaded {len(current_data)} samples")
    
    # Load predictions and labels if provided
    y_pred = None
    y_true = None
    
    if args.predictions_path:
        pred_path = Path(args.predictions_path)
        if pred_path.suffix == '.csv':
            y_pred = pd.read_csv(pred_path).iloc[:, 0]
        else:
            y_pred = pd.read_parquet(pred_path).iloc[:, 0]
        logger.info(f"Loaded {len(y_pred)} predictions")
    
    if args.labels_path:
        labels_path = Path(args.labels_path)
        if labels_path.suffix == '.csv':
            y_true = pd.read_csv(labels_path).iloc[:, 0]
        else:
            y_true = pd.read_parquet(labels_path).iloc[:, 0]
        logger.info(f"Loaded {len(y_true)} true labels")
    
    # Run monitoring
    logger.info("Initializing monitoring service...")
    monitor = MonitoringService(config_path=args.config)
    
    logger.info("Running monitoring checks...")
    results = monitor.check_production_data(
        current_data=current_data,
        y_true=y_true,
        y_pred=y_pred,
        model_version=args.model_version
    )
    
    # Print results
    logger.info("=" * 60)
    logger.info("MONITORING RESULTS")
    logger.info("=" * 60)
    logger.info(f"Model Version: {results['model_version']}")
    logger.info(f"Drift Detected: {results['drift_detected']}")
    
    if 'drift_metrics' in results:
        logger.info(f"  Drift Share: {results['drift_metrics']['drift_share']:.2%}")
        logger.info(f"  Drifted Columns: {results['drift_metrics']['number_of_drifted_columns']}")
    
    if 'performance_degraded' in results:
        logger.info(f"Performance Degraded: {results['performance_degraded']}")
    
    if 'performance_metrics' in results:
        pm = results['performance_metrics']
        logger.info(f"  Accuracy: {pm['accuracy']:.4f}")
        logger.info(f"  F1 Score: {pm['f1_score']:.4f}")
    
    logger.info(f"Retraining Triggered: {results['retraining_triggered']}")
    logger.info("=" * 60)
    
    # Exit with error code if retraining was triggered
    if results['retraining_triggered']:
        logger.warning("Automated retraining has been triggered!")
        sys.exit(2)  # Special exit code for retraining trigger
    
    sys.exit(0)


if __name__ == '__main__':
    main()
