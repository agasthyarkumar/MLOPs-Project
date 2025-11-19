.PHONY: install setup train serve test clean

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
