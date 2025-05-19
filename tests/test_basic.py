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

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_index_redirects_to_login(client):
    response = client.get('/')
    # Should redirect to login if not logged in
    assert response.status_code in (302, 308, 401)
    location = response.headers.get('Location', '').lower()
    assert location.endswith('/') or 'login' in location

def test_favicon(client):
    response = client.get('/favicon.ico')
    assert response.status_code in (301, 302, 308)
    assert 'static/icons/favicon/favicon.ico' in response.headers.get('Location', '').lower()
