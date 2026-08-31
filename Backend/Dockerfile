FROM python:3.13-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first so this layer is cached
# unless requirements change.
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy application source
COPY . .

# Collect static files during the image build.
# The resulting /app/staticfiles directory becomes part
# of the Docker image and does not need to be generated
# when the container starts.
RUN python manage.py collectstatic --noinput

EXPOSE 10000

# Static files are already collected in the image.
# Render provides $PORT at runtime.
CMD gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:$PORT