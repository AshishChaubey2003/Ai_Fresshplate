#!/usr/bin/env bash
# Render build script. Stop at the first failure - without this, a failed
# migration still reports a "successful" deploy and the site breaks later.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# TEMPORARY: both lines below are one-time setup for the fresh database.
# Delete them after the next successful deploy.
python manage.py seed_menu
python manage.py createsuperuser --noinput --email admin@freshplate.com --full_name "Admin" || true