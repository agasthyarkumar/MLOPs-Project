"""Monitor model performance metrics."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor model performance in production."""

    def __init__(
        self,
        metrics_dir: str = "monitoring/metrics",
        performance_threshold: float = 0.8,
        prometheus_gateway: Optional[str] = None
    ):
        """
        Initialize performance monitor.
        
        Args:
            metrics_dir: Directory to save metrics
            performance_threshold: Minimum acceptable performance
            prometheus_gateway: Prometheus pushgateway URL (optional)
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.performance_threshold = performance_threshold
        self.prometheus_gateway = prometheus_gateway
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self.accuracy_gauge = Gauge(
            'model_accuracy',
            'Model accuracy score',
            registry=self.registry
        )
        self.f1_gauge = Gauge(
            'model_f1_score',
            'Model F1 score',
            registry=self.registry
        )
        self.precision_gauge = Gauge(
            'model_precision',
            'Model precision score',
            registry=self.registry
        )
        self.recall_gauge = Gauge(
            'model_recall',
            'Model recall score',
            registry=self.registry
        )
        
        self.metrics_history: List[Dict] = []
        self._load_metrics_history()

    def _load_metrics_history(self):
        """Load historical metrics."""
        history_file = self.metrics_dir / "metrics_history.json"
        if history_file.exists():
            with open(history_file, 'r') as f:
                self.metrics_history = json.load(f)
            logger.info(f"Loaded {len(self.metrics_history)} historical metrics")

    def _save_metrics_history(self):
        """Save metrics history."""
        history_file = self.metrics_dir / "metrics_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)

    def evaluate_performance(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_version: str = "unknown"
    ) -> Dict:
        """
        Evaluate model performance.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            model_version: Version of the model being evaluated
            
        Returns:
            Dictionary of performance metrics
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'model_version': model_version,
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
            'sample_size': len(y_true)
        }
        
        # Update Prometheus metrics
        self.accuracy_gauge.set(metrics['accuracy'])
        self.f1_gauge.set(metrics['f1_score'])
        self.precision_gauge.set(metrics['precision'])
        self.recall_gauge.set(metrics['recall'])
        
        # Push to Prometheus gateway if configured
        if self.prometheus_gateway:
            try:
                push_to_gateway(
                    self.prometheus_gateway,
                    job='mlops_model_monitoring',
                    registry=self.registry
                )
            except Exception as e:
                logger.warning(f"Failed to push metrics to Prometheus: {e}")
        
        # Save metrics
        self.metrics_history.append(metrics)
        self._save_metrics_history()
        
        # Save individual metric file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metric_file = self.metrics_dir / f"metrics_{timestamp}.json"
        with open(metric_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Performance metrics - Accuracy: {metrics['accuracy']:.4f}, "
                   f"F1: {metrics['f1_score']:.4f}")
        
        return metrics

    def check_performance_degradation(
        self,
        current_metrics: Dict,
        lookback_window: int = 5
    ) -> bool:
        """
        Check if performance has degraded.
        
        Args:
            current_metrics: Current performance metrics
            lookback_window: Number of recent metrics to compare against
            
        Returns:
            True if performance has degraded
        """
        if len(self.metrics_history) < lookback_window:
            logger.info("Not enough historical data for degradation check")
            return False
        
        # Get recent metrics
        recent_metrics = self.metrics_history[-lookback_window:]
        avg_accuracy = np.mean([m['accuracy'] for m in recent_metrics])
        avg_f1 = np.mean([m['f1_score'] for m in recent_metrics])
        
        # Check degradation
        accuracy_degraded = current_metrics['accuracy'] < (avg_accuracy * 0.95)
        f1_degraded = current_metrics['f1_score'] < (avg_f1 * 0.95)
        below_threshold = current_metrics['accuracy'] < self.performance_threshold
        
        degraded = accuracy_degraded or f1_degraded or below_threshold
        
        if degraded:
            logger.warning(
                f"Performance degradation detected! "
                f"Current: {current_metrics['accuracy']:.4f}, "
                f"Avg: {avg_accuracy:.4f}, "
                f"Threshold: {self.performance_threshold:.4f}"
            )
        
        return degraded

    def get_performance_summary(self) -> Dict:
        """Get summary of recent performance."""
        if not self.metrics_history:
            return {}
        
        recent = self.metrics_history[-10:]
        
        return {
            'latest_accuracy': recent[-1]['accuracy'],
            'latest_f1': recent[-1]['f1_score'],
            'avg_accuracy_10': np.mean([m['accuracy'] for m in recent]),
            'avg_f1_10': np.mean([m['f1_score'] for m in recent]),
            'total_evaluations': len(self.metrics_history),
            'last_updated': recent[-1]['timestamp']
        }
