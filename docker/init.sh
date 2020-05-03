#!/usr/bin/env bash
set -e

docker-compose exec db psql --user=postgres -c "CREATE DATABASE wanderverse"
docker-compose exec web ./manage.py migrate
docker-compose exec web ./manage.py loaddata test_data_user.json
docker-compose exec web ./manage.py loaddata test_data_poems.json
docker-compose exec web ./manage.py loaddata test_data_verses.json
