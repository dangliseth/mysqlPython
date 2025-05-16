import pytest
from flask import session
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

def test_login_logout(client):
    # Test login page loads
    response = client.get('/auth/login')
    assert response.status_code == 200
    # Test login with invalid credentials
    response = client.post('/auth/login', data={'username': 'bad', 'password': 'bad'})
    assert b'incorrect' in response.data or response.status_code in (200, 401)
    # Test logout redirects
    response = client.get('/auth/logout')
    assert response.status_code in (302, 308)

def test_register_redirects_for_non_admin(client):
    # Should redirect to login or index if not admin
    response = client.get('/auth/register')
    assert response.status_code in (302, 308, 401)
    location = response.headers.get('Location', '').lower()
    assert location.endswith('/') or 'login' in location

def test_reset_password_requires_admin(client):
    response = client.get('/auth/1/reset_password')
    assert response.status_code in (302, 308, 401)
    location = response.headers.get('Location', '').lower()
    assert location.endswith('/') or 'login' in location
