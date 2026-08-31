FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.production

ENV DJANGO_SECRET_KEY="build-only-placeholder"
ENV ALLOWED_HOSTS="localhost"
ENV DATABASE_URL="postgresql://build:build@localhost:5432/build"
ENV CORS_ALLOWED_ORIGINS="http://localhost:3000"
ENV AWS_ACCESS_KEY_ID="build-only-placeholder"
ENV AWS_SECRET_ACCESS_KEY="build-only-placeholder"
ENV AWS_STORAGE_BUCKET_NAME="build-only-placeholder"
ENV SENTRY_DSN="https://00000000000000000000000000000000@localhost/0"

ENV AWS_S3_REGION_NAME=""
ENV AWS_CLOUDFRONT_DOMAIN=""
ENV RESEND_API_KEY=""
ENV ADMIN_NOTIFICATION_EMAIL=""
ENV DEFAULT_FROM_EMAIL=""
ENV RESEND_FROM_EMAIL=""
ENV STORE_NAME=""
ENV FRONTEND_URL=""
ENV BACKEND_URL=""
ENV STORE_LOGO_URL=""
ENV SUPPORT_EMAIL=""
ENV STORE_ADDRESS=""

RUN python manage.py collectstatic --noinput

EXPOSE 10000

CMD gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:${PORT:-10000}