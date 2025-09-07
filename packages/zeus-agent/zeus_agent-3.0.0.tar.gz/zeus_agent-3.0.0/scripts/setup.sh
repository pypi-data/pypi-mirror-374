#!/bin/bash

# Agent Development Center - Setup Script
echo "🚀 Agent Development Center - Environment Setup"
echo "=============================================="

# Check Python
echo "Checking Python..."
python3 --version || { echo "Python3 not found!"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p logs data workspace/projects

# Copy config
echo "Setting up configuration..."
cp config/default.yaml config/local.yaml

echo "✅ Setup complete!"
echo "Next steps:"
echo "1. source venv/bin/activate"
echo "2. Edit config/local.yaml"
echo "3. python main.py --help" 