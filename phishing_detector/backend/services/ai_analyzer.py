from services.llm_analyzer import LLMAnalyzer
from services.virustotal_api import VirusTotalAPI
from services.url_analyzer import URLAnalyzer

class AIAnalyzer:
    # Trusted email providers that should never be flagged
    TRUSTED_DOMAINS = {
        'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'icloud.com',
        'protonmail.com', 'aol.com', 'live.com', 'msn.com', 'yandex.com',
        'mail.com', 'zoho.com', 'fastmail.com', 'tutanota.com'
    }
    
    @staticmethod
    def analyze_with_ai(email_data):
        # Use LLM for text analysis (reduced weight)
        llm_analyzer = LLMAnalyzer()
        llm_result = llm_analyzer.analyze_email_with_llm(email_data)
        
        # Reduce text analysis weight to 15-20%
        text_score = int(llm_result['score'] * 0.2)  # 20% weight for text content
        
        # Get VirusTotal data for sender domain
        vt_detections = []
        if '@' in email_data['sender']:
            domain = email_data['sender'].split('@')[1].strip('>')
            
            # Import here to avoid circular import
            from routes.domain_routes import is_domain_whitelisted, add_malicious_domain
            
            # Skip analysis if domain is trusted or whitelisted
            if domain.lower() not in AIAnalyzer.TRUSTED_DOMAINS and not is_domain_whitelisted(domain):
                vt_api = VirusTotalAPI()
                vt_result = vt_api.check_domain(domain)
                if vt_result.get('detections') and isinstance(vt_result['detections'], list):
                    # Filter out invalid detections
                    valid_detections = []
                    for detection in vt_result['detections']:
                        if isinstance(detection, (list, tuple)) and len(detection) >= 2:
                            vendor, threat = detection[0], detection[1]
                            if vendor and len(str(vendor)) > 1:  # Avoid single character vendors
                                valid_detections.append([vendor, threat])
                    vt_detections = valid_detections
                    # Add to malicious domains if detected
                    if vt_result.get('is_malicious'):
                        add_malicious_domain(domain)
        
        # Analyze URLs with expansion and VirusTotal check
        url_analyzer = URLAnalyzer()
        url_results = url_analyzer.analyze_urls(email_data['urls'])
        
        # Technical analysis gets 80% weight
        technical_score = 0
        malicious_urls = []
        
        # Domain analysis (30% weight)
        domain_risk = 0
        if vt_detections:
            # Check if sender domain is whitelisted - if so, ignore detections
            from routes.domain_routes import is_domain_whitelisted
            sender_domain = ''
            if '@' in email_data['sender']:
                sender_domain = email_data['sender'].split('@')[1].strip('>')
            
            if sender_domain and is_domain_whitelisted(sender_domain):
                domain_risk = 0  # Whitelisted domain overrides VirusTotal detections
                vt_detections = []  # Clear detections for whitelisted domains
            else:
                domain_risk = 30  # High risk if domain has detections and not whitelisted
        
        # URL analysis (40% weight) 
        url_risk = 0
        for url_result in url_results:
            if url_result['is_malicious']:
                url_risk += 40  # Higher weight for malicious URLs
                malicious_urls.append(url_result)
                # Only add valid detections
                if isinstance(url_result.get('detections'), list):
                    for detection in url_result['detections']:
                        if isinstance(detection, (list, tuple)) and len(detection) >= 2:
                            vendor, threat = detection[0], detection[1]
                            if vendor and len(str(vendor)) > 1:
                                vt_detections.append([vendor, threat])
                # Add malicious URL domain to tracking
                from urllib.parse import urlparse
                from routes.domain_routes import is_domain_whitelisted, add_malicious_domain
                try:
                    parsed_url = urlparse(url_result['expanded_url'])
                    url_domain = parsed_url.netloc.lower()
                    
                    # Check if URL domain is whitelisted
                    if is_domain_whitelisted(url_domain):
                        # Remove this URL from malicious list if whitelisted
                        url_result['is_malicious'] = False
                        url_result['risk_score'] = 0
                        url_risk -= 40  # Remove the risk points added earlier
                    elif (url_domain and url_domain not in AIAnalyzer.TRUSTED_DOMAINS):
                        add_malicious_domain(url_domain)
                except:
                    pass
        
        # Attachment risk (10% weight)
        attachment_risk = 0
        if email_data.get('attachments'):
            suspicious_extensions = ['.exe', '.scr', '.bat', '.com', '.pif', '.vbs', '.js']
            for attachment in email_data['attachments']:
                if any(attachment.lower().endswith(ext) for ext in suspicious_extensions):
                    attachment_risk += 10
        
        # Calculate final score: 20% text + 80% technical
        technical_score = min(domain_risk + url_risk + attachment_risk, 80)
        final_score = min(text_score + technical_score, 100)
        
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