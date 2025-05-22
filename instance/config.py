import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key')
MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'root'

# Read DB password from a local file if it exists, else fallback to env or default
password_file = os.path.join(os.path.dirname(__file__), 'db_password.txt')
if os.path.exists(password_file):
    with open(password_file, 'r', encoding='utf-8') as f:
        MYSQL_DATABASE_PASSWORD = f.read().strip()
else:
    MYSQL_DATABASE_PASSWORD = os.environ.get('MYSQL_DATABASE_PASSWORD', 'fallback-insecure-password')

MYSQL_DATABASE_DB = 'inventory_database'