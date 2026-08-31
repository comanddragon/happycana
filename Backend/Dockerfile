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

# Temporary key used only during Docker build.
# The real key is provided by the hosting platform at runtime.
ARG DJANGO_SECRET_KEY=build-only-not-used-in-production
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

RUN python manage.py collectstatic --noinput

EXPOSE 10000

CMD gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:$PORT