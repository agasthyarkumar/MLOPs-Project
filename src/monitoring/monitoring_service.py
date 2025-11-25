"""Main monitoring service orchestrating drift detection and performance monitoring."""

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from .drift_detector import DriftDetector
from .performance_monitor import PerformanceMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringService:
    """Orchestrates monitoring and triggers retraining."""

    def __init__(
        self,
        config_path: str = "config/monitoring_config.json"
    ):
        """Initialize monitoring service."""
        self.config = self._load_config(config_path)
        
        self.drift_detector = DriftDetector(
            reference_data_path=self.config['reference_data_path'],
            drift_threshold=self.config['drift_threshold'],
            reports_dir=self.config['reports_dir']
        )
        
        self.performance_monitor = PerformanceMonitor(
            metrics_dir=self.config['metrics_dir'],
            performance_threshold=self.config['performance_threshold'],
            prometheus_gateway=self.config.get('prometheus_gateway')
        )
        
        self.alerts_dir = Path(self.config.get('alerts_dir', 'monitoring/alerts'))
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration."""
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        
        with open(config_file, 'r') as f:
            return json.load(f)

    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            'reference_data_path': 'data/reference/reference_data.csv',
            'drift_threshold': 0.5,
            'performance_threshold': 0.8,
            'reports_dir': 'monitoring/reports',
            'metrics_dir': 'monitoring/metrics',
            'alerts_dir': 'monitoring/alerts',
            'retraining_cooldown_hours': 24,
            'enable_auto_retrain': True
        }

    def check_production_data(
        self,
        current_data: pd.DataFrame,
        y_true: Optional[pd.Series] = None,
        y_pred: Optional[pd.Series] = None,
        model_version: str = "unknown"
    ) -> Dict:
        """
        Check production data for drift and performance issues.
        
        Args:
            current_data: Current production data
            y_true: True labels (if available)
            y_pred: Predictions (if available)
            model_version: Current model version
            
        Returns:
            Monitoring results dictionary
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'model_version': model_version,
            'drift_detected': False,
            'performance_degraded': False,
            'retraining_triggered': False
        }
        
        # Check for data drift
        logger.info("Checking for data drift...")
        drift_detected, drift_metrics = self.drift_detector.detect_drift(current_data)
        results['drift_detected'] = drift_detected
        results['drift_metrics'] = drift_metrics
        
        # Check performance if labels available
        if y_true is not None and y_pred is not None:
            logger.info("Evaluating model performance...")
            performance_metrics = self.performance_monitor.evaluate_performance(
                y_true.values,
                y_pred.values,
                model_version
            )
            results['performance_metrics'] = performance_metrics
            
            # Check for degradation
            performance_degraded = self.performance_monitor.check_performance_degradation(
                performance_metrics
            )
            results['performance_degraded'] = performance_degraded
        
        # Trigger retraining if needed
        should_retrain = (
            (drift_detected or results.get('performance_degraded', False))
            and self.config.get('enable_auto_retrain', True)
            and self._check_retraining_cooldown()
        )
        
        if should_retrain:
            logger.warning("Conditions met for automated retraining!")
            results['retraining_triggered'] = self._trigger_retraining(results)
        
        # Save alert if issues detected
        if drift_detected or results.get('performance_degraded', False):
            self._save_alert(results)
        
        return results

    def _check_retraining_cooldown(self) -> bool:
        """Check if enough time has passed since last retraining."""
        cooldown_file = self.alerts_dir / 'last_retraining.json'
        
        if not cooldown_file.exists():
            return True
        
        with open(cooldown_file, 'r') as f:
            last_retraining = json.load(f)
        
        last_time = datetime.fromisoformat(last_retraining['timestamp'])
        hours_since = (datetime.now() - last_time).total_seconds() / 3600
        cooldown_hours = self.config.get('retraining_cooldown_hours', 24)
        
        if hours_since < cooldown_hours:
            logger.info(f"Retraining cooldown active: {hours_since:.1f}/{cooldown_hours} hours")
            return False
        
        return True

    def _trigger_retraining(self, monitoring_results: Dict) -> bool:
        """
        Trigger automated retraining pipeline.
        
        Args:
            monitoring_results: Results from monitoring checks
            
        Returns:
            True if retraining was triggered successfully
        """
        try:
            # Create trigger file for GitHub Actions
            trigger_file = Path('.github/triggers/retrain_trigger.json')
            trigger_file.parent.mkdir(parents=True, exist_ok=True)
            
            trigger_data = {
                'triggered_at': datetime.now().isoformat(),
                'reason': 'automated_monitoring',
                'drift_detected': monitoring_results.get('drift_detected', False),
                'performance_degraded': monitoring_results.get('performance_degraded', False),
                'drift_metrics': monitoring_results.get('drift_metrics', {}),
                'performance_metrics': monitoring_results.get('performance_metrics', {})
            }
            
            with open(trigger_file, 'w') as f:
                json.dump(trigger_data, f, indent=2)
            
            # Update last retraining timestamp
            cooldown_file = self.alerts_dir / 'last_retraining.json'
            with open(cooldown_file, 'w') as f:
                json.dump({'timestamp': datetime.now().isoformat()}, f)
            
            # Trigger GitHub Actions workflow via repository dispatch
            if os.getenv('GITHUB_TOKEN'):
                try:
                    subprocess.run([
                        'gh', 'workflow', 'run', 'retrain.yml',
                        '--ref', 'main'
                    ], check=True)
                    logger.info("GitHub Actions retraining workflow triggered")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to trigger GitHub Actions: {e}")
            else:
                logger.info("Retraining trigger file created. Manual workflow dispatch needed.")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger retraining: {e}")
            return False

    def _save_alert(self, results: Dict):
        """Save monitoring alert."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_file = self.alerts_dir / f"alert_{timestamp}.json"
        
        with open(alert_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Alert saved to {alert_file}")
