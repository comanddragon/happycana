FROM python:3.13-slim

WORKDIR /app

# System deps needed for Pillow / psycopg2-binary at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Install deps first so this layer is cached unless requirements change
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Now copy the rest of the code
COPY . .

EXPOSE 10000
CMD python manage.py collectstatic --noinput && \
    python manage.py migrate --noinput && \
    gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:10000