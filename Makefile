.PHONY: install setup train serve test clean self-healing help

# Default target - show help
help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║       🔄 Self-Healing MLOps Pipeline - Make Commands       ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@echo "║                                                            ║"
	@echo "║  📦 SETUP & INSTALLATION                                   ║"
	@echo "║  make install          - Install all dependencies          ║"
	@echo "║  make setup            - Create directory structure        ║"
	@echo "║  make download-data    - Download dataset                  ║"
	@echo "║                                                            ║"
	@echo "║  🎯 MODEL TRAINING                                         ║"
	@echo "║  make train            - Train basic model                 ║"
	@echo "║  make train-improved   - Train improved pipeline           ║"
	@echo "║  make train-ensemble   - Train ensemble model              ║"
	@echo "║  make train-tuned      - Train with hyperparameter tuning  ║"
	@echo "║                                                            ║"
	@echo "║  🚀 DEPLOYMENT                                             ║"
	@echo "║  make serve            - Start API server (uvicorn)        ║"
	@echo "║  make mlflow-ui        - Start MLflow UI                   ║"
	@echo "║  make docker-build     - Build Docker image                ║"
	@echo "║  make docker-run       - Run Docker container              ║"
	@echo "║                                                            ║"
	@echo "║  🔄 SELF-HEALING (NEW!)                                    ║"
	@echo "║  make test-self-healing   - Test all self-healing features ║"
	@echo "║  make fix-data            - Auto-fix data quality issues   ║"
	@echo "║  make rollback            - Rollback to previous model     ║"
	@echo "║  make recover-service     - Auto-recover failed service    ║"
	@echo "║  make run-monitoring      - Run drift detection            ║"
	@echo "║  make logs-all            - View all self-healing logs     ║"
	@echo "║  make help-self-healing   - Detailed self-healing help     ║"
	@echo "║                                                            ║"
	@echo "║  ✅ TESTING & QUALITY                                      ║"
	@echo "║  make test             - Run tests with coverage           ║"
	@echo "║  make format           - Format code (black, isort)        ║"
	@echo "║  make lint             - Lint code (flake8, pylint)        ║"
	@echo "║                                                            ║"
	@echo "║  📊 UTILITIES                                              ║"
	@echo "║  make results          - Show model results                ║"
	@echo "║  make compare          - Compare model metrics             ║"
	@echo "║  make clean            - Clean temporary files             ║"
	@echo "║                                                            ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "💡 Quick Start: make install && make setup && make train"
	@echo "🔄 Self-Healing: make help-self-healing"
	@echo ""

install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

setup:
	mkdir -p data/{raw,processed,feature_store} mlflow
	chmod +x scripts/*.sh

download-data:
	bash scripts/download_data.sh

train:
	python src/models/train.py

train-improved:
	python run_improved_pipeline.py

train-ensemble:
	python src/models/ensemble.py

train-tuned:
	python src/models/hyperparameter_tuning.py

serve:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

mlflow-ui:
	mlflow ui --host 0.0.0.0 --port 5000

test:
	pytest tests/ -v --cov=src

format:
	black src/ tests/
	isort src/ tests/

lint:
	flake8 src/ tests/
	pylint src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info

docker-build:
	docker build -f docker/Dockerfile -t house-price-api:latest .

docker-run:
	docker run -p 8000:8000 house-price-api:latest

# New convenience commands
results:
	cat models/production_model_metadata.yaml

compare:
	python -c "import pandas as pd; import yaml; \
	with open('models/production_model_metadata.yaml') as f: \
	    data = yaml.safe_load(f); \
	    print('\n🏆 PRODUCTION MODEL'); \
	    print(f\"Model: {data['model_name']}\"); \
	    print(f\"RMSE: \$${data['test_rmse']:,.2f}\"); \
	    print(f\"R²: {data['test_r2']:.4f}\"); \
	    print(f\"Features: {data['n_features']}\"); \
	    print(f\"Trained: {data['training_date']}\n\")"

# ============================================================================
# 🔄 SELF-HEALING COMMANDS
# ============================================================================

# Run all self-healing tests
test-self-healing:
	@echo "🔄 Running self-healing capabilities test suite..."
	python scripts/test_self_healing.py

# Data quality auto-fix
fix-data:
	@echo "🔧 Auto-fixing data quality issues..."
	python scripts/auto_fix_data_issues.py --data-path data/raw/housing.csv

# Model rollback
rollback:
	@echo "🔙 Rolling back to previous model version..."
	python scripts/rollback_model.py --version previous

rollback-on-failure:
	@echo "🔙 Checking model performance and rolling back if needed..."
	python scripts/rollback_model.py --current-metric $(METRIC) --threshold 0.70

# Auto-retrain on drift
retrain-on-drift:
	@echo "🔄 Checking for drift and retraining if needed..."
	python scripts/auto_retrain_on_drift.py --drift-detected --drift-score $(SCORE)

# Service recovery
recover-service:
	@echo "🏥 Attempting service auto-recovery..."
	python scripts/auto_recover_service.py --method process --service-url http://localhost:8000

recover-docker:
	@echo "🏥 Attempting Docker container recovery..."
	python scripts/auto_recover_service.py --method docker --service-url http://localhost:8000

# Monitoring
run-monitoring:
	@echo "📊 Running monitoring and drift detection..."
	python scripts/run_monitoring.py --data-path data/production/current_batch.csv --model-version latest

# Model validation
validate-model:
	@echo "✅ Validating model performance..."
	python scripts/validate_model.py --min-accuracy 0.70 --output validation_results.json

# View self-healing logs
logs-recovery:
	@echo "📝 Service Recovery Log:"
	@cat monitoring/recovery_log.json 2>/dev/null | jq '.' || echo "No recovery log found"

logs-rollback:
	@echo "📝 Model Rollback Log:"
	@cat models/rollback_log.json 2>/dev/null | jq '.' || echo "No rollback log found"

logs-retrain:
	@echo "📝 Auto-Retraining Log:"
	@cat .github/triggers/retraining_log.json 2>/dev/null | jq '.' || echo "No retraining log found"

# View all self-healing logs
logs-all:
	@echo "📊 ALL SELF-HEALING LOGS"
	@echo "========================"
	@make logs-recovery
	@echo ""
	@make logs-rollback
	@echo ""
	@make logs-retrain

# Self-healing status dashboard
self-healing-status:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║           SELF-HEALING STATUS DASHBOARD                    ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@python scripts/test_self_healing.py 2>/dev/null || echo "Run 'make test-self-healing' first"
	@echo "╚════════════════════════════════════════════════════════════╝"

# Complete self-healing workflow simulation
self-healing-demo:
	@echo "🎬 Running self-healing demonstration..."
	@echo ""
	@echo "1️⃣  Testing data auto-fix..."
	@make fix-data || true
	@echo ""
	@echo "2️⃣  Testing model validation..."
	@make validate-model || true
	@echo ""
	@echo "3️⃣  Testing monitoring..."
	@make run-monitoring || true
	@echo ""
	@echo "✅ Self-healing demo complete!"

# Help for self-healing commands
help-self-healing:
	@echo "🔄 Self-Healing Commands:"
	@echo ""
	@echo "  make test-self-healing    - Run all self-healing tests"
	@echo "  make fix-data             - Auto-fix data quality issues"
	@echo "  make rollback             - Rollback to previous model"
	@echo "  make rollback-on-failure  - Rollback if METRIC < threshold (e.g., METRIC=0.65)"
	@echo "  make retrain-on-drift     - Auto-retrain on drift (e.g., SCORE=0.85)"
	@echo "  make recover-service      - Recover failed service (process mode)"
	@echo "  make recover-docker       - Recover failed service (Docker mode)"
	@echo "  make run-monitoring       - Run drift detection monitoring"
	@echo "  make validate-model       - Validate model performance"
	@echo "  make logs-recovery        - View service recovery log"
	@echo "  make logs-rollback        - View model rollback log"
	@echo "  make logs-retrain         - View auto-retraining log"
	@echo "  make logs-all             - View all self-healing logs"
	@echo "  make self-healing-status  - Show self-healing status dashboard"
	@echo "  make self-healing-demo    - Run complete self-healing demo"
	@echo ""
	@echo "Examples:"
	@echo "  make rollback-on-failure METRIC=0.65"
	@echo "  make retrain-on-drift SCORE=0.82"

