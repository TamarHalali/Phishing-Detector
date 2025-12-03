from flask import Flask
from flask_cors import CORS
from database import db
import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///phishing.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from routes.email_routes import email_bp
from routes.domain_routes import domain_bp
from routes.cache_routes import cache_bp
app.register_blueprint(email_bp)
app.register_blueprint(domain_bp)
app.register_blueprint(cache_bp)

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)