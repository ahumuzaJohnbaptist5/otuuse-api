#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
# Apply migrations to the configured persistent PostgreSQL database.
python manage.py migrate --noinput
# One-time recovery; remove after a successful login.
python manage.py fix_admin
