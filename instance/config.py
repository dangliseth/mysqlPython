import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key')
MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'root'
MYSQL_DATABASE_PASSWORD = os.environ.get('MYSQL_DATABASE_PASSWORD')
MYSQL_DATABASE_DB = 'inventory_database'