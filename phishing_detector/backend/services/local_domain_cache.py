from datetime import datetime, timedelta
from database import db
from models.database import DomainCache
import json

class LocalDomainCache:
    def __init__(self):
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
    
    def get_cached_result(self, domain):
        """Get cached result for domain if exists and not expired"""
        domain = domain.lower().strip()
        
        cache_entry = DomainCache.query.filter_by(domain=domain).first()
        if cache_entry:
            if datetime.now() - cache_entry.created_at < self.cache_duration:
                return json.loads(cache_entry.result)
            else:
                # Remove expired cache
                db.session.delete(cache_entry)
                db.session.commit()
        
        return None
    
    def cache_result(self, domain, result):
        """Cache domain analysis result"""
        domain = domain.lower().strip()
        
        # Remove existing cache entry if exists
        existing = DomainCache.query.filter_by(domain=domain).first()
        if existing:
            db.session.delete(existing)
        
        # Add new cache entry
        cache_entry = DomainCache(domain=domain, result=json.dumps(result))
        db.session.add(cache_entry)
        db.session.commit()
    
    def is_known_malicious(self, domain):
        """Check if domain is known to be malicious from cache"""
        cached = self.get_cached_result(domain)
        return cached and cached.get('is_malicious', False)
    
    def is_known_safe(self, domain):
        """Check if domain is known to be safe from cache"""
        cached = self.get_cached_result(domain)
        return cached and not cached.get('is_malicious', False) and cached.get('risk_score', 0) == 0

# Global cache instance
domain_cache = LocalDomainCache()