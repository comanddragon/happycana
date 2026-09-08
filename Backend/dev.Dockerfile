FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/development.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.development

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]