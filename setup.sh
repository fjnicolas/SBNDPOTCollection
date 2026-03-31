#!/usr/bin/env bash

# Exit on error
set -e

ENV_NAME="venv-sbndpot"

echo "Creating virtual environment..."
python3 -m venv $ENV_NAME

echo "Activating virtual environment..."
source $ENV_NAME/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

if [ -f requirements.txt ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found, skipping..."
fi

echo "Setup complete!"