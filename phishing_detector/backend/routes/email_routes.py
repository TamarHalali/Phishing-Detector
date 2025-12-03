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
        
        # Save to MySQL database
        email_record = EmailAnalysis(
            sender=parsed_email['sender'],
            subject=parsed_email['subject'],
            body=parsed_email['body'],
            urls=json.dumps(parsed_email['urls']),
            attachments=json.dumps(parsed_email['attachments']),
            ai_score=ai_result['score'],
            ai_summary=ai_result['summary'],
            ai_indicators=json.dumps(ai_result.get('indicators', [])),
            ai_detections=json.dumps(ai_result.get('detections', [])),
            url_analysis=json.dumps(ai_result.get('url_analysis', []))
        )
        
        db.session.add(email_record)
        db.session.commit()
        
        return jsonify({
            'id': email_record.id,
            'parsed_email': parsed_email,
            'ai_analysis': ai_result
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
            'ai_analysis': ai_result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/history', methods=['GET'])
def history():
    emails = EmailAnalysis.query.order_by(EmailAnalysis.timestamp.desc()).all()
    return jsonify([email.to_dict() for email in emails])

@email_bp.route('/email/<int:email_id>', methods=['GET'])
def get_email(email_id):
    email = EmailAnalysis.query.get_or_404(email_id)
    return jsonify(email.to_dict())