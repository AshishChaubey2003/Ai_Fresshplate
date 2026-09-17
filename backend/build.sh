#!/usr/bin/env bash
# Render build script. Stop at the first failure - without this, a failed
# migration still reports a "successful" deploy and the site breaks later.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# TEMPORARY: seeds the live menu once. Remove after the first successful deploy.
python manage.py seed_menu