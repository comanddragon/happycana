FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .

# Tell Django which settings to use during the image build
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Build static files into the Docker image
RUN python manage.py collectstatic --noinput

EXPOSE 10000

CMD gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:$PORT