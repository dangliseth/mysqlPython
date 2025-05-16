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

def test_dashboard_user_pdf_requires_login(client):
    response = client.get('/items/convert_pdf')
    assert response.status_code in (302, 308, 401)
    location = response.headers.get('Location', '').lower()
    assert location.endswith('/') or 'login' in location

def test_dashboard_user_pdf_qr_requires_login(client):
    response = client.get('/items/convert_pdf_qr')
    assert response.status_code in (302, 308, 401)
    location = response.headers.get('Location', '').lower()
    assert location.endswith('/') or 'login' in location
