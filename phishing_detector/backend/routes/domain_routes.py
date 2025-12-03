from flask import Blueprint, request, jsonify
from database import db
from models.database import MaliciousDomain, WhitelistedDomain

domain_bp = Blueprint('domain', __name__)

@domain_bp.route('/malicious_domains', methods=['GET'])
def get_malicious_domains():
    """Get all detected malicious domains"""
    domains = MaliciousDomain.query.all()
    return jsonify([domain.domain for domain in domains])

@domain_bp.route('/whitelist_domain', methods=['POST'])
def whitelist_domain():
    """Add domain to whitelist"""
    data = request.get_json()
    domain = data.get('domain', '').strip().lower()
    
    if domain:
        # Add to whitelist if not exists
        if not WhitelistedDomain.query.filter_by(domain=domain).first():
            whitelist_entry = WhitelistedDomain(domain=domain)
            db.session.add(whitelist_entry)
        
        # Remove from malicious if exists
        malicious_entry = MaliciousDomain.query.filter_by(domain=domain).first()
        if malicious_entry:
            db.session.delete(malicious_entry)
        
        db.session.commit()
        return jsonify({'message': f'Domain {domain} whitelisted successfully'})
    
    return jsonify({'error': 'Domain is required'}), 400

@domain_bp.route('/remove_whitelist', methods=['POST'])
def remove_whitelist():
    """Remove domain from whitelist"""
    data = request.get_json()
    domain = data.get('domain', '').strip().lower()
    
    whitelist_entry = WhitelistedDomain.query.filter_by(domain=domain).first()
    if whitelist_entry:
        db.session.delete(whitelist_entry)
        db.session.commit()
        return jsonify({'message': f'Domain {domain} removed from whitelist'})
    
    return jsonify({'error': 'Domain not found in whitelist'}), 404

@domain_bp.route('/whitelisted_domains', methods=['GET'])
def get_whitelisted_domains():
    """Get all whitelisted domains"""
    domains = WhitelistedDomain.query.all()
    return jsonify([domain.domain for domain in domains])

def add_malicious_domain(domain):
    """Add domain to malicious list if not whitelisted"""
    domain = domain.strip().lower()
    if not is_domain_whitelisted(domain):
        if not MaliciousDomain.query.filter_by(domain=domain).first():
            malicious_entry = MaliciousDomain(domain=domain)
            db.session.add(malicious_entry)
            db.session.commit()

def is_domain_whitelisted(domain):
    """Check if domain is whitelisted"""
    return WhitelistedDomain.query.filter_by(domain=domain.strip().lower()).first() is not None