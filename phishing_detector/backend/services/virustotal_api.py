import requests
import time
import os
from urllib.parse import urlparse

class VirusTotalAPI:
    def __init__(self):
        self.api_key = os.getenv('VIRUSTOTAL_API_KEY')
        if not self.api_key:
            raise ValueError("VIRUSTOTAL_API_KEY environment variable is required")
        self.base_url = 'https://www.virustotal.com/vtapi/v2'
    
    def check_domain(self, domain):
        """Check domain reputation - first local cache, then VirusTotal API"""
        from services.local_domain_cache import domain_cache
        
        # First check local cache
        cached_result = domain_cache.get_cached_result(domain)
        if cached_result:
            print(f"Using cached result for domain: {domain}")
            return cached_result
        
        # Check with VirusTotal API
        url = f"{self.base_url}/domain/report"
        params = {
            'apikey': self.api_key,
            'domain': domain
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = self._parse_domain_response(data)
            else:
                result = {'risk_score': 0, 'is_malicious': False, 'detections': []}
        except Exception as e:
            print(f"VirusTotal API error: {e}")
            result = {'risk_score': 0, 'is_malicious': False, 'detections': []}
        
        # Cache the result
        domain_cache.cache_result(domain, result)
        print(f"Cached new result for domain: {domain}")
        return result
    
    def check_url(self, url):
        """Check URL reputation via VirusTotal API"""
        api_url = f"{self.base_url}/url/report"
        params = {
            'apikey': self.api_key,
            'resource': url
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_url_response(data)
            else:
                return {'risk_score': 0, 'is_malicious': False}
        except Exception as e:
            print(f"VirusTotal URL API error: {e}")
            return {'risk_score': 0, 'is_malicious': False}
    
    def _parse_url_response(self, data):
        """Parse VirusTotal URL response"""
        if data.get('response_code') == 1:
            positives = data.get('positives', 0)
            total = data.get('total', 1)
            risk_score = int((positives / total) * 100) if total > 0 else 0
            return {
                'risk_score': risk_score,
                'is_malicious': risk_score > 30,
                'detections': positives
            }
        return {'risk_score': 0, 'is_malicious': False, 'detections': 0}
    
    def _parse_domain_response(self, data):
        """Parse VirusTotal domain response"""
        if data.get('response_code') == 1:
            detected_urls = data.get('detected_urls', [])
            risk_score = min(len(detected_urls) * 10, 100)
            detections = []
            
            # Extract detection details if available
            for detection in data.get('detected_communicating_samples', [])[:5]:
                if 'positives' in detection:
                    detections.append(f"Sample: {detection['positives']}/{detection.get('total', 0)}")
            
            return {
                'risk_score': risk_score,
                'is_malicious': risk_score > 50,
                'detections': detections
            }
        return {'risk_score': 0, 'is_malicious': False, 'detections': []}