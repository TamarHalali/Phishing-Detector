import email
import re
import base64
from email.header import decode_header
from urllib.parse import urlparse

class EmailParser:
    @staticmethod
    def parse_eml(file_content):
        msg = email.message_from_string(file_content)
        
        sender = EmailParser.decode_header_field(msg.get('From', ''))
        subject = EmailParser.decode_header_field(msg.get('Subject', ''))
        
        body = EmailParser.extract_body(msg)
        urls = EmailParser.extract_urls(body + ' ' + file_content)
        attachments = EmailParser.extract_attachments(msg)
        
        return {
            'sender': sender,
            'subject': subject,
            'body': body,
            'urls': urls,
            'attachments': attachments
        }
    
    @staticmethod
    def decode_header_field(field):
        if not field:
            return ''
        
        decoded_parts = decode_header(field)
        decoded_string = ''
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding, errors='ignore')
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string
    
    @staticmethod
    def extract_body(msg):
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        if part.get('Content-Transfer-Encoding') == 'base64':
                            try:
                                body = base64.b64decode(payload).decode('utf-8', errors='ignore')
                            except:
                                body = payload.decode('utf-8', errors='ignore')
                        else:
                            body = payload.decode('utf-8', errors='ignore')
                    break
                elif content_type == "text/html" and not body:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = EmailParser.html_to_text(payload.decode('utf-8', errors='ignore'))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        
        return body
    
    @staticmethod
    def html_to_text(html_content):
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def extract_urls(text):
        url_patterns = [
            r'https?://[^\s<>"\[\]{}|\\^`]+',
            r'href=["\']([^"\'>]+)["\']',
            r'url=["\']([^"\'>]+)["\']'
        ]
        
        urls = set()
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    urls.add(match[0])
                else:
                    urls.add(match)
        
        filtered_urls = []
        for url in urls:
            if url.startswith(('http://', 'https://')) and len(url) > 10:
                filtered_urls.append(url)
        
        return filtered_urls
    
    @staticmethod
    def extract_attachments(msg):
        attachments = []
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        'filename': filename,
                        'content_type': part.get_content_type()
                    })
        return attachments