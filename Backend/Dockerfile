FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt && pip install --upgrade pip

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.production

# These values exist only for collectstatic's settings import and are not
# persisted in the image. Production must supply every required value at run
# time; no placeholder credential can accidentally become a live fallback.
RUN DJANGO_SECRET_KEY=collectstatic-only-not-a-runtime-secret-0000000000000000 \
    ALLOWED_HOSTS=localhost \
    DATABASE_URL=postgresql://build:build@localhost:5432/build \
    CORS_ALLOWED_ORIGINS=http://localhost:3000 \
    AWS_ACCESS_KEY_ID=collectstatic \
    AWS_SECRET_ACCESS_KEY=collectstatic \
    AWS_STORAGE_BUCKET_NAME=collectstatic \
    SENTRY_DSN= \
    python manage.py collectstatic --noinput

EXPOSE 10000

CMD ["sh", "-c", "exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:${PORT:-10000}"]
