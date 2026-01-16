#!/usr/bin/env bash
# Render.com build script for backend

set -o errexit

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr libzbar0 libgl1-mesa-glx libglib2.0-0

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

echo "Backend build complete!"
