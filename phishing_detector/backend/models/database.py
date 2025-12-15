from database import db
from datetime import datetime
import json

class EmailAnalysis(db.Model):
    __tablename__ = 'email_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500))
    sender_domain = db.Column(db.String(255))
    ai_score = db.Column(db.Integer)
    risk_level = db.Column(db.String(50))  # Low, Medium, High, Critical
    ai_summary = db.Column(db.Text)
    threat_indicators = db.Column(db.Text)  # JSON string - key findings only
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'subject': self.subject,
            'sender_domain': self.sender_domain,
            'ai_score': self.ai_score,
            'risk_level': self.risk_level,
            'ai_summary': self.ai_summary,
            'threat_indicators': json.loads(self.threat_indicators) if self.threat_indicators else [],
            'timestamp': self.timestamp.isoformat()
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