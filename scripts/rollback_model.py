#!/usr/bin/env python3
"""
Automatic model rollback on performance degradation
Self-healing mechanism to restore previous working model
"""
import json
import logging
import shutil
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelRollback:
    """Rollback to previous model version on failure"""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.backup_dir = Path("models/backups")
        self.rollback_log = Path("models/rollback_log.json")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def get_model_versions(self) -> list:
        """Get list of available model backups"""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup in self.backup_dir.iterdir():
            if backup.is_dir() and backup.name.startswith('v'):
                try:
                    metadata_file = backup / 'metadata.json'
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            backups.append({
                                'version': backup.name,
                                'path': backup,
                                'timestamp': metadata.get('timestamp'),
                                'metrics': metadata.get('metrics', {})
                            })
                except Exception as e:
                    logger.warning(f"Could not read backup {backup.name}: {e}")
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def backup_current_model(self, version_name: str = None):
        """Backup current model before rollback"""
        if version_name is None:
            version_name = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / version_name
        backup_path.mkdir(exist_ok=True)
        
        # Copy model files
        for item in self.models_dir.iterdir():
            if item.is_file() and item.suffix in ['.pkl', '.joblib', '.h5', '.pt', '.onnx']:
                shutil.copy2(item, backup_path / item.name)
                logger.info(f"Backed up {item.name} to {version_name}")
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'version': version_name,
            'backed_up_from': 'current'
        }
        
        with open(backup_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Current model backed up as {version_name}")
    
    def rollback_to_version(self, version: str = "previous") -> bool:
        """Rollback to a specific version"""
        try:
            versions = self.get_model_versions()
            
            if not versions:
                logger.error("❌ No backup versions available for rollback")
                return False
            
            # Get target version
            if version == "previous":
                target = versions[0]
            else:
                target = next((v for v in versions if v['version'] == version), None)
                if not target:
                    logger.error(f"❌ Version {version} not found")
                    return False
            
            logger.info(f"🔄 Rolling back to {target['version']} from {target['timestamp']}")
            
            # Backup current model first
            self.backup_current_model(f"before_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Restore backup
            backup_path = target['path']
            for item in backup_path.iterdir():
                if item.is_file() and item.suffix in ['.pkl', '.joblib', '.h5', '.pt', '.onnx']:
                    dest = self.models_dir / item.name
                    shutil.copy2(item, dest)
                    logger.info(f"Restored {item.name}")
            
            # Log rollback
            self.log_rollback(target['version'], "Performance degradation")
            
            logger.info(f"✅ Successfully rolled back to {target['version']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def log_rollback(self, version: str, reason: str):
        """Log rollback event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'rolled_back_to': version,
            'reason': reason,
            'triggered_by': 'auto-heal'
        }
        
        # Append to log
        log_data = []
        if self.rollback_log.exists():
            with open(self.rollback_log, 'r') as f:
                try:
                    log_data = json.load(f)
                except:
                    log_data = []
        
        log_data.append(log_entry)
        
        with open(self.rollback_log, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"📝 Logged rollback event")
    
    def auto_rollback_on_failure(self, current_metric: float, threshold: float) -> bool:
        """Automatically rollback if current model underperforms"""
        if current_metric < threshold:
            logger.warning(f"⚠️  Model performance {current_metric:.3f} below threshold {threshold:.3f}")
            return self.rollback_to_version("previous")
        else:
            logger.info(f"✅ Model performance {current_metric:.3f} meets threshold")
            return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback model to previous version')
    parser.add_argument('--version', default='previous',
                       help='Version to rollback to (default: previous)')
    parser.add_argument('--current-metric', type=float, default=None,
                       help='Current model metric for auto-rollback')
    parser.add_argument('--threshold', type=float, default=0.70,
                       help='Minimum acceptable metric')
    args = parser.parse_args()
    
    rollback = ModelRollback()
    
    if args.current_metric is not None:
        # Auto-rollback mode
        success = rollback.auto_rollback_on_failure(args.current_metric, args.threshold)
    else:
        # Manual rollback
        success = rollback.rollback_to_version(args.version)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
