# 🐍 Python Virtual Environment Setup Guide

## Overview

This project now supports **three deployment options**:

1. **Virtual Environment** (Recommended for Development)
2. **Docker** (Recommended for Production)
3. **Manual Setup** (For customization)

## Quick Start Options

### Option 1: One-Command Setup ⚡

```bash
# Complete setup with virtual environment
make setup-all
```

Or use the quick start script:

```bash
chmod +x quick_start.sh scripts/setup_venv.sh
./quick_start.sh
```

**What it does:**
- Creates Python virtual environment
- Installs all dependencies
- Creates directory structure
- Makes scripts executable
- Ready to train and serve

### Option 2: Docker Setup 🐳

```bash
# Start all services
make docker-compose

# Stop services
make docker-compose-down
```

**Services available at:**
- API: http://localhost:8000
- MLflow UI: http://localhost:5000

### Option 3: Step-by-Step Manual Setup 🔧

```bash
# 1. Create virtual environment
make venv

# 2. Activate environment
source venv/bin/activate

# 3. Install dependencies
make install

# 4. Create directories
make setup

# 5. Download data (optional)
make download-data
```

## Virtual Environment Commands

### Available Makefile Targets

| Command | Description |
|---------|-------------|
| `make venv` | Create virtual environment |
| `make venv-activate` | Show activation command |
| `make venv-clean` | Remove virtual environment |
| `make install` | Install dependencies (requires active venv) |
| `make setup` | Create directory structure |
| `make setup-all` | Complete setup (venv + install + setup) |
| `make clean` | Remove temporary files |
| `make clean-all` | Remove temp files + venv |

### Activating Virtual Environment

After creating the virtual environment:

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

You'll see `(venv)` prefix in your terminal when activated.

### Deactivating Virtual Environment

```bash
deactivate
```

## Project Workflow with Virtual Environment

### 1. Initial Setup

```bash
# Clone repository
git clone <your-repo-url>
cd MLOPs-Project

# Complete setup
make setup-all

# Activate environment
source venv/bin/activate
```

### 2. Train Model

```bash
# Train basic model
make train

# Train with hyperparameter tuning
make train-tuned

# Train ensemble model
make train-ensemble
```

### 3. Start Services

```bash
# Terminal 1: Start MLflow UI
make mlflow-ui

# Terminal 2: Start API server
make serve
```

### 4. Run Tests

```bash
# Run all tests
make test

# Test self-healing capabilities
python scripts/test_self_healing.py
```

### 5. Monitor and Self-Heal

```bash
# Run monitoring service
python scripts/run_monitoring.py

# Auto-fix data issues
python scripts/auto_fix_data_issues.py --data-path data/raw/housing.csv

# Auto-retrain on drift
python scripts/auto_retrain_on_drift.py --drift-detected

# Test service recovery
python scripts/auto_recover_service.py
```

## Scripts Reference

### setup_venv.sh

Comprehensive virtual environment setup script.

**Usage:**
```bash
./scripts/setup_venv.sh
```

**Features:**
- Creates Python virtual environment
- Upgrades pip, setuptools, wheel
- Installs all project dependencies
- Creates directory structure
- Makes scripts executable
- Optional data download

**Options:**
```bash
./scripts/setup_venv.sh --download-data    # Include data download
```

### quick_start.sh

One-command startup for entire pipeline.

**Usage:**
```bash
./quick_start.sh
```

**What it does:**
1. Checks if setup is complete
2. Runs setup_venv.sh if needed
3. Activates virtual environment
4. Trains a model (if none exists)
5. Starts MLflow UI (background)
6. Starts API server (foreground)

**Services started:**
- MLflow UI: http://localhost:5000 (background)
- API: http://localhost:8000 (foreground)

## Troubleshooting

### "python3: command not found"

Install Python 3.10+:

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-venv python3-pip

# macOS
brew install python@3.10

# Windows
# Download from https://www.python.org/downloads/
```

### "venv: No module named venv"

Install venv module:

```bash
# Ubuntu/Debian
sudo apt install python3-venv

# The module is included in standard Python installation on macOS/Windows
```

### "Permission denied" when running scripts

Make scripts executable:

```bash
chmod +x scripts/*.sh scripts/*.py
```

### Virtual environment not activating

Verify creation:

```bash
ls -la venv/bin/activate

# If missing, recreate:
make venv-clean
make venv
```

### Dependencies not installing

Upgrade pip first:

```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel
make install
```

### MLflow or API won't start

Check ports are free:

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check if port 5000 is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>
```

## Virtual Environment Benefits

### Development
- ✅ Isolated dependencies
- ✅ No system Python conflicts
- ✅ Easy cleanup (delete venv folder)
- ✅ Reproducible environment
- ✅ Fast setup and teardown

### Production
- 🐳 Use Docker instead (recommended)
- 📦 Better isolation
- 🔒 Security hardening
- 🚀 Easy scaling

## Environment Variables

The virtual environment automatically uses:

```bash
VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
```

Override in Makefile if needed:

```makefile
VENV=.venv  # Use .venv instead of venv
```

## Cleaning Up

### Remove virtual environment only:

```bash
make venv-clean
```

### Remove everything:

```bash
make clean-all
```

This removes:
- Virtual environment
- Python cache files
- Test artifacts
- Build artifacts
- Generated files (mlflow, monitoring, etc.)

## Integration with CI/CD

The virtual environment setup is **development-focused**. 

GitHub Actions workflow uses:
- Docker containers for consistency
- Cached dependencies for speed
- Matrix testing across Python versions

Local development uses venv for flexibility.

## Next Steps

After setup:

1. **Verify installation:**
   ```bash
   source venv/bin/activate
   python -c "import mlflow, fastapi, evidently; print('All packages installed!')"
   ```

2. **Train your first model:**
   ```bash
   make train
   ```

3. **Start services:**
   ```bash
   make serve      # API
   make mlflow-ui  # MLflow
   ```

4. **Test self-healing:**
   ```bash
   python scripts/test_self_healing.py
   ```

5. **Read documentation:**
   - [Self-Healing Guide](SELF_HEALING.md)
   - [Architecture Overview](ARCHITECTURE.md)
   - [Implementation Summary](../IMPLEMENTATION_SUMMARY.md)

## Support

For issues or questions:
- Check troubleshooting section above
- Review [README.md](../README.md)
- Check GitHub Issues
- Review workflow logs in GitHub Actions

---

**Happy Coding!** 🚀
