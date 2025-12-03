from database import db
from datetime import datetime
import json

class EmailAnalysis(db.Model):
    __tablename__ = 'email_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.Text)
    body = db.Column(db.Text)
    urls = db.Column(db.Text)  # JSON string
    attachments = db.Column(db.Text)  # JSON string
    ai_score = db.Column(db.Integer)
    ai_summary = db.Column(db.Text)
    ai_indicators = db.Column(db.Text)  # JSON string
    ai_detections = db.Column(db.Text)  # JSON string
    url_analysis = db.Column(db.Text)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'subject': self.subject,
            'ai_score': self.ai_score,
            'ai_summary': self.ai_summary,
            'timestamp': self.timestamp.isoformat(),
            'parsed_email': {
                'sender': self.sender,
                'subject': self.subject,
                'body': self.body,
                'urls': json.loads(self.urls) if self.urls else [],
                'attachments': json.loads(self.attachments) if self.attachments else []
            },
            'ai_analysis': {
                'score': self.ai_score,
                'summary': self.ai_summary,
                'indicators': json.loads(self.ai_indicators) if self.ai_indicators else [],
                'detections': json.loads(self.ai_detections) if self.ai_detections else [],
                'url_analysis': json.loads(self.url_analysis) if self.url_analysis else []
            }
        }

class MaliciousDomain(db.Model):
    __tablename__ = 'malicious_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WhitelistedDomain(db.Model):
    __tablename__ = 'whitelisted_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DomainCache(db.Model):
    __tablename__ = 'domain_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(500), unique=True, nullable=False)
    result = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)