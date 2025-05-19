import pytest
from invemp import create_app
from invemp.dashboard_helpers import is_valid_table, get_items_columns, get_dropdown_options

def test_is_valid_table():
    assert is_valid_table('items')
    assert not is_valid_table('notatable')

def test_get_items_columns():
    cols = get_items_columns()
    assert 'item_id' in cols
    assert 'item_name' in cols

def test_get_dropdown_options_keys(app, monkeypatch):
    class FakeCursor:
        def execute(self, q): pass
        def fetchall(self): return [(1, 'Test Employee')]
        def close(self): pass
    monkeypatch.setattr('invemp.db.get_cursor', lambda: FakeCursor())
    from invemp.dashboard_helpers import get_dropdown_options
    with app.app_context():
        opts = get_dropdown_options()
        assert 'category' in opts
        assert 'department' in opts
        assert 'Assigned To' in opts
        assert 'status' in opts
        assert 'account_type' in opts
