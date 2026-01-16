#!/usr/bin/env bash
# Render.com build script for backend

set -o errexit

echo "Installing system dependencies..."
apt-get update
apt-get install -y tesseract-ocr libzbar0 libgl1-mesa-glx libglib2.0-0

echo "Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Backend build complete!"
