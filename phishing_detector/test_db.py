import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from backend.database import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_database_connection():
    with app.app_context():
        assert db.engine is not None