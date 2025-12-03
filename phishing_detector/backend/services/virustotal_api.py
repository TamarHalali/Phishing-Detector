import requests
import time
import os
from urllib.parse import urlparse

class VirusTotalAPI:
    def __init__(self):
        self.api_key = os.getenv('VIRUSTOTAL_API_KEY', 'demo_key')
        self.base_url = 'https://www.virustotal.com/vtapi/v2'
    
    def check_domain(self, domain):
        """Check domain reputation - first local cache, then VirusTotal API"""
        from services.local_domain_cache import domain_cache
        
        # First check local cache
        cached_result = domain_cache.get_cached_result(domain)
        if cached_result:
            print(f"Using cached result for domain: {domain}")
            return cached_result
        
        # If not in cache, check with VirusTotal or mock
        if self.api_key == 'demo_key':
            result = self._mock_domain_check(domain)
        else:
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
            except:
                result = {'risk_score': 0, 'is_malicious': False, 'detections': []}
        
        # Cache the result
        domain_cache.cache_result(domain, result)
        print(f"Cached new result for domain: {domain}")
        return result
    
    def check_url(self, url):
        """Check URL reputation via VirusTotal API"""
        if self.api_key == 'demo_key':
            return self._mock_url_check(url)
        
        # Implementation for real VirusTotal URL check
        return {'risk_score': 0, 'is_malicious': False}
    
    def _mock_domain_check(self, domain):
        """Mock domain check for demo purposes"""
        suspicious_domains = {
            'tempmail.com': {'score': 80, 'detections': [('Kaspersky', 'Spam'), ('BitDefender', 'Phishing')]},
            'guerrillamail.com': {'score': 85, 'detections': [('Norton', 'Malicious'), ('McAfee', 'Spam')]},
            '10minutemail.com': {'score': 90, 'detections': [('Avast', 'Phishing'), ('ESET', 'Suspicious')]},
            'mailinator.com': {'score': 75, 'detections': [('Symantec', 'Spam')]},
            'fake-bank.com': {'score': 95, 'detections': [('Kaspersky', 'Phishing'), ('BitDefender', 'Malicious'), ('Norton', 'Fraud')]},
            'bricklestrks.com': {'score': 92, 'detections': [('Kaspersky', 'Phishing'), ('McAfee', 'Malicious'), ('Avast', 'Fraud')]},
            'flagotechs.com': {'score': 88, 'detections': [('Norton', 'Spam'), ('ESET', 'Phishing')]}
        }
        
        domain_info = suspicious_domains.get(domain.lower(), {'score': 0, 'detections': []})
        return {
            'risk_score': domain_info['score'],
            'is_malicious': domain_info['score'] > 70,
            'detections': domain_info['detections']
        }
    
    def _mock_url_check(self, url):
        """Mock URL check for demo purposes"""
        suspicious_patterns = ['bit.ly', 'tinyurl.com', 'fake-', 'phish']
        risk_score = 0
        
        for pattern in suspicious_patterns:
            if pattern in url.lower():
                risk_score += 25
        
        return {
            'risk_score': min(risk_score, 100),
            'is_malicious': risk_score > 50
        }
    
    def _parse_domain_response(self, data):
        """Parse VirusTotal domain response"""
        if data.get('response_code') == 1:
            detected_urls = data.get('detected_urls', [])
            risk_score = min(len(detected_urls) * 10, 100)
            return {
                'risk_score': risk_score,
                'is_malicious': risk_score > 50
            }
        return {'risk_score': 0, 'is_malicious': False}