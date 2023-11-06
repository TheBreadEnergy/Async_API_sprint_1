#!/usr/bin/env bash

set -e

./manage.py collectstatic --noinput
while ! nc -z "$DB_HOST" "$DB_PORT"; do sleep 1; done;
./manage.py migrate
uwsgi --strict --ini uwsgi.ini
