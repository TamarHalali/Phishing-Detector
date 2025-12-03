from services.llm_analyzer import LLMAnalyzer
from services.virustotal_api import VirusTotalAPI
from services.url_analyzer import URLAnalyzer

class AIAnalyzer:
    @staticmethod
    def analyze_with_ai(email_data):
        # Use LLM for primary analysis
        llm_analyzer = LLMAnalyzer()
        llm_result = llm_analyzer.analyze_email_with_llm(email_data)
        
        # Get VirusTotal data for sender domain
        vt_detections = []
        if '@' in email_data['sender']:
            domain = email_data['sender'].split('@')[1].strip('>')
            
            # Import here to avoid circular import
            from routes.domain_routes import is_domain_whitelisted, add_malicious_domain
            
            # Skip analysis if domain is whitelisted
            if not is_domain_whitelisted(domain):
                vt_api = VirusTotalAPI()
                vt_result = vt_api.check_domain(domain)
                if vt_result.get('detections'):
                    vt_detections = vt_result['detections']
                    # Add to malicious domains if detected
                    if vt_result.get('is_malicious'):
                        add_malicious_domain(domain)
        
        # Analyze URLs with expansion and VirusTotal check
        url_analyzer = URLAnalyzer()
        url_results = url_analyzer.analyze_urls(email_data['urls'])
        
        # Add URL risk to overall score
        url_risk = 0
        malicious_urls = []
        for url_result in url_results:
            if url_result['is_malicious']:
                url_risk += 30
                malicious_urls.append(url_result)
                vt_detections.extend(url_result['detections'])
                # Add malicious URL domain to tracking
                from urllib.parse import urlparse
                from routes.domain_routes import is_domain_whitelisted, add_malicious_domain
                try:
                    parsed_url = urlparse(url_result['expanded_url'])
                    if parsed_url.netloc and not is_domain_whitelisted(parsed_url.netloc):
                        add_malicious_domain(parsed_url.netloc)
                except:
                    pass
        
        final_score = min(llm_result['score'] + url_risk, 100)
        
        # Add URL indicators to summary
        url_indicators = []
        for url_result in url_results:
            if url_result['is_shortened']:
                url_indicators.append(f"Shortened URL detected: {url_result['original_url']} -> {url_result['expanded_url']}")
            if url_result['is_malicious']:
                url_indicators.append(f"Malicious URL detected: {url_result['expanded_url']}")
        
        all_indicators = llm_result.get('indicators', []) + url_indicators
        
        return {
            "score": final_score,
            "summary": llm_result['summary'],
            "indicators": all_indicators,
            "detections": vt_detections,
            "url_analysis": url_results
        }
    
    @staticmethod
    def check_sender_trust(sender):
        # Extract domain from sender email
        if '@' in sender:
            domain = sender.split('@')[1].strip('>')
            vt_api = VirusTotalAPI()
            result = vt_api.check_domain(domain)
            return result['risk_score'], result.get('detections', [])
        return 20, []
    
    @staticmethod
    def check_suspicious_domains(sender):
        suspicious_domains = ['tempmail', 'guerrillamail', '10minutemail']
        for domain in suspicious_domains:
            if domain in sender.lower():
                return 25
        return 0
    
    @staticmethod
    def check_urgent_language(body):
        urgent_words = ['urgent', 'immediate', 'expires today', 'act now', 'limited time']
        for word in urgent_words:
            if word.lower() in body.lower():
                return 15
        return 0
    
    @staticmethod
    def check_personal_info_requests(body):
        personal_keywords = ['password', 'ssn', 'social security', 'credit card', 'bank account']
        for keyword in personal_keywords:
            if keyword.lower() in body.lower():
                return 30
        return 0
    
    @staticmethod
    def check_urls(urls):
        vt_api = VirusTotalAPI()
        max_risk = 0
        
        for url in urls:
            result = vt_api.check_url(url)
            max_risk = max(max_risk, result['risk_score'])
        
        return min(max_risk, 30)
    
    @staticmethod
    def check_profit_promises(body):
        profit_keywords = ['make money fast', 'guaranteed profit', 'easy money', 'get rich']
        for keyword in profit_keywords:
            if keyword.lower() in body.lower():
                return 25
        return 0