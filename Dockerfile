# Déploiement Render (ou autre) : runtime Docker = build reproductible, sans Poetry/uv implicite.
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

COPY toftal_python /app/toftal_python

WORKDIR /app/toftal_python

ENV PYTHONUNBUFFERED=1

# Render fournit la variable PORT au runtime
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 app:app"]
