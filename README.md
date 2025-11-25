# 🔄 Self-Healing MLOps Pipeline - House Price Prediction

A **truly self-healing** production MLOps pipeline that automatically detects and fixes issues across the entire ML lifecycle. Features automated data quality fixes, model rollback, drift-based retraining, and service recovery.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![MLflow](https://img.shields.io/badge/MLflow-2.8.1-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![Evidently](https://img.shields.io/badge/Evidently-0.4.15-red)
![Self-Healing](https://img.shields.io/badge/Self--Healing-✅%20Active-brightgreen)

---

## 🎯 Self-Healing Features

### ✨ True Self-Healing Capabilities

- **🔧 Auto-Fix Data Quality**: Automatically detects and fixes missing values, outliers, and duplicates
- **🔙 Smart Model Rollback**: Auto-rollback when new models underperform (< 70% accuracy)
- **🔄 Drift-Based Retraining**: Automatically retrains models when data drift is detected
- **🏥 Service Auto-Recovery**: Automatically restarts and recovers failed API services
- **📊 Continuous Monitoring**: Real-time drift detection with Evidently AI + Prometheus
- **⏱️ Cooldown Protection**: Prevents excessive retraining with intelligent cooldown periods
- **📝 Complete Audit Trail**: All self-healing actions are logged and trackable
- **🛡️ Safety Mechanisms**: Backups before changes, rollback capability, max retry limits

### 🚀 MLOps Pipeline Features

- **End-to-End ML Pipeline**: Data ingestion → preprocessing → training → deployment
- **Experiment Tracking**: MLflow-based experiment management & model registry
- **REST API**: FastAPI prediction service with automatic health checks
- **✅ Model Validation**: Automated performance testing before deployment
- **CI/CD**: 8-stage GitHub Actions workflow with self-healing integration
- **Containerized**: Docker-ready deployment with docker-compose support
- **Dashboard**: Real-time monitoring with drift reports and alerts

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
│   ├── monitoring_config.json      # Monitoring settings
│   └── self_healing_config.json    # 🆕 Self-healing configuration
├── scripts/
│   ├── auto_fix_data_issues.py     # 🆕 Self-healing: Auto-fix data quality
│   ├── auto_retrain_on_drift.py    # 🆕 Self-healing: Drift-based retraining
│   ├── rollback_model.py           # 🆕 Self-healing: Model rollback
│   ├── auto_recover_service.py     # 🆕 Self-healing: Service recovery
│   ├── run_monitoring.py           # Manual monitoring execution
│   ├── validate_model.py           # Model validation tests
│   ├── register_model.py           # MLflow registry integration
│   ├── promote_model.py            # Production promotion
│   └── update_reference_data.py    # Reference data management
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

### Option 1: Python Virtual Environment (Recommended for Development)

```bash
# Clone repository
git clone <your-repo-url>
cd MLOPs-Project

# Complete setup with one command
make setup-all

# Activate virtual environment
source venv/bin/activate

# Train model
make train

# Start services
make serve           # API on port 8000
make mlflow-ui       # MLflow on port 5000
```

**Or use the quick start script:**

```bash
chmod +x quick_start.sh scripts/setup_venv.sh
./quick_start.sh
```

### Option 2: Docker (Recommended for Production)

```bash
# Clone repository
git clone <your-repo-url>
cd MLOPs-Project

# Start all services with docker-compose
make docker-compose

# Services will be available at:
# - API: http://localhost:8000
# - MLflow UI: http://localhost:5000

# Stop services
make docker-compose-down
```

### Option 3: Manual Setup

```bash
git clone <your-repo-url>
cd MLOPs-Project

# Create virtual environment
make venv
source venv/bin/activate

# Install dependencies
make install

# Create directory structure
make setup

# Download data
make download-data
```

### 2. Prepare Reference Data for Monitoring

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

## 🔄 Self-Healing Capabilities

### 🎯 What Makes This Truly Self-Healing?

Unlike traditional resilient pipelines that just "continue on error", this pipeline **automatically detects and fixes issues**:

| Issue Type | Detection | Remediation | Result |
|------------|-----------|-------------|--------|
| **Data Quality** | Missing values, outliers, duplicates | Auto-fix with intelligent imputation | Clean data, tests pass |
| **Model Performance** | Accuracy < 70% | Auto-rollback to previous version | Production stability maintained |
| **Data Drift** | Distribution changes detected | Auto-retrain with cooldown | Model stays current |
| **Service Failure** | Health check fails | Auto-restart with recovery | Zero-downtime recovery |

### 🔧 Self-Healing Scripts

#### 1. **Data Quality Auto-Fix**
```bash
# Automatically fixes data issues before training
python scripts/auto_fix_data_issues.py --data-path data/raw/housing.csv

# Fixes applied:
# ✅ Missing values filled (median/mode)
# ✅ Outliers capped (IQR method)
# ✅ Duplicates removed
# ✅ Data types corrected
```

#### 2. **Model Rollback**
```bash
# Automatically rolls back if new model underperforms
python scripts/rollback_model.py --current-metric 0.65 --threshold 0.70

# Actions taken:
# ⚠️  Model performance 0.65 < threshold 0.70
# 📦 Backing up current model
# 🔙 Restoring previous version
# ✅ Rollback complete
```

#### 3. **Drift-Based Retraining**
```bash
# Automatically retrains when drift detected
python scripts/auto_retrain_on_drift.py --drift-detected --drift-score 0.82

# Actions taken:
# 🚨 Drift detected! Score: 0.82
# ✅ Cooldown check passed (24h)
# 🔄 Starting automatic retraining
# ✅ Model retrained successfully
```

#### 4. **Service Auto-Recovery**
```bash
# Automatically recovers failed services
python scripts/auto_recover_service.py --method docker --service-url http://localhost:8000

# Recovery steps:
# ❌ Health check failed
# 🔄 Clearing cache
# 🔄 Restarting container
# ✅ Service recovered
```

### 📊 Self-Healing Workflow Integration

The GitHub Actions workflow integrates all self-healing capabilities:

```yaml
# Example: Tests with auto-fix
- name: 🧪 Run tests with auto-fix
  run: |
    if ! pytest tests/; then
      python scripts/auto_fix_data_issues.py
      pytest tests/  # Retry after fix
    fi

# Example: Auto-rollback on validation failure
- name: 🔙 Auto-rollback
  if: accuracy < 0.70
  run: python scripts/rollback_model.py --current-metric ${{ accuracy }}

# Example: Auto-retrain on drift
- name: 🔄 Auto-retrain
  if: drift_detected == 'true'
  run: python scripts/auto_retrain_on_drift.py --drift-score ${{ drift_score }}
```

### 📋 Configuration

Edit `config/self_healing_config.json`:

```json
{
  "data_quality": {
    "auto_fix_enabled": true,
    "outlier_threshold_iqr": 3.0
  },
  "model_validation": {
    "auto_rollback_enabled": true,
    "min_accuracy_threshold": 0.70
  },
  "drift_detection": {
    "auto_retrain_enabled": true,
    "drift_threshold": 0.5,
    "retraining_cooldown_hours": 24
  },
  "service_recovery": {
    "auto_recovery_enabled": true,
    "max_recovery_attempts": 3
  }
}
```

### 📝 Audit Trail

All self-healing actions are logged:

- `monitoring/recovery_log.json` - Service recovery events
- `models/rollback_log.json` - Model rollback history
- `.github/triggers/retraining_log.json` - Auto-retraining events

**📚 Full Documentation**: See [docs/SELF_HEALING.md](docs/SELF_HEALING.md) for complete details.

---

## 🚀 GitHub Actions Workflows

### Overview
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
