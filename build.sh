#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export VITE_API_BASE_URL=""

cd "$PROJECT_ROOT/casa_aurora_frontend"
npm ci
npm run build -- --base=/static/

cd "$PROJECT_ROOT/casa_aurora_backend"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput