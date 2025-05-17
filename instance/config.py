import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key')
MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'app_user'
MYSQL_DATABASE_PASSWORD = 'test'
MYSQL_DATABASE_DB = 'inventory_database'