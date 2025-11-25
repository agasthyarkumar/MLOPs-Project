#!/usr/bin/env python3
"""
Service health monitoring and auto-recovery
Self-healing mechanism for API service failures
"""
import time
import logging
import sys
import requests
import subprocess
from pathlib import Path
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServiceAutoRecovery:
    """Automatically recover from service failures"""
    
    def __init__(self, service_url: str = "http://localhost:8000"):
        self.service_url = service_url
        self.health_endpoint = f"{service_url}/health"
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.recovery_log = Path("monitoring/recovery_log.json")
        self.recovery_log.parent.mkdir(parents=True, exist_ok=True)
        
    def check_health(self) -> bool:
        """Check if service is healthy"""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Service is healthy")
                return True
            else:
                logger.warning(f"⚠️  Service returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def restart_service_docker(self, container_name: str = "mlops-api") -> bool:
        """Restart Docker container"""
        try:
            logger.info(f"🔄 Attempting to restart Docker container: {container_name}")
            
            # Stop container
            subprocess.run(['docker', 'stop', container_name], 
                         capture_output=True, timeout=30)
            time.sleep(2)
            
            # Start container
            result = subprocess.run(['docker', 'start', container_name],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ Container {container_name} restarted successfully")
                time.sleep(10)  # Wait for service to initialize
                return True
            else:
                logger.error(f"❌ Failed to restart container: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Docker restart failed: {e}")
            return False
    
    def restart_service_process(self, pid_file: str = "api.pid") -> bool:
        """Restart service process"""
        try:
            logger.info("🔄 Attempting to restart service process...")
            
            # Kill existing process
            if Path(pid_file).exists():
                with open(pid_file, 'r') as f:
                    pid = f.read().strip()
                try:
                    subprocess.run(['kill', pid], timeout=5)
                    logger.info(f"Killed process {pid}")
                    time.sleep(2)
                except:
                    pass
            
            # Start new process
            process = subprocess.Popen(
                ['uvicorn', 'src.api.main:app', '--host', '0.0.0.0', '--port', '8000'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Save PID
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            logger.info(f"✅ Service restarted with PID {process.pid}")
            time.sleep(10)
            return True
            
        except Exception as e:
            logger.error(f"❌ Process restart failed: {e}")
            return False
    
    def clear_cache(self) -> bool:
        """Clear service cache"""
        try:
            cache_dir = Path("cache")
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                cache_dir.mkdir()
                logger.info("✅ Cache cleared")
                return True
        except Exception as e:
            logger.warning(f"⚠️  Cache clear failed: {e}")
        return False
    
    def log_recovery(self, recovery_action: str, success: bool):
        """Log recovery attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': recovery_action,
            'success': success,
            'service_url': self.service_url
        }
        
        log_data = []
        if self.recovery_log.exists():
            with open(self.recovery_log, 'r') as f:
                try:
                    log_data = json.load(f)
                except:
                    log_data = []
        
        log_data.append(log_entry)
        
        with open(self.recovery_log, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def auto_recover(self, recovery_method: str = "docker") -> bool:
        """Attempt automatic recovery"""
        logger.info("🔍 Starting auto-recovery process...")
        
        # Check if service is already healthy
        if self.check_health():
            logger.info("Service is already healthy - no recovery needed")
            return True
        
        # Try recovery with retries
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"🔄 Recovery attempt {attempt}/{self.max_retries}")
            
            # Clear cache first
            self.clear_cache()
            
            # Attempt restart based on method
            if recovery_method == "docker":
                restart_success = self.restart_service_docker()
            elif recovery_method == "process":
                restart_success = self.restart_service_process()
            else:
                logger.error(f"Unknown recovery method: {recovery_method}")
                return False
            
            if not restart_success:
                logger.warning(f"Restart failed on attempt {attempt}")
                time.sleep(self.retry_delay)
                continue
            
            # Verify health after restart
            time.sleep(5)
            if self.check_health():
                logger.info(f"✅ Auto-recovery successful on attempt {attempt}")
                self.log_recovery(f"{recovery_method}_restart", True)
                return True
            
            logger.warning(f"Health check failed after attempt {attempt}")
            time.sleep(self.retry_delay)
        
        logger.error(f"❌ Auto-recovery failed after {self.max_retries} attempts")
        self.log_recovery(f"{recovery_method}_restart", False)
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-recover service on failure')
    parser.add_argument('--service-url', default='http://localhost:8000',
                       help='Service URL to monitor')
    parser.add_argument('--method', default='docker', choices=['docker', 'process'],
                       help='Recovery method (docker or process)')
    parser.add_argument('--container-name', default='mlops-api',
                       help='Docker container name')
    args = parser.parse_args()
    
    recovery = ServiceAutoRecovery(args.service_url)
    success = recovery.auto_recover(args.method)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
