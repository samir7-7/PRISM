#!/bin/bash

set -e

echo "Creating virtual environment..."
python -m venv venv

echo "Activating virtual environment..."
source venv/Scripts/activate

echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Installing frontend dependencies..."
cd frontend/prism
npm install
cd ../../

echo "Done! Environment is ready."