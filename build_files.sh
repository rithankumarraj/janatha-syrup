#!/usr/bin/env bash
# Build script for Vercel deployment
echo "Building project assets..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "Build finished successfully!"
