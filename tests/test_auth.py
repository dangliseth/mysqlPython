import pytest
from flask import g, session
from invemp import create_app
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test'})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# --- Auth route tests ---

def test_login_get(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()

@patch('invemp.auth.get_cursor')
def test_login_post_invalid_user(mock_cursor, client):
    mock_cursor.return_value.execute.return_value = None
    mock_cursor.return_value.fetchone.return_value = None
    response = client.post('/auth/login', data={'username': 'nouser', 'password': 'pass'})
    assert b'Incorrect username' in response.data

@patch('invemp.auth.get_cursor')
def test_login_post_invalid_password(mock_cursor, client):
    user = (1, 'test', 'hashed', 'user')
    mock_cursor.return_value.execute.return_value = None
    mock_cursor.return_value.fetchone.return_value = user
    with patch('invemp.auth.check_password_hash', return_value=False):
        response = client.post('/auth/login', data={'username': 'test', 'password': 'wrong'})
        assert b'Incorrect password' in response.data

@patch('invemp.auth.get_cursor')
def test_logout(client, mock_cursor):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'login' in response.data.lower()

@patch('invemp.auth.get_cursor')
def test_register_get(mock_cursor, client):
    # Should require admin, so redirect to login if not logged in
    response = client.get('/auth/register', follow_redirects=True)
    assert b'login' in response.data.lower()

@patch('invemp.auth.get_cursor')
def test_register_post_missing_username(mock_cursor, client):
    # Simulate admin session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    # Mock admin user
    mock_cursor.return_value.execute.side_effect = [None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), None]
    data = {'username': '', 'password': 'pass', 'type': 'user'}
    response = client.post('/auth/register', data=data)
    assert b'Username is required' in response.data

@patch('invemp.auth.get_cursor')
def test_register_post_missing_password(mock_cursor, client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    mock_cursor.return_value.execute.side_effect = [None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), None]
    data = {'username': 'user', 'password': '', 'type': 'user'}
    response = client.post('/auth/register', data=data)
    assert b'Password is required' in response.data

@patch('invemp.auth.get_cursor')
def test_register_post_duplicate_user(mock_cursor, client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    mock_cursor.return_value.execute.side_effect = [None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), (2, 'user', 'hash', 'user')]
    data = {'username': 'user', 'password': 'pass', 'type': 'user'}
    response = client.post('/auth/register', data=data)
    assert b'already registered' in response.data

@patch('invemp.auth.get_cursor')
def test_register_post_success(mock_cursor, client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    # First fetch admin, then check user does not exist
    mock_cursor.return_value.execute.side_effect = [None, None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), None, None]
    data = {'username': 'newuser', 'password': 'pass', 'type': 'user'}
    response = client.post('/auth/register', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert '/dashboard_user' in response.headers['Location']

@patch('invemp.auth.get_cursor')
def test_reset_password_get_requires_admin(mock_cursor, client):
    # Not logged in, should redirect to login
    response = client.get('/auth/1/reset_password', follow_redirects=True)
    assert b'login' in response.data.lower()

@patch('invemp.auth.get_cursor')
def test_reset_password_post_missing_fields(mock_cursor, client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    # Mock admin user and entry fetch
    mock_cursor.return_value.execute.side_effect = [None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), (2, 'user', 'hash', 'user')]
    data = {'new-password': '', 'confirm-password': ''}
    response = client.post('/auth/2/reset_password', data=data)
    assert b'Both password fields are required' in response.data

@patch('invemp.auth.get_cursor')
def test_reset_password_post_mismatch(mock_cursor, client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    mock_cursor.return_value.execute.side_effect = [None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), (2, 'user', 'hash', 'user')]
    data = {'new-password': 'abc', 'confirm-password': 'def'}
    response = client.post('/auth/2/reset_password', data=data)
    assert b'Passwords must match' in response.data

@patch('invemp.auth.get_cursor')
def test_reset_password_post_success(mock_cursor, client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    # Fetch admin, fetch entry, then update
    mock_cursor.return_value.execute.side_effect = [None, None, None]
    mock_cursor.return_value.fetchone.side_effect = [(1, 'admin', 'hash', 'admin'), (2, 'user', 'hash', 'user'), None]
    data = {'new-password': 'abc', 'confirm-password': 'abc'}
    response = client.post('/auth/2/reset_password', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert '/dashboard_user' in response.headers['Location']
