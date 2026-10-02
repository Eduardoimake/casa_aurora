FROM node:24-bookworm-slim AS frontend

WORKDIR /app/casa_aurora_frontend

COPY casa_aurora_frontend/package.json casa_aurora_frontend/package-lock.json ./
RUN npm ci

COPY casa_aurora_frontend/ ./
RUN npm run build -- --base=/static/

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/casa_aurora_backend

COPY casa_aurora_backend/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY casa_aurora_backend/ ./
COPY --from=frontend /app/casa_aurora_frontend/dist/ /app/casa_aurora_frontend/dist/

RUN DJANGO_SECRET_KEY=build-only-not-for-runtime \
    DJANGO_DEBUG=false \
    DJANGO_ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

CMD ["sh", "-c", "gunicorn casa_aurora.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --access-logfile - --error-logfile -"]