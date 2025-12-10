from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
import os
import socket
import uuid
import time
import pymysql
from datetime import datetime

def wait_for_mysql():
    max_retries = 30
    for i in range(max_retries):
        try:
            connection = pymysql.connect(
                host='mysql',
                user='phishing_user',
                password='phishing_pass',
                database='phishing_db'
            )
            connection.close()
            print(f"MySQL connected after {i+1} attempts")
            return True
        except:
            print(f"Waiting for MySQL... ({i+1}/{max_retries})")
            time.sleep(2)
    return False

if not wait_for_mysql():
    print("FATAL: Cannot connect to MySQL")
    exit(1)

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phishing_user:phishing_pass@mysql:3306/phishing_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from routes.email_routes import email_bp
from routes.domain_routes import domain_bp
from routes.cache_routes import cache_bp
app.register_blueprint(email_bp)
app.register_blueprint(domain_bp)
app.register_blueprint(cache_bp)

# Container identification
CONTAINER_ID = str(uuid.uuid4())[:8]
HOSTNAME = socket.gethostname()

# Simple in-memory queue counter
request_counter = 0

@app.before_request
def before_request():
    global request_counter
    request_counter += 1
    
    # Log to terminal
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Container {CONTAINER_ID} | Host: {HOSTNAME} | Request #{request_counter} | {request.method} {request.path} | Client: {client_ip}")
    
    request.container_info = {
        'container_id': CONTAINER_ID,
        'hostname': HOSTNAME,
        'request_number': request_counter,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'container_id': CONTAINER_ID,
        'hostname': HOSTNAME,
        'requests_handled': request_counter
    }

@app.route('/container-info')
def container_info():
    return {
        'container_id': CONTAINER_ID,
        'hostname': HOSTNAME,
        'requests_handled': request_counter,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Container {CONTAINER_ID} started on {HOSTNAME}")
    app.run(debug=False, host='0.0.0.0', port=5000)