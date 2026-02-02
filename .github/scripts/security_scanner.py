#!/usr/bin/env python3
"""
Security Scanner Script
Handles dependency scanning and vulnerability checks
"""

import subprocess
import json
import os
import sys
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        self.results = {
            'python': {'pip_audit': None, 'safety': None},
            'nodejs': {'npm_audit': None},
            'docker': {'base_images': []}
        }
    
    def run_command(self, cmd, cwd=None, capture_output=True):
        """Run shell command and return result"""
        try:
            result = subprocess.run(cmd, shell=True, cwd=cwd, 
                                  capture_output=capture_output, text=True)
            return result
        except Exception as e:
            print(f"Error running command '{cmd}': {e}")
            return None
    
    def scan_python_dependencies(self, backend_path):
        """Scan Python dependencies for vulnerabilities"""
        print("🔍 Scanning Python dependencies...")
        
        # Install dependencies
        print("📦 Installing Python dependencies...")
        self.run_command("pip install --upgrade pip", cwd=backend_path)
        self.run_command("pip install -r requirements.txt", cwd=backend_path)
        self.run_command("pip install -r requirements-test.txt", cwd=backend_path)
        self.run_command("pip install -r requirements-dev.txt", cwd=backend_path)
        
        # Run pip-audit
        print("🔍 Running pip-audit...")
        result = self.run_command(
            "pip-audit --format=json --output=pip-audit-results.json --progress-spinner=off || true",
            cwd=backend_path
        )
        
        # Run safety
        print("🔍 Running Safety scan...")
        self.run_command(
            "safety check --json --output=safety-results.json || true",
            cwd=backend_path
        )
        
        # Try to fix vulnerabilities
        print("🔧 Attempting to fix vulnerabilities...")
        audit_file = Path(backend_path) / "pip-audit-results.json"
        if audit_file.exists():
            try:
                with open(audit_file) as f:
                    audit_data = json.load(f)
                
                for vuln in audit_data.get('vulnerabilities', []):
                    if vuln.get('fix_versions'):
                        package = vuln['name']
                        fix_version = vuln['fix_versions'][0]
                        print(f"🔄 Updating {package} to {fix_version}")
                        self.run_command(f"pip install --upgrade {package}=={fix_version} || true")
            except Exception as e:
                print(f"⚠️ Error processing pip-audit results: {e}")
        
        print("✅ Python dependency scan completed")
    
    def scan_nodejs_dependencies(self, frontend_path):
        """Scan Node.js dependencies for vulnerabilities"""
        print("🔍 Scanning Node.js dependencies...")
        
        # Install dependencies
        print("📦 Installing Node.js dependencies...")
        self.run_command("npm install", cwd=frontend_path)
        
        # Run npm audit
        print("🔍 Running npm audit...")
        self.run_command(
            "npm audit --audit-level=high --json > npm-audit-results.json || true",
            cwd=frontend_path
        )
        
        # Try to fix vulnerabilities
        print("🔧 Attempting to fix vulnerabilities...")
        self.run_command("npm audit fix --audit-level=high || true", cwd=frontend_path)
        
        print("✅ Node.js dependency scan completed")
    
    def scan_docker_images(self):
        """Scan Docker base images for vulnerabilities"""
        print("🔍 Scanning Docker base images...")
        
        images = [
            ("python:3.11.7-slim", "python-base-scan.json"),
            ("node:18.19.0-alpine", "node-base-scan.json"),
            ("mysql:8.0.35", "mysql-base-scan.json")
        ]
        
        for image, output_file in images:
            print(f"🐳 Scanning {image}...")
            self.run_command(
                f"trivy image --severity HIGH,CRITICAL --format json --output {output_file} {image} || true"
            )
        
        print("✅ Docker base image scan completed")
    
    def scan_built_images(self, username, version):
        """Scan built Docker images"""
        print("🔍 Scanning built Docker images...")
        
        images = [
            (f"{username}/phishing-detector-backend:latest", "backend-built-scan.json"),
            (f"{username}/phishing-detector-frontend:latest", "frontend-built-scan.json"),
            (f"{username}/phishing-detector-nginx:latest", "nginx-built-scan.json")
        ]
        
        for image, output_file in images:
            print(f"🐳 Scanning {image}...")
            self.run_command(
                f"trivy image --severity HIGH,CRITICAL --format json --output {output_file} {image} || true"
            )
            # Also run text output for immediate feedback
            self.run_command(
                f"trivy image --severity HIGH,CRITICAL {image} || true"
            )
        
        print("✅ Built images scan completed")

def main():
    scanner = SecurityScanner()
    
    # Get paths
    backend_path = "phishing_detector/backend"
    frontend_path = "phishing_detector/frontend"
    
    # Run scans based on arguments
    if len(sys.argv) > 1:
        scan_type = sys.argv[1]
        
        if scan_type == "dependencies":
            scanner.scan_python_dependencies(backend_path)
            scanner.scan_nodejs_dependencies(frontend_path)
        elif scan_type == "docker-base":
            scanner.scan_docker_images()
        elif scan_type == "docker-built":
            username = sys.argv[2] if len(sys.argv) > 2 else "tamarhalali"
            version = sys.argv[3] if len(sys.argv) > 3 else "latest"
            scanner.scan_built_images(username, version)
        else:
            print("Usage: python security_scanner.py [dependencies|docker-base|docker-built] [username] [version]")
    else:
        # Run all scans
        scanner.scan_python_dependencies(backend_path)
        scanner.scan_nodejs_dependencies(frontend_path)
        scanner.scan_docker_images()

if __name__ == "__main__":
    main()