#!/usr/bin/env python3
"""
Docker Build and Push Script
Handles building and pushing Docker images to Docker Hub
"""

import subprocess
import sys
import os
from pathlib import Path

class DockerBuilder:
    def __init__(self, username, version):
        self.username = username
        self.version = version
        self.images = {
            'backend': {
                'path': 'phishing_detector/backend',
                'dockerfile': 'Dockerfile',
                'name': f'{username}/phishing-detector-backend'
            },
            'frontend': {
                'path': 'phishing_detector/frontend', 
                'dockerfile': 'Dockerfile',
                'name': f'{username}/phishing-detector-frontend'
            },
            'nginx': {
                'path': 'phishing_detector',
                'dockerfile': 'nginx.Dockerfile',
                'name': f'{username}/phishing-detector-nginx'
            }
        }
    
    def run_command(self, cmd, cwd=None):
        """Run shell command"""
        try:
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {e}")
            return False
    
    def build_image(self, service_name):
        """Build Docker image for a service"""
        config = self.images[service_name]
        
        print(f"🔨 Building {service_name} image...")
        
        # Build with version tag
        version_tag = f"{config['name']}:{self.version}"
        latest_tag = f"{config['name']}:latest"
        
        # Build commands
        if config['dockerfile'] == 'Dockerfile':
            build_cmd = f"docker build -t {version_tag} -t {latest_tag} ."
        else:
            build_cmd = f"docker build -f {config['dockerfile']} -t {version_tag} -t {latest_tag} ."
        
        success = self.run_command(build_cmd, cwd=config['path'])
        
        if success:
            print(f"✅ {service_name} image built successfully")
            print(f"📋 Tags created:")
            print(f"  - {version_tag}")
            print(f"  - {latest_tag}")
            return True
        else:
            print(f"❌ Failed to build {service_name} image")
            return False
    
    def scan_image(self, service_name):
        """Scan built image for vulnerabilities"""
        config = self.images[service_name]
        latest_tag = f"{config['name']}:latest"
        scan_file = f"{service_name}-built-scan.json"
        
        print(f"🔍 Scanning {service_name} image for vulnerabilities...")
        
        # JSON output for reports
        self.run_command(
            f"trivy image --severity HIGH,CRITICAL --format json --output {scan_file} {latest_tag} || true"
        )
        
        # Text output for immediate feedback
        self.run_command(
            f"trivy image --severity HIGH,CRITICAL {latest_tag} || true"
        )
        
        print(f"✅ {service_name} image security scan completed")
    
    def push_image(self, service_name):
        """Push Docker image to Docker Hub"""
        config = self.images[service_name]
        
        print(f"🚀 Pushing {service_name} image to Docker Hub...")
        
        version_tag = f"{config['name']}:{self.version}"
        latest_tag = f"{config['name']}:latest"
        
        # Push both tags
        success1 = self.run_command(f"docker push {version_tag}")
        success2 = self.run_command(f"docker push {latest_tag}")
        
        if success1 and success2:
            print(f"✅ {service_name} image pushed successfully")
            print(f"📋 Pushed tags:")
            print(f"  - {version_tag}")
            print(f"  - {latest_tag}")
            return True
        else:
            print(f"❌ Failed to push {service_name} image")
            return False
    
    def build_scan_push(self, service_name):
        """Build, scan, and push a single service"""
        print(f"\n{'='*50}")
        print(f"Processing {service_name.upper()} Image")
        print(f"{'='*50}")
        
        # Build
        if not self.build_image(service_name):
            return False
        
        # Scan
        self.scan_image(service_name)
        
        # Push
        if not self.push_image(service_name):
            return False
        
        # Set GitHub Actions output
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"{service_name}_success=true\n")
        
        return True
    
    def build_all(self):
        """Build, scan, and push all images"""
        print(f"🐳 Starting Docker build process...")
        print(f"Username: {self.username}")
        print(f"Version: {self.version}")
        
        results = {}
        
        for service in ['backend', 'frontend', 'nginx']:
            results[service] = self.build_scan_push(service)
        
        # Summary
        print(f"\n{'='*50}")
        print("BUILD SUMMARY")
        print(f"{'='*50}")
        
        all_success = True
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{service.upper()}: {status}")
            if not success:
                all_success = False
        
        if all_success:
            print("\n🎉 All images built and pushed successfully!")
        else:
            print("\n⚠️ Some images failed to build/push")
            sys.exit(1)
        
        return all_success

def main():
    if len(sys.argv) < 3:
        print("Usage: python docker_builder.py <username> <version> [service]")
        print("Services: backend, frontend, nginx, all")
        sys.exit(1)
    
    username = sys.argv[1]
    version = sys.argv[2]
    service = sys.argv[3] if len(sys.argv) > 3 else "all"
    
    builder = DockerBuilder(username, version)
    
    if service == "all":
        builder.build_all()
    elif service in builder.images:
        builder.build_scan_push(service)
    else:
        print(f"Unknown service: {service}")
        print("Available services: backend, frontend, nginx, all")
        sys.exit(1)

if __name__ == "__main__":
    main()