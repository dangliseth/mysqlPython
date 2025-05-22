import os
import keyring

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key')
MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'root'
MYSQL_DATABASE_PASSWORD = keyring.get_password("inventory_app_mysql", "root")
MYSQL_DATABASE_DB = 'inventory_database'