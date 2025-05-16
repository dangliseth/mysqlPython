import pytest
from flask import g, session
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

# Example: test login page loads

def test_login_page_loads(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()

# Example: test register page requires admin (should redirect if not logged in)
def test_register_requires_admin(client):
    response = client.get('/auth/register')
    assert response.status_code in (302, 401)
    location = response.headers.get('Location', '').lower()
    assert 'login' in location or location.endswith('/')

# Example: test 404 for invalid route
def test_404(client):
    response = client.get('/nonexistent')
    assert response.status_code in (302, 404)
