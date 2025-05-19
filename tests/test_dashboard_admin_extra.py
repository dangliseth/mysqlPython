import pytest
from invemp import create_app

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test',
        'MYSQL_DATABASE_HOST': 'localhost',
        'MYSQL_DATABASE_USER': 'test_user',
        'MYSQL_DATABASE_PASSWORD': 'test_pass',
        'MYSQL_DATABASE_DB': 'inventory_database',
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_dashboard_admin_create_requires_admin(client):
    response = client.get('/items/create')
    assert response.status_code in (302, 308, 401)
    location = response.headers.get('Location', '').lower()
    assert location.endswith('/') or 'login' in location

def test_dashboard_admin_update_requires_admin(client):
    response = client.get('/items/1/update')
    assert response.status_code in (302, 308, 401, 404)

def test_dashboard_admin_delete_requires_admin(client):
    response = client.get('/items/1/delete')
    assert response.status_code in (302, 308, 401, 404)

def test_dashboard_admin_archive_scrap_requires_admin(client):
    response = client.get('/items/1/archive_scrap')
    assert response.status_code in (302, 308, 401, 404)
