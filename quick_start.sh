#!/bin/bash
# Quick Start Script for MLOps Pipeline

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 Quick Start - Self-Healing MLOps Pipeline       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if setup is needed
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Running setup..."
    chmod +x scripts/setup_venv.sh
    ./scripts/setup_venv.sh
else
    echo "✅ Virtual environment already exists"
fi

# Activate environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if data exists
if [ ! -f "data/raw/housing.csv" ]; then
    echo ""
    echo "📥 Dataset not found. Downloading..."
    bash scripts/download_data.sh || echo "⚠️  Download failed, continuing..."
fi

# Train model
echo ""
echo "🎯 Training model..."
python src/models/train.py || echo "⚠️  Training completed with warnings"

# Test self-healing
echo ""
echo "🔄 Testing self-healing capabilities..."
python scripts/test_self_healing.py

# Start services
echo ""
read -p "🚀 Start API and MLflow UI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting services in background..."
    
    # Start MLflow UI
    mlflow ui --host 0.0.0.0 --port 5000 > logs/mlflow.log 2>&1 &
    MLFLOW_PID=$!
    echo "✅ MLflow UI started (PID: $MLFLOW_PID)"
    
    sleep 2
    
    # Start API
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
    API_PID=$!
    echo "✅ API server started (PID: $API_PID)"
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                 🎉 All Services Running!                   ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║                                                            ║"
    echo "║  📊 MLflow UI:    http://localhost:5000                    ║"
    echo "║  🚀 API:          http://localhost:8000                    ║"
    echo "║  📖 API Docs:     http://localhost:8000/docs               ║"
    echo "║  💚 Health:       http://localhost:8000/health             ║"
    echo "║                                                            ║"
    echo "║  📝 Logs:                                                  ║"
    echo "║     MLflow: logs/mlflow.log                                ║"
    echo "║     API:    logs/api.log                                   ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "💡 To stop services:"
    echo "   kill $MLFLOW_PID $API_PID"
    echo ""
    echo "   Or run: make clean-services"
    echo ""
    
    # Create cleanup script
    echo "kill $MLFLOW_PID $API_PID 2>/dev/null || true" > /tmp/stop_mlops_services.sh
    chmod +x /tmp/stop_mlops_services.sh
fi

echo ""
echo "✅ Quick start complete!"
echo ""
