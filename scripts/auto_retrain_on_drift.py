#!/usr/bin/env python3
"""
Automatic model retraining triggered by drift detection
Self-healing mechanism for model performance degradation
"""
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoRetrainer:
    """Automatically retrain model when drift is detected"""
    
    def __init__(self, config_path: str = "config/monitoring_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.retraining_log = Path(".github/triggers/retraining_log.json")
        self.retraining_log.parent.mkdir(parents=True, exist_ok=True)
        
    def load_config(self) -> dict:
        """Load monitoring configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}, using defaults")
            return {
                "retraining_cooldown_hours": 24,
                "enable_auto_retrain": True,
                "drift_threshold": 0.5
            }
    
    def check_cooldown(self) -> bool:
        """Check if enough time has passed since last retraining"""
        if not self.retraining_log.exists():
            return True
        
        try:
            with open(self.retraining_log, 'r') as f:
                log_data = json.load(f)
                last_retrain = datetime.fromisoformat(log_data.get('last_retrain_time', '2000-01-01'))
                cooldown_hours = self.config.get('retraining_cooldown_hours', 24)
                
                time_since_retrain = datetime.now() - last_retrain
                if time_since_retrain < timedelta(hours=cooldown_hours):
                    logger.info(f"⏳ Cooldown active. {cooldown_hours - time_since_retrain.seconds/3600:.1f}h remaining")
                    return False
        except Exception as e:
            logger.warning(f"Error checking cooldown: {e}")
        
        return True
    
    def log_retraining(self, reason: str, drift_score: float = None):
        """Log retraining event"""
        log_data = {
            'last_retrain_time': datetime.now().isoformat(),
            'reason': reason,
            'drift_score': drift_score,
            'triggered_by': 'auto-heal'
        }
        
        with open(self.retraining_log, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"📝 Logged retraining event: {reason}")
    
    def trigger_retraining(self) -> bool:
        """Execute model retraining"""
        logger.info("🔄 Starting automatic model retraining...")
        
        try:
            # Run training script
            result = subprocess.run(
                ['python', 'src/models/train.py'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Model retraining completed successfully!")
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"❌ Retraining failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Retraining timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Retraining error: {e}")
            return False
    
    def should_retrain(self, drift_detected: bool, drift_score: float = None) -> bool:
        """Decide if retraining should happen"""
        if not self.config.get('enable_auto_retrain', True):
            logger.info("Auto-retrain is disabled in config")
            return False
        
        if not drift_detected:
            logger.info("No drift detected - retraining not needed")
            return False
        
        if not self.check_cooldown():
            logger.info("Cooldown period active - skipping retraining")
            return False
        
        if drift_score and drift_score < self.config.get('drift_threshold', 0.5):
            logger.info(f"Drift score {drift_score:.3f} below threshold - no action needed")
            return False
        
        return True
    
    def execute(self, drift_detected: bool = False, drift_score: float = None) -> bool:
        """Main execution logic"""
        logger.info("🔍 Evaluating need for automatic retraining...")
        
        if self.should_retrain(drift_detected, drift_score):
            logger.info("✅ Conditions met for automatic retraining")
            
            if self.trigger_retraining():
                self.log_retraining(
                    reason="Data drift detected",
                    drift_score=drift_score
                )
                return True
            else:
                logger.error("❌ Automatic retraining failed")
                return False
        else:
            logger.info("ℹ️  Retraining conditions not met")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-retrain model on drift')
    parser.add_argument('--drift-detected', action='store_true',
                       help='Whether drift was detected')
    parser.add_argument('--drift-score', type=float, default=None,
                       help='Drift score (0-1)')
    parser.add_argument('--config', default='config/monitoring_config.json',
                       help='Config file path')
    args = parser.parse_args()
    
    retrainer = AutoRetrainer(args.config)
    success = retrainer.execute(args.drift_detected, args.drift_score)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
