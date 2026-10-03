# ---------- Etapa 1: build do frontend ----------
FROM node:24-bookworm-slim AS frontend

WORKDIR /app/casa_aurora_frontend

# Copia apenas package*.json primeiro (melhor cache)
COPY casa_aurora_frontend/package.json casa_aurora_frontend/package-lock.json ./

RUN npm ci

# Copia o restante do frontend
COPY casa_aurora_frontend/ ./

RUN npm run build -- --base=/static/


# ---------- Etapa 2: backend Django ----------
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Backend
WORKDIR /app/casa_aurora_backend

# Copia requirements.txt explicitamente
COPY casa_aurora_backend/requirements.txt ./requirements.txt

# Instala dependências
RUN python -m pip install --no-cache-dir -r ./requirements.txt

# Copia o restante do backend
COPY casa_aurora_backend/ ./

# Copia o build do frontend para dentro do backend
COPY --from=frontend /app/casa_aurora_frontend/dist/ ./casa_aurora_frontend/dist/

# Coleta estáticos
RUN DJANGO_SECRET_KEY=build-only-not-for-runtime \
    DJANGO_DEBUG=false \
    DJANGO_ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

# Comando de inicialização
CMD ["sh", "-c", "gunicorn casa_aurora.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --access-logfile - --error-logfile -"]