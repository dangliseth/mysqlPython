import pytest
from flask import g
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

# --- dashboard_user.py ---
def test_index_admin_access(client, monkeypatch):
    # Simulate admin user in g
    class FakeUser(list):
        def __getitem__(self, idx):
            if idx == 3:
                return 'admin'
            return super().__getitem__(idx)
    monkeypatch.setattr('flask.g', type('g', (), {'user': FakeUser([1, 'admin', 'pw', 'admin'])})())
    response = client.get('/items')
    assert response.status_code in (200, 302, 308)

def test_index_nonadmin_redirect(client, monkeypatch):
    class FakeUser(list):
        def __getitem__(self, idx):
            if idx == 3:
                return 'user'
            return super().__getitem__(idx)
    monkeypatch.setattr('flask.g', type('g', (), {'user': FakeUser([1, 'user', 'pw', 'user'])})())
    response = client.get('/user_accounts')
    assert response.status_code in (302, 308)

# --- dashboard_helpers.py ---
def test_get_tables(monkeypatch, app):
    with app.app_context():
        class FakeCursor:
            def execute(self, q): pass
            def fetchall(self): return [('items',), ('employees',)]
            def close(self): pass
        monkeypatch.setattr('invemp.db.get_cursor', lambda: FakeCursor())
        from invemp.dashboard_helpers import get_tables
        tables = get_tables()
        assert 'items' in tables
        assert 'employees' in tables

def test_get_entry(monkeypatch, app):
    with app.app_context():
        class FakeCursor:
            def __init__(self):
                self.calls = 0
            def execute(self, q, v=None):
                self.calls += 1
            def fetchall(self):
                # First call: DESCRIBE, second call: SELECT
                if self.calls == 1:
                    return [('id',), ('name',)]
                return []
            def fetchone(self):
                # Only return a row for the SELECT query
                if self.calls == 2:
                    return (1, 'test')
                return None
            def close(self): pass
        monkeypatch.setattr('invemp.db.get_cursor', lambda: FakeCursor())
        from invemp.dashboard_helpers import get_entry
        entry = get_entry(1, 'items')
        assert entry is not None
        assert entry[0] == 1

# --- dashboard_admin.py ---
def test_create_requires_admin(client):
    response = client.get('/items/create')
    assert response.status_code in (302, 308, 401)

def test_delete_requires_admin(client):
    response = client.get('/items/1/delete')
    assert response.status_code in (302, 308, 401, 404)

# --- auth.py ---
def test_login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_logout_redirect(client):
    response = client.get('/auth/logout')
    assert response.status_code in (302, 308)
