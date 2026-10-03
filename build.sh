#!/usr/bin/env bash
set -euo pipefail

export VITE_API_BASE_URL=""

cd casa_aurora_frontend
npm ci
npm run build -- --base=/static/

cd ../casa_aurora_backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput