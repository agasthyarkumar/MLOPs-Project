"""Update reference data for drift detection after retraining."""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_reference_data(
    new_training_data_path: str = "data/processed/train_data.csv",
    reference_output_path: str = "data/reference/reference_data.csv"
):
    """
    Update reference dataset used for drift detection.
    
    Args:
        new_training_data_path: Path to newly used training data
        reference_output_path: Where to save the new reference data
    """
    logger.info(f"Loading new training data from {new_training_data_path}")
    
    # Load the data used for training
    if Path(new_training_data_path).suffix == '.csv':
        data = pd.read_csv(new_training_data_path)
    else:
        data = pd.read_parquet(new_training_data_path)
    
    # Create reference directory if needed
    ref_path = Path(reference_output_path)
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as new reference
    data.to_csv(reference_output_path, index=False)
    logger.info(f"Updated reference data saved to {reference_output_path}")
    
    # Also save a timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ref_path.parent / f"reference_data_{timestamp}.csv"
    data.to_csv(backup_path, index=False)
    logger.info(f"Backup saved to {backup_path}")


if __name__ == '__main__':
    update_reference_data()
