import pytest
from invemp import create_app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_app_creation():
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test'})
    assert app is not None
    assert app.config['TESTING']
    assert app.config['SECRET_KEY'] == 'test'
