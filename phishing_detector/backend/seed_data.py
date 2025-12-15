from app import app
from database import db
from models.email import UntrustedDomain, UntrustedUrl

def seed_database():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add known suspicious domains if they don't exist
        untrusted_domains = [
            ('tempmail.com', 60),
            ('guerrillamail.com', 65),
            ('10minutemail.com', 70),
            ('mailinator.com', 55)
        ]
        
        for domain, risk_score in untrusted_domains:
            if not UntrustedDomain.query.filter_by(domain=domain).first():
                untrusted_domain = UntrustedDomain(domain=domain, risk_score=risk_score)
                db.session.add(untrusted_domain)
        
        # Add known suspicious URL patterns if they don't exist
        untrusted_urls = [
            ('bit.ly', 40),
            ('tinyurl.com', 35),
            ('t.co', 30)
        ]
        
        for url, risk_score in untrusted_urls:
            if not UntrustedUrl.query.filter_by(url=url).first():
                untrusted_url = UntrustedUrl(url=url, risk_score=risk_score)
                db.session.add(untrusted_url)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()