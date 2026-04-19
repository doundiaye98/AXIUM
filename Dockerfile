# Déploiement Render (ou autre) : runtime Docker = build reproductible, sans Poetry/uv implicite.
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

COPY toftal_python /app/toftal_python

WORKDIR /app/toftal_python

ENV PYTHONUNBUFFERED=1

# Render injecte PORT. Ne définisse pas de « Start Command » dans le tableau de bord
# (sinon vous écrasez cette ligne et Gunicorn peut ne pas écouter sur $PORT → 404 / 502).
CMD ["sh", "-c", "if [ -z \"${PORT}\" ]; then echo 'ERROR: PORT is empty' >&2; exit 1; fi; exec gunicorn --bind \"0.0.0.0:${PORT}\" --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app"]
