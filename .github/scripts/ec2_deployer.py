#!/usr/bin/env python3
"""
EC2 Deployment Script
Handles deployment to EC2 instance via SSH
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class EC2Deployer:
    def __init__(self, host, ssh_key, username="tamarhalali"):
        self.host = host
        self.ssh_key = ssh_key
        self.username = username
        self.ssh_options = [
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null", 
            "-o", "LogLevel=ERROR"
        ]
    
    def setup_ssh(self):
        """Setup SSH key and known hosts"""
        print("🔑 Setting up SSH for deployment...")
        
        # Create .ssh directory
        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(exist_ok=True)
        
        # Save SSH key
        key_file = ssh_dir / "deploy_key"
        with open(key_file, 'w') as f:
            f.write(self.ssh_key)
        key_file.chmod(0o600)
        
        # Verify key format
        result = subprocess.run(['ssh-keygen', '-l', '-f', str(key_file)], 
                              capture_output=True)
        if result.returncode != 0:
            print("❌ Invalid SSH private key format")
            sys.exit(1)
        
        # Add host to known_hosts
        subprocess.run(['ssh-keyscan', '-H', self.host], 
                      stdout=open(ssh_dir / "known_hosts", 'a'),
                      stderr=subprocess.DEVNULL)
        
        print("✅ SSH setup completed")
        return str(key_file)
    
    def run_ssh_command(self, command, key_file):
        """Run command on EC2 via SSH"""
        ssh_cmd = [
            'ssh', '-i', key_file,
            *self.ssh_options,
            f'ec2-user@{self.host}',
            command
        ]
        
        try:
            result = subprocess.run(ssh_cmd, check=True, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ SSH command failed: {e}")
            return False
    
    def create_docker_compose(self, key_file):
        """Create docker-compose.prod.yml on EC2"""
        print("📝 Creating docker-compose.prod.yml on EC2...")
        
        compose_content = '''version: '3.8'

services:
  mysql:
    image: mysql:8.0.35
    container_name: phishing-mysql
    environment:
      MYSQL_ROOT_PASSWORD: "${MYSQL_ROOT_PASSWORD}"
      MYSQL_DATABASE: phishing_db
      MYSQL_USER: phishing_user
      MYSQL_PASSWORD: "${MYSQL_PASSWORD}"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  backend1:
    image: tamarhalali/phishing-detector-backend:latest
    container_name: phishing-backend1
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+pymysql://phishing_user:${MYSQL_PASSWORD}@mysql:3306/phishing_db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - VIRUSTOTAL_API_KEY=${VIRUSTOTAL_API_KEY}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped

  backend2:
    image: tamarhalali/phishing-detector-backend:latest
    container_name: phishing-backend2
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+pymysql://phishing_user:${MYSQL_PASSWORD}@mysql:3306/phishing_db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - VIRUSTOTAL_API_KEY=${VIRUSTOTAL_API_KEY}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped

  backend3:
    image: tamarhalali/phishing-detector-backend:latest
    container_name: phishing-backend3
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+pymysql://phishing_user:${MYSQL_PASSWORD}@mysql:3306/phishing_db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - VIRUSTOTAL_API_KEY=${VIRUSTOTAL_API_KEY}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    image: tamarhalali/phishing-detector-frontend:latest
    container_name: phishing-frontend
    depends_on:
      backend1:
        condition: service_started
    restart: unless-stopped

  nginx:
    image: tamarhalali/phishing-detector-nginx:latest
    container_name: phishing-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend1
      - backend2
      - backend3
    restart: unless-stopped

volumes:
  mysql_data:'''
        
        # Create the file on EC2
        command = f'cat > /home/ec2-user/docker-compose.prod.yml << "EOF"\n{compose_content}\nEOF'
        return self.run_ssh_command(command, key_file)
    
    def cleanup_containers(self, key_file):
        """Emergency cleanup of containers"""
        print("🧹 Emergency cleanup...")
        
        commands = [
            "docker stop $(docker ps -aq 2>/dev/null) 2>/dev/null || true",
            "docker rm -f $(docker ps -aq 2>/dev/null) 2>/dev/null || true", 
            "docker system prune -f 2>/dev/null || true"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, key_file)
    
    def pull_images(self, key_file):
        """Pull latest Docker images"""
        print("🐳 Pulling latest images...")
        
        images = [
            "mysql:8.0.35",
            f"{self.username}/phishing-detector-backend:latest",
            f"{self.username}/phishing-detector-frontend:latest", 
            f"{self.username}/phishing-detector-nginx:latest"
        ]
        
        for image in images:
            print(f"📥 Pulling {image}...")
            self.run_ssh_command(f"docker pull {image}", key_file)
    
    def start_services(self, key_file):
        """Start Docker Compose services"""
        print("🚀 Starting containers...")
        
        return self.run_ssh_command(
            "docker-compose -f /home/ec2-user/docker-compose.prod.yml up -d",
            key_file
        )
    
    def check_status(self, key_file):
        """Check service status"""
        print("🔍 Checking status...")
        
        self.run_ssh_command(
            "docker-compose -f /home/ec2-user/docker-compose.prod.yml ps",
            key_file
        )
    
    def verify_deployment(self):
        """Verify deployment is working"""
        print("⏳ Waiting 30 seconds for deployment to complete...")
        time.sleep(30)
        
        print("🔍 Checking if application is responding...")
        
        # Check frontend
        result = subprocess.run([
            'curl', '-f', '-s', '--max-time', '10', 
            f'http://{self.host}/'
        ], capture_output=True)
        
        if result.returncode == 0:
            print("✅ Frontend is responding!")
        else:
            print("⚠️ Frontend check failed - deployment may still be in progress")
        
        # Check API
        result = subprocess.run([
            'curl', '-f', '-s', '--max-time', '10',
            f'http://{self.host}/api/health'
        ], capture_output=True)
        
        if result.returncode == 0:
            print("✅ API is responding!")
        else:
            print("⚠️ API check failed - deployment may still be in progress")
    
    def deploy(self):
        """Full deployment process"""
        print("🚀 Starting deployment on EC2...")
        
        # Setup SSH
        key_file = self.setup_ssh()
        
        # Create docker-compose file
        if not self.create_docker_compose(key_file):
            print("❌ Failed to create docker-compose file")
            sys.exit(1)
        
        # Cleanup old containers
        self.cleanup_containers(key_file)
        
        # Pull latest images
        self.pull_images(key_file)
        
        # Start services
        if not self.start_services(key_file):
            print("❌ Failed to start services")
            sys.exit(1)
        
        # Wait for services
        print("⏳ Waiting for services...")
        time.sleep(30)
        
        # Check status
        self.check_status(key_file)
        
        print("✅ Deployment completed!")
        
        # Verify deployment
        self.verify_deployment()
        
        print("✅ Deployment verification completed")

def main():
    if len(sys.argv) < 3:
        print("Usage: python ec2_deployer.py <host> <ssh_key> [username]")
        sys.exit(1)
    
    host = sys.argv[1]
    ssh_key = sys.argv[2]
    username = sys.argv[3] if len(sys.argv) > 3 else "tamarhalali"
    
    deployer = EC2Deployer(host, ssh_key, username)
    deployer.deploy()

if __name__ == "__main__":
    main()