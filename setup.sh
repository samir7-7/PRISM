#!/bin/bash

set -e

echo "Creating virtual environment..."
python -m venv venv

echo "Activating virtual environment..."
source venv/Scripts/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Done! Virtual environment is ready."