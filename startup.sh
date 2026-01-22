#!/bin/bash

# Startup script for Azure App Service

echo "Starting Azure AI FastAPI Demo..."

# Install dependencies if not already installed
pip install -r requirements.txt

# Start the FastAPI application with gunicorn for production
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
