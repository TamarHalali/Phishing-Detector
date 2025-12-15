#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_virustotal():
    api_key = os.getenv('VIRUSTOTAL_API_KEY')
    if not api_key:
        print("❌ VirusTotal: No API key")
        return False
    
    url = "https://www.virustotal.com/vtapi/v2/domain/report"
    params = {'apikey': api_key, 'domain': 'google.com'}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            print("✅ VirusTotal: Connected")
            return True
        else:
            print(f"❌ VirusTotal: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VirusTotal: {e}")
        return False

def test_openai():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI: No API key")
        return False
    
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ OpenAI: Connected")
            return True
        else:
            print(f"❌ OpenAI: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAI: {e}")
        return False

def test_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Gemini: No API key")
        return False
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ Gemini: Connected")
            return True
        else:
            print(f"❌ Gemini: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gemini: {e}")
        return False

if __name__ == '__main__':
    print("Testing API Connectivity...")
    print("-" * 30)
    
    results = [
        test_virustotal(),
        test_openai(), 
        test_gemini()
    ]
    
    print("-" * 30)
    if all(results):
        print("🎉 All APIs connected successfully!")
    else:
        print("⚠️  Some APIs failed to connect")