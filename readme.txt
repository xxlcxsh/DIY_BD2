создать venv

Postgresql перед запуском
CREATE DATABASE DIY_DB;
CREATE USER projuser WITH PASSWORD 'mypassword';
ALTER ROLE projuser SET client_encoding TO 'utf8';
ALTER ROLE projuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE projuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE DIY_DB TO projuser;

Перед запуском
python manage.py makemigrations
python manage.py migrate
для запуска сайта - 'python manage.py runserver'

