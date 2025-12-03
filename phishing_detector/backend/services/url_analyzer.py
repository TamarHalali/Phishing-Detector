import requests
import os
import base64
import hashlib
from urllib.parse import urlparse

class URLAnalyzer:
    def __init__(self):
        self.vt_api_key = os.getenv('VIRUSTOTAL_API_KEY', 'demo_key')
        self.shortener_domains = [
            'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 
            'short.link', 'rebrand.ly', 'cutt.ly', 'is.gd'
        ]
    
    def analyze_urls(self, urls):
        """Analyze all URLs in the email"""
        results = []
        
        for url in urls:
            try:
                # Expand shortened URLs
                expanded_url = self.expand_shortened_url(url)
                
                # Check with VirusTotal
                vt_result = self.check_url_with_virustotal(expanded_url)
                
                results.append({
                    'original_url': url,
                    'expanded_url': expanded_url,
                    'is_shortened': url != expanded_url,
                    'risk_score': vt_result['risk_score'],
                    'detections': vt_result['detections'],
                    'is_malicious': vt_result['is_malicious']
                })
            except:
                results.append({
                    'original_url': url,
                    'expanded_url': url,
                    'is_shortened': False,
                    'risk_score': 0,
                    'detections': [],
                    'is_malicious': False
                })
        
        return results
    
    def expand_shortened_url(self, url):
        """Expand shortened URLs to see final destination"""
        if not any(domain in url.lower() for domain in self.shortener_domains):
            return url
        
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.url
        except:
            return url
    
    def check_url_with_virustotal(self, url):
        """Check URL with VirusTotal API - first local cache, then API"""
        from services.local_domain_cache import domain_cache
        
        # Check cache first
        cached_result = domain_cache.get_cached_result(url)
        if cached_result:
            print(f"Using cached result for URL: {url}")
            return cached_result
        
        # If not cached, check with VirusTotal or mock
        if self.vt_api_key == 'demo_key':
            result = self._mock_url_check(url)
        else:
            # Encode URL for VirusTotal
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            headers = {
                "x-apikey": self.vt_api_key
            }
            
            try:
                # Check if URL already scanned
                response = requests.get(
                    f"https://www.virustotal.com/api/v3/urls/{url_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = self._parse_vt_response(data)
                else:
                    # Submit URL for scanning
                    scan_response = requests.post(
                        "https://www.virustotal.com/api/v3/urls",
                        headers=headers,
                        data={"url": url},
                        timeout=10
                    )
                    result = {'risk_score': 0, 'detections': [], 'is_malicious': False}
            except:
                result = self._mock_url_check(url)
        
        # Cache the result
        domain_cache.cache_result(url, result)
        print(f"Cached new result for URL: {url}")
        return result
    
    def _parse_vt_response(self, data):
        """Parse VirusTotal response"""
        stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
        malicious = stats.get('malicious', 0)
        suspicious = stats.get('suspicious', 0)
        
        # Get detection details
        results = data.get('data', {}).get('attributes', {}).get('last_analysis_results', {})
        detections = []
        
        for engine, result in results.items():
            if result.get('category') in ['malicious', 'suspicious']:
                detections.append((engine, result.get('result', 'Malicious')))
        
        risk_score = min((malicious + suspicious) * 10, 100)
        
        return {
            'risk_score': risk_score,
            'detections': detections,
            'is_malicious': malicious > 0 or suspicious > 2
        }
    
    def _mock_url_check(self, url):
        """Mock URL check for demo"""
        suspicious_patterns = {
            'bit.ly': {'score': 60, 'detections': [('Kaspersky', 'Suspicious'), ('McAfee', 'Phishing')]},
            'tinyurl.com': {'score': 55, 'detections': [('Norton', 'Suspicious')]},
            'bricklestrks.com': {'score': 95, 'detections': [('Kaspersky', 'Phishing'), ('BitDefender', 'Malicious'), ('Avast', 'Fraud')]},
            'flagotechs.com': {'score': 88, 'detections': [('Norton', 'Spam'), ('ESET', 'Phishing')]},
            'fake-bank': {'score': 98, 'detections': [('Kaspersky', 'Phishing'), ('McAfee', 'Fraud'), ('Norton', 'Malicious')]},
            'phishing': {'score': 92, 'detections': [('BitDefender', 'Phishing'), ('Avast', 'Malicious')]},
            'malware': {'score': 96, 'detections': [('Kaspersky', 'Malware'), ('Norton', 'Trojan')]}
        }
        
        for pattern, info in suspicious_patterns.items():
            if pattern in url.lower():
                return {
                    'risk_score': info['score'],
                    'detections': info['detections'],
                    'is_malicious': info['score'] > 70
                }
        
        return {
            'risk_score': 0,
            'detections': [],
            'is_malicious': False
        }