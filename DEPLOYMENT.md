# Deployment to Render (example)

This document explains how to deploy the Central Adventures Django app to Render.com.

Quick summary
- Use the provided `render.yaml` or set the Render web service `Start Command` to:

```
gunicorn central_adventures.wsgi:application --bind 0.0.0.0:$PORT
```

- Ensure `requirements.txt` contains `gunicorn`, `whitenoise`, and any DB driver (e.g. `psycopg2-binary`) — this repo already lists them.
- Set the `DJANGO_SETTINGS_MODULE` environment variable to `central_adventures.settings` (the `render.yaml` already does this).
- Provide a secure `SECRET_KEY` in Render's environment variables (do not keep the development key in production).
- Set `DEBUG` to `False` in Render env vars.
- Configure `DATABASE_URL` (Render Postgres) and other secrets in Render env vars.

Render (service) example
1. Create a new Web Service on Render, connect the repository and choose the `main` branch.
2. Either add the `render.yaml` at the repository root (already included) or set the following fields in the Render UI:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn central_adventures.wsgi:application --bind 0.0.0.0:$PORT`
   - Environment Variables:
     - `DJANGO_SETTINGS_MODULE = central_adventures.settings`
     - `SECRET_KEY = <your-secret-here>`
     - `DEBUG = False`
     - `DATABASE_URL = postgres://...` (Render can provide this when you add a managed Postgres instance)

Static files and WhiteNoise
- `whitenoise` is listed in `requirements.txt`. To use it in production make sure you:
  1. Add `WhiteNoiseMiddleware` to `MIDDLEWARE` (below `SecurityMiddleware`).
  2. Set a `STATIC_ROOT` in your `settings.py` and run `collectstatic`.

Recommended production snippets for `central_adventures/settings.py` (do NOT paste your SECRET_KEY):

```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Read secret and debug from env
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-for-local')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Static files (production)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise (after SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... rest of middleware
]

# Use dj-database-url to parse DATABASE_URL when provided
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}

# Enable WhiteNoise compressed manifest static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Deployment checklist
- Add/ensure `SECRET_KEY`, `DATABASE_URL`, `DEBUG` env vars on Render.
- Attach a managed Postgres and set `DATABASE_URL` to the provided URL.
- Run a deploy — Render will run the `buildCommand` (migrations + collectstatic).
- Verify logs in Render; common follow-ups:
  - `ValueError: settings.DATABASES is improperly configured` → check `DATABASE_URL`.
  - `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty` → set `SECRET_KEY`.
  - Static files 404s → ensure `collectstatic` ran and `STATIC_ROOT` is configured.

If you want, I can add the `whitenoise` middleware lines directly to `settings.py` and set `STATIC_ROOT` and `STATICFILES_STORAGE` for you — tell me and I'll patch `central_adventures/settings.py` and run a quick local `collectstatic` to make sure nothing breaks.
