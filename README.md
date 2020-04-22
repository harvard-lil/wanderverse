# wanderverse

```
pip install -r requirements.txt
psql --user=postgres -c "CREATE DATABASE wanderverse"
./manage.py migrate
./manage.py loaddata test_data_user.json
./manage.py loaddata test_data_poems.json
./manage.py loaddata test_data_verses.json
```