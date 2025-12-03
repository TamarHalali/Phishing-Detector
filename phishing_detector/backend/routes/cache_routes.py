from flask import Blueprint, jsonify
from services.local_domain_cache import domain_cache

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/cache_stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    from models.database import DomainCache
    import json
    
    cache_entries = DomainCache.query.all()
    total_entries = len(cache_entries)
    malicious_count = 0
    
    for entry in cache_entries:
        try:
            result = json.loads(entry.result)
            if result.get('is_malicious', False):
                malicious_count += 1
        except:
            pass
    
    safe_count = total_entries - malicious_count
    
    return jsonify({
        'total_entries': total_entries,
        'malicious_domains': malicious_count,
        'safe_domains': safe_count,
        'cache_duration_hours': 24
    })

@cache_bp.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear all cached domain results"""
    from models.database import DomainCache, db
    
    DomainCache.query.delete()
    db.session.commit()
    return jsonify({'message': 'Cache cleared successfully'})