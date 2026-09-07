.PHONY: check ci check-dev check-prod lint migrations test schema format fix run

# Run all validation across both environments
check: check-dev check-prod

ci: check
# Development / test environment checks
check-dev: lint migrations test schema
	DJANGO_SETTINGS_MODULE=config.settings.test python manage.py check

# Production settings validation
check-prod:
	DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy

# Linting
lint:
	ruff check . --exclude .venv,.output,.scripts,staticfiles

# Ensure models and migrations are in sync
migrations:
	DJANGO_SETTINGS_MODULE=config.settings.test python manage.py makemigrations --check --dry-run

# Run tests
test:
	DJANGO_SETTINGS_MODULE=config.settings.test pytest -q

# Validate OpenAPI schema generation
schema:
	DJANGO_SETTINGS_MODULE=config.settings.test python manage.py spectacular --file /tmp/openapi.yml

# Formatting
format:
	ruff format .

# Auto-fix lint issues where possible
fix:
	ruff check . --fix --exclude .venv,.output,.scripts,staticfiles
	ruff format .

# Local development server
run:
	python manage.py runserver