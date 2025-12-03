import json
import os
from datetime import datetime

class PersistentStorage:
    def __init__(self):
        self.data_dir = 'data'
        self.history_file = os.path.join(self.data_dir, 'analysis_history.json')
        self.domains_file = os.path.join(self.data_dir, 'malicious_domains.json')
        self.whitelist_file = os.path.join(self.data_dir, 'whitelisted_domains.json')
        self.cache_file = os.path.join(self.data_dir, 'domain_cache.json')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_history(self):
        """Load analysis history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_history(self, history):
        """Save analysis history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_malicious_domains(self):
        """Load malicious domains from file"""
        try:
            if os.path.exists(self.domains_file):
                with open(self.domains_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
        except:
            pass
        return set()
    
    def save_malicious_domains(self, domains):
        """Save malicious domains to file"""
        try:
            with open(self.domains_file, 'w', encoding='utf-8') as f:
                json.dump(list(domains), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving malicious domains: {e}")
    
    def load_whitelisted_domains(self):
        """Load whitelisted domains from file"""
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
        except:
            pass
        return set()
    
    def save_whitelisted_domains(self, domains):
        """Save whitelisted domains to file"""
        try:
            with open(self.whitelist_file, 'w', encoding='utf-8') as f:
                json.dump(list(domains), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving whitelisted domains: {e}")
    
    def load_cache(self):
        """Load domain cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime objects
                    for domain, cache_data in data.items():
                        cache_data['timestamp'] = datetime.fromisoformat(cache_data['timestamp'])
                    return data
        except:
            pass
        return {}
    
    def save_cache(self, cache_data):
        """Save domain cache to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_data = {}
            for domain, cache_info in cache_data.items():
                serializable_data[domain] = {
                    'result': cache_info['result'],
                    'timestamp': cache_info['timestamp'].isoformat()
                }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

# Global storage instance
storage = PersistentStorage()