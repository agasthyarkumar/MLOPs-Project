#!/bin/bash

# Script to download the California Housing dataset
# This is an alternative to the Boston Housing dataset (deprecated in sklearn)

echo "🔽 Downloading California Housing Dataset..."

# Create data directory if it doesn't exist
mkdir -p data/raw

# Download the dataset
curl -o data/raw/housing.csv https://raw.githubusercontent.com/ageron/handson-ml/master/datasets/housing/housing.csv

if [ -f "data/raw/housing.csv" ]; then
    echo "✅ Dataset downloaded successfully!"
    echo "📊 Dataset location: data/raw/housing.csv"
    
    # Show basic info