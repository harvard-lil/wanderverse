# wanderverse

```
pip install -r requirements.txt
psql --user=postgres -c "CREATE DATABASE wanderverse"
./manage.py migrate
./manage.py loaddata test_data_user.json
./manage.py loaddata test_data_poems.json
./manage.py loaddata test_data_verses.json
```

In Docker world:

```
docker-compose up -d
bash docker/init.sh
docker-compose exec web ./manage.py runserver 0.0.0.0:8000
```

To clean up:


```
docker-compose down
bash docker/clean.sh
```
