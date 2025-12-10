import pytest
import json
from app import app, db
from models.database import EmailAnalysis

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_database_connection(client):
    """Test database connection"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_email_creation(client):
    """Test email record creation"""
    with app.app_context():
        email = EmailAnalysis(
            sender='test@example.com',
            subject='Test Email',
            body='Test body',
            urls='[]',
            attachments='[]',
            ai_score=0.5,
            ai_summary='Test summary'
        )
        db.session.add(email)
        db.session.commit()
        
        saved_email = EmailAnalysis.query.first()
        assert saved_email.sender == 'test@example.com'
        assert saved_email.subject == 'Test Email'

def test_container_info(client):
    """Test container info endpoint"""
    response = client.get('/container-info')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'container_id' in data
    assert 'hostname' in data
    assert 'requests_handled' in data

def test_history_endpoint(client):
    """Test history endpoint with database"""
    response = client.get('/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'emails' in data
    assert 'container_info' in data