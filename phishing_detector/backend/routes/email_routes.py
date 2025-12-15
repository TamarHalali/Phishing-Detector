from flask import Blueprint, request, jsonify
from services.email_parser import EmailParser
from services.ai_analyzer import AIAnalyzer
from database import db
from models.database import EmailAnalysis
import json

email_bp = Blueprint('email', __name__)

@email_bp.route('/upload_email', methods=['POST'])
def upload_email():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        content = file.read().decode('utf-8')
        parsed_email = EmailParser.parse_eml(content)
        
        # Analyze with LLM
        ai_result = AIAnalyzer.analyze_with_ai(parsed_email)
        
        # Extract domain from sender
        sender_domain = ''
        if '@' in parsed_email['sender']:
            sender_domain = parsed_email['sender'].split('@')[1].strip('>')
        
        # Determine risk level
        score = ai_result['score']
        if score >= 80:
            risk_level = 'Critical'
        elif score >= 60:
            risk_level = 'High'
        elif score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Save only analysis results to database
        email_record = EmailAnalysis(
            sender=parsed_email['sender'],
            subject=parsed_email['subject'][:500] if parsed_email['subject'] else '',
            sender_domain=sender_domain,
            ai_score=score,
            risk_level=risk_level,
            ai_summary=ai_result['summary'],
            threat_indicators=json.dumps(ai_result.get('indicators', [])[:5])  # Only top 5 indicators
        )
        
        db.session.add(email_record)
        db.session.commit()
        
        return jsonify({
            'id': email_record.id,
            'analysis_summary': {
                'score': score,
                'risk_level': risk_level,
                'summary': ai_result['summary'],
                'sender_domain': sender_domain
            },
            'parsed_email': parsed_email,
            'ai_analysis': ai_result,
            'container_info': request.container_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No content provided'}), 400
    
    try:
        parsed_email = EmailParser.parse_eml(data['content'])
        ai_result = AIAnalyzer.analyze_with_ai(parsed_email)
        
        return jsonify({
            'parsed_email': parsed_email,
            'ai_analysis': ai_result,
            'container_info': request.container_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/history', methods=['GET'])
def history():
    emails = EmailAnalysis.query.order_by(EmailAnalysis.timestamp.desc()).all()
    return jsonify({
        'emails': [email.to_dict() for email in emails],
        'container_info': request.container_info
    })

# Email detail endpoint removed - history records are not clickable