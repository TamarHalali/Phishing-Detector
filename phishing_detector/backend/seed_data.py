from app import app
from database import db
from models.email import UntrustedDomain, UntrustedUrl

def seed_database():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add untrusted domains if they don't exist
        untrusted_domains = [
            ('tempmail.com', 80),
            ('guerrillamail.com', 85),
            ('10minutemail.com', 90),
            ('mailinator.com', 75)
        ]
        
        for domain, risk_score in untrusted_domains:
            if not UntrustedDomain.query.filter_by(domain=domain).first():
                untrusted_domain = UntrustedDomain(domain=domain, risk_score=risk_score)
                db.session.add(untrusted_domain)
        
        # Add untrusted URLs if they don't exist
        untrusted_urls = [
            ('http://bit.ly/suspicious', 70),
            ('http://tinyurl.com/phish', 75),
            ('https://fake-bank.com', 95)
        ]
        
        for url, risk_score in untrusted_urls:
            if not UntrustedUrl.query.filter_by(url=url).first():
                untrusted_url = UntrustedUrl(url=url, risk_score=risk_score)
                db.session.add(untrusted_url)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()