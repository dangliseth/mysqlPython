import os

# Read secrets from db.txt
secrets_path = os.path.join(os.path.dirname(__file__), 'db.txt')
secrets = {}
if os.path.exists(secrets_path):
    with open(secrets_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                secrets[key.strip()] = value.strip()

SECRET_KEY = secrets.get('SECRET_KEY', os.environ.get('SECRET_KEY', 'fallback-insecure-key'))
MYSQL_DATABASE_HOST = 'localhost'
MYSQL_DATABASE_USER = 'root'
MYSQL_DATABASE_PASSWORD = secrets.get('MYSQL_DATABASE_PASSWORD', os.environ.get('MYSQL_DATABASE_PASSWORD'))
MYSQL_DATABASE_DB = 'inventory_database'