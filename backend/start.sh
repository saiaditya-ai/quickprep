#!/bin/bash
# Start script for Render deployment

echo "Starting QuickPrep API server..."
uvicorn main:app --host 0.0.0.0 --port $PORT