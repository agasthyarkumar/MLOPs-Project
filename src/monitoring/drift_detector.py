"""Drift detection using Evidently AI."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
from evidently import metric_preset
from evidently.report import Report

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detects data drift and target drift using Evidently AI."""

    def __init__(
        self,
        reference_data_path: str,
        drift_threshold: float = 0.5,
        reports_dir: str = "monitoring/reports"
    ):
        """
        Initialize drift detector.
        
        Args:
            reference_data_path: Path to reference dataset
            drift_threshold: Threshold for drift detection (0-1)
            reports_dir: Directory to save drift reports
        """
        self.reference_data_path = Path(reference_data_path)
        self.drift_threshold = drift_threshold
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.reference_data: Optional[pd.DataFrame] = None
        self._load_reference_data()

    def _load_reference_data(self):
        """Load reference dataset for drift comparison."""
        try:
            if self.reference_data_path.suffix == '.csv':
                self.reference_data = pd.read_csv(self.reference_data_path)
            elif self.reference_data_path.suffix == '.parquet':
                self.reference_data = pd.read_parquet(self.reference_data_path)
            logger.info(f"Loaded reference data: {len(self.reference_data)} rows")
        except Exception as e:
            logger.error(f"Failed to load reference data: {e}")
            raise

    def detect_drift(
        self,
        current_data: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> Tuple[bool, Dict]:
        """
        Detect drift between reference and current data.
        
        Args:
            current_data: Current production data
            target_column: Name of target column (optional)
            
        Returns:
            Tuple of (drift_detected, drift_metrics)
        """
        if self.reference_data is None:
            raise ValueError("Reference data not loaded")

        # Create drift report
        report = Report(metrics=[
            metric_preset.DataDriftPreset(),
        ])
        
        if target_column and target_column in current_data.columns:
            report = Report(metrics=[
                metric_preset.DataDriftPreset(),
                metric_preset.TargetDriftPreset(),
            ])

        report.run(
            reference_data=self.reference_data,
            current_data=current_data,
            column_mapping=None
        )

        # Extract metrics
        report_dict = report.as_dict()
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"drift_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        report.save_html(str(self.reports_dir / f"drift_report_{timestamp}.html"))
        
        # Check for drift
        drift_metrics = self._extract_drift_metrics(report_dict)
        drift_detected = drift_metrics['drift_share'] > self.drift_threshold
        
        logger.info(f"Drift detection: {drift_detected}, "
                   f"Drift share: {drift_metrics['drift_share']:.2%}")
        
        return drift_detected, drift_metrics

    def _extract_drift_metrics(self, report_dict: Dict) -> Dict:
        """Extract key drift metrics from report."""
        metrics = {
            'drift_share': 0.0,
            'number_of_drifted_columns': 0,
            'dataset_drift': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            for metric in report_dict.get('metrics', []):
                if metric.get('metric') == 'DatasetDriftMetric':
                    result = metric.get('result', {})
                    metrics['drift_share'] = result.get('drift_share', 0.0)
                    metrics['number_of_drifted_columns'] = result.get('number_of_drifted_columns', 0)
                    metrics['dataset_drift'] = result.get('dataset_drift', False)
                    break
        except Exception as e:
            logger.error(f"Error extracting drift metrics: {e}")
        
        return metrics

    def update_reference_data(self, new_reference_data: pd.DataFrame):
        """Update reference dataset."""
        self.reference_data = new_reference_data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reference_path = self.reports_dir.parent / f"reference_data_{timestamp}.parquet"
        new_reference_data.to_parquet(reference_path, index=False)
        logger.info(f"Updated reference data saved to {reference_path}")
