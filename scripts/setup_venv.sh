#!/bin/bash
# Setup Python Virtual Environment for MLOps Project

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🐍 Setting up Python Virtual Environment - MLOps Pipeline ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Python found: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "📚 Installing dev dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "📦 Installing package in editable mode..."
pip install -e .

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p data/{raw,processed,feature_store,reference,production} \
         models/backups \
         mlflow \
         monitoring/{reports,metrics,alerts} \
         logs \
         config \
         .github/triggers

echo "✅ Directories created!"

# Make scripts executable
echo ""
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true

# Download data (optional)
echo ""
read -p "📥 Download dataset now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/download_data.sh" ]; then
        bash scripts/download_data.sh
    else
        echo "⚠️  Download script not found, skipping..."
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ✅ Setup Complete!                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 To activate the virtual environment, run:"
echo "   source venv/bin/activate"
echo ""
echo "🚀 Quick start commands:"
echo "   make train              # Train model"
echo "   make serve              # Start API server"
echo "   make mlflow-ui          # Start MLflow UI"
echo "   make test-self-healing  # Test self-healing features"
echo ""
echo "📖 For all commands, run: make help"
echo ""
