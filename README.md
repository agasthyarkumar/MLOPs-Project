# Self Healing Pipelines on House Price Prediction

A production-ready machine learning pipeline for house price prediction with **self-healing MLOps capabilities**, featuring automated drift detection, performance monitoring, and intelligent retraining using MLflow, FastAPI, and Docker.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![MLflow](https://img.shields.io/badge/MLflow-2.8.1-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![Evidently](https://img.shields.io/badge/Evidently-0.4.15-red)

---

## 🎯 Features

- **End-to-End ML Pipeline**: Data ingestion, preprocessing, training & deployment
- **Experiment Tracking**: MLflow-based experiment management & model registry
- **REST API**: FastAPI prediction service with high performance
- **🔄 Self-Healing Pipeline**: Automated drift detection and model retraining
- **📊 Real-time Monitoring**: Evidently AI for drift detection + Prometheus metrics
- **🤖 Automated Retraining**: Intelligent triggers based on drift and performance degradation
- **✅ Model Validation**: Automated testing before production deployment
- **CI/CD**: Complete GitHub Actions workflows for monitoring and retraining
- **Containerized**: Docker-ready deployment with docker-compose support
- **Dashboard**: Real-time model performance tracking and drift reports

---

## 📁 Project Structure

```bash
MLOPs-Project/
├── .github/
│   ├── workflows/
│   │   ├── main.yml                # 🆕 Complete pipeline (all stages)
│   │   ├── ci.yml                  # Continuous integration
│   │   ├── monitoring.yml          # Production monitoring (every 6h)
│   │   ├── retrain.yml             # Automated retraining pipeline
│   │   └── retrain_deploy.yml      # Manual deployment
│   └── triggers/                   # Retraining trigger files
├── data/
│   ├── raw/                        # Original datasets
│   ├── processed/                  # Preprocessed data
│   ├── reference/                  # Baseline data for drift detection
│   └── production/                 # Production data batches
├── src/
│   ├── data/                       # Data ingestion & preprocessing
│   ├── models/                     # Model training & evaluation
│   ├── monitoring/                 # 🆕 Monitoring module
│   │   ├── drift_detector.py       # Evidently AI drift detection
│   │   ├── performance_monitor.py  # Performance metrics tracking
│   │   └── monitoring_service.py   # Main monitoring orchestrator
│   └── api/                        # FastAPI application
├── config/
│   ├── config.yaml                 # Main configuration
│   ├── model_config.yaml           # Model hyperparameters
│   └── monitoring_config.json      # 🆕 Monitoring settings
├── scripts/
│   ├── run_monitoring.py           # 🆕 Manual monitoring execution
│   ├── validate_model.py           # 🆕 Model validation tests
│   ├── register_model.py           # 🆕 MLflow registry integration
│   ├── promote_model.py            # 🆕 Production promotion
│   └── update_reference_data.py    # 🆕 Reference data management
├── monitoring/                     # 🆕 Monitoring outputs
│   ├── reports/                    # Drift HTML reports
│   ├── metrics/                    # Performance metrics history
│   └── alerts/                     # Alert notifications
├── docker/                         # Docker deployment files
├── tests/                          # Unit & integration tests
└── notebooks/                      # Jupyter notebooks
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
git clone <your-repo-url>
cd MLOPs-Project

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### 2. Download Data

```bash
make download-data
# or
bash scripts/download_data.sh
```

### 3. Prepare Reference Data for Monitoring

```bash
# Create reference dataset from training data
mkdir -p data/reference
cp data/processed/train_data.csv data/reference/reference_data.csv
```

### 4. Train Model

```bash
make train
# or
python src/models/train.py
```

### 5. Start MLflow UI

```bash
make mlflow-ui
# Access at http://localhost:5000
```

### 6. Start API Server

```bash
make serve
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

---

## 🔄 GitHub Actions Workflows

### Available Workflows

When you push to the repository, you'll see **4 workflows** in GitHub Actions:

#### 1. **🚀 Complete MLOps Pipeline** (`main.yml`)
- **Trigger**: Push to `main` or `develop`, Pull Requests
- **Purpose**: Runs all stages sequentially
- **Stages**:
  1. 🔍 **CI** - Lint, Test & Validate
  2. 🎯 **Model Training** - Train with MLflow
  3. ✅ **Model Validation** - Performance checks
  4. 📊 **Monitoring Setup** - Initialize infrastructure
  5. 🔍 **Monitoring Check** - Drift detection
  6. 🚀 **API Build & Test** - Test endpoints
  7. 🐳 **Docker Build** - Container creation
  8. 📋 **Deployment Summary** - Final report

**Note**: All workflows use GitHub Actions artifact actions v4 for improved performance and reliability.

#### 2. **🔍 CI - Continuous Integration** (`ci.yml`)
- **Trigger**: Pull Requests, Manual
- **Purpose**: Multi-version Python testing
- **Tests**: Python 3.9, 3.10, 3.11

#### 3. **📊 Monitoring - Production Model** (`monitoring.yml`)
- **Trigger**: Every 6 hours, Manual
- **Purpose**: Monitor production model performance
- **Actions**: Drift detection, performance tracking, alert generation

#### 4. **🔄 Retrain - Automated Retraining** (`retrain.yml`)
- **Trigger**: Manual, Repository dispatch from monitoring
- **Purpose**: Retrain and deploy new models
- **Stages**: Fetch data → Train → Validate → Register → Promote

### Workflow Execution on Push

When you push to `main` or `develop`:
- The **🚀 Complete MLOps Pipeline** (`main.yml`) runs automatically.
- This pipeline includes all stages: CI, Model Training, Validation, Monitoring Setup, Monitoring Check, API Build & Test, Docker Build, and Deployment Summary.
- You can monitor the progress in the Actions tab of your GitHub repository.

---

## 🔄 Self-Healing MLOps Pipeline

### Overview

The self-healing pipeline continuously monitors your model in production and automatically triggers retraining when performance degrades or data drift is detected, creating a **closed-loop autonomous system**.

### Architecture Components

#### 1. **Drift Detection** (Evidently AI)
- **Data Drift**: Monitors feature distribution changes
- **Target Drift**: Tracks prediction distribution shifts
- **Configurable Thresholds**: Customizable sensitivity
- **HTML Reports**: Visual drift analysis

#### 2. **Performance Monitoring** (Prometheus + Custom)
- **Key Metrics**: Accuracy, F1, Precision, Recall
- **Historical Tracking**: Time-series performance data
- **Degradation Detection**: Automatic alerts on performance drops
- **Prometheus Integration**: Optional pushgateway support

#### 3. **Automated Retraining**
- **Smart Triggers**: Based on drift + performance thresholds
- **Cooldown Period**: Prevents excessive retraining (24h default)
- **MLflow Integration**: Full experiment tracking
- **Model Registry**: Automatic versioning and staging
- **Validation Gates**: Quality checks before deployment

### Setup Monitoring

#### 1. Configure Monitoring Parameters

Edit `config/monitoring_config.json`:

```json
{
  "reference_data_path": "data/reference/reference_data.csv",
  "drift_threshold": 0.5,
  "performance_threshold": 0.75,
  "reports_dir": "monitoring/reports",
  "metrics_dir": "monitoring/metrics",
  "alerts_dir": "monitoring/alerts",
  "retraining_cooldown_hours": 24,
  "enable_auto_retrain": true,
  "monitoring_schedule": "0 */6 * * *",
  "batch_monitoring_enabled": true,
  "prometheus_gateway": null
}
```

#### 2. Initialize Monitoring Structure

```bash
mkdir -p monitoring/{reports,metrics,alerts}
mkdir -p data/{reference,production}
mkdir -p .github/triggers
```

### Running Monitoring

#### Manual Monitoring Check

```bash
python scripts/run_monitoring.py \
  --data-path data/production/current_batch.csv \
  --predictions-path data/production/predictions.csv \
  --labels-path data/production/labels.csv \
  --model-version v1.0.0
```

#### Automated Monitoring (GitHub Actions)
The monitoring workflow runs automatically every 6 hours via `.github/workflows/monitoring.yml`

### Retraining Pipeline

When monitoring detects issues, the automated retraining pipeline:

1. **Checks trigger conditions**
   - Data drift above threshold
   - Performance degradation detected
   - Cooldown period elapsed

2. **Fetches fresh data** and trains new model

3. **Validates new model** against test set

4. **Registers in MLflow** Model Registry

5. **Promotes to production** if validation passes

6. **Updates reference data** for future drift detection

### Monitoring Reports

- **Drift Reports**: `monitoring/reports/drift_report_*.html`
- **Performance Metrics**: `monitoring/metrics/metrics_*.json`
- **Alerts**: `monitoring/alerts/alert_*.json`

### CI/CD Integration

The self-healing pipeline integrates with GitHub Actions:

- `.github/workflows/monitoring.yml` - Scheduled monitoring
- `.github/workflows/retrain.yml` - Automated retraining

### Configuration

Edit `config/monitoring_config.json`:

```json
{
  "drift_threshold": 0.5,           // Drift detection threshold
  "performance_threshold": 0.75,     // Minimum acceptable accuracy
  "retraining_cooldown_hours": 24,  // Hours between retraining
  "enable_auto_retrain": true        // Enable automated retraining
}
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_api.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔄 CI/CD Pipeline

### Continuous Integration (`.github/workflows/ci.yml`)
- Runs on every push/PR
- Linting, testing, security checks
- Multi-version Python testing

### Retraining & Deployment (`.github/workflows/retrain_deploy.yml`)
- Scheduled weekly retraining
- Automated model deployment
- Docker image building and pushing

## 📝 Available Commands

```bash
make install          # Install dependencies
make setup           # Create directories
make download-data   # Download dataset
make train           # Train model
make serve           # Start API server
make mlflow-ui       # Start MLflow UI
make test            # Run tests
make format          # Format code
make lint            # Lint code
make clean           # Clean artifacts
make docker-build    # Build Docker image
make docker-run      # Run Docker container
```

## 🔧 Development

### Add New Model

1. Add configuration in `config/model_config.yaml`
2. Update `src/models/train.py` to support new model
3. Test and train

### Add New Features

1. Modify `src/data/preprocessing.py`
2. Update configuration
3. Retrain model

## 📊 MLflow Tracking

All experiments are tracked in MLflow:
- Parameters (hyperparameters)
- Metrics (MAE, RMSE, R², MAPE)
- Artifacts (models, plots, preprocessors)
- Models (versioned and registered)

Access MLflow UI at `http://localhost:5000`

## 🔐 Environment Variables

```bash
MLFLOW_TRACKING_URI=./mlflow
PYTHONUNBUFFERED=1
```

## 📚 Tech Stack

- **ML Framework**: scikit-learn, TensorFlow
- **Experiment Tracking**: MLflow
- **API Framework**: FastAPI
- **Data Processing**: Pandas, NumPy
- **Monitoring**: Evidently AI
- **Testing**: pytest
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Code Quality**: black, flake8, pylint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

[Agasthya R Kumar](https://github.com/agasthyarkumar)

## 🙏 Acknowledgments

- California Housing Dataset from scikit-learn
- MLflow for experiment tracking
- FastAPI for the amazing web framework
- Evidently AI for drift detection

## 📮 Contact

For questions or feedback, please open an issue on GitHub.

---

**Happy Predicting! 🏠📈**
