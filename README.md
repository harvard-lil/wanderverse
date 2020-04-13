# wanderverse

```
pip install -r requirements.txt
psql --user=postgres -c "CREATE DATABASE wanderverse"
./manage.py migrate
./manage.py loaddata seed_data_country.json
./manage.py loaddata test_data_user.json
./manage.py loaddata test_data_poems.json
./manage.py loaddata test_data_books.json
./manage.py loaddata test_data_lines.json
```