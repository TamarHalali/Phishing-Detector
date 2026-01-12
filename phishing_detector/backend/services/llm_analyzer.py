import requests
import json
import os

class LLMAnalyzer:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    def analyze_email_with_llm(self, email_data):
        """Analyze email using LLM (Gemini)"""
        return self._analyze_with_gemini(email_data)
    
    def _analyze_with_gemini(self, email_data):
        """Analyze with Google Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
        
        prompt = f"""
        Analyze this email for phishing indicators and provide a risk score (0-100) and summary:
        
        From: {email_data['sender']}
        Subject: {email_data['subject']}
        Body: {email_data['body'][:1000]}
        URLs: {', '.join(email_data['urls'])}
        
        Respond in JSON format:
        {{"score": <number>, "summary": "<explanation>", "indicators": ["<list of specific indicators found>"]}}
        """
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text.strip('```json\n').strip('```'))
            else:
                return self._mock_llm_analysis(email_data)
        except:
            return self._mock_llm_analysis(email_data)
    

    
    def _mock_llm_analysis(self, email_data):
        """Mock LLM analysis for demo"""
        score = 0
        indicators = []
        
        # Check for urgent language
        urgent_words = ['urgent', 'immediate', 'expires', 'act now', 'limited time', 'אחרון', 'דחוף', 'מיידי']
        for word in urgent_words:
            if word.lower() in email_data['body'].lower() or word.lower() in email_data['subject'].lower():
                score += 25
                indicators.append(f"Urgent language: '{word}'")
                break
        
        # Check for suspicious URLs
        suspicious_domains = ['bit.ly', 'tinyurl', 'bricklestrks', 'flagotechs']
        for url in email_data['urls']:
            for domain in suspicious_domains:
                if domain in url.lower():
                    score += 30
                    indicators.append(f"Suspicious URL: {url}")
                    break
        
        # Check for personal info requests
        personal_keywords = ['password', 'credit card', 'ssn', 'פרטים', 'אישור', 'סיסמה']
        for keyword in personal_keywords:
            if keyword.lower() in email_data['body'].lower():
                score += 20
                indicators.append(f"Requests personal information: '{keyword}'")
                break
        
        # Check sender domain
        if '@' in email_data['sender']:
            domain = email_data['sender'].split('@')[1].lower()
            suspicious_sender_domains = ['tempmail', 'guerrilla', '10minute', 'mailinator']
            for sus_domain in suspicious_sender_domains:
                if sus_domain in domain:
                    score += 25
                    indicators.append(f"Suspicious sender domain: {domain}")
                    break
        
        summary = f"Detected {len(indicators)} phishing indicators" if indicators else "No significant phishing indicators detected"
        
        return {
            "score": min(score, 100),
            "summary": summary,
            "indicators": indicators
        }