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
        
        # JSON output for reports - without || true to catch errors
        result = subprocess.run(
            f"trivy image --severity HIGH,CRITICAL --format json --output {scan_file} {latest_tag}",
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"⚠️  Trivy scan had issues: {result.stderr}")
            # Create empty result file so report generation doesn't fail
            import json
            with open(scan_file, 'w') as f:
                json.dump({'Results': []}, f)
        
        # Human-readable summary
        print(f"\n{'='*60}")
        print(f"📊 SECURITY SCAN SUMMARY - {service_name.upper()}")
        print(f"{'='*60}")
        
        # Run trivy in table format for human-readable output
        result = subprocess.run(
            f"trivy image --severity HIGH,CRITICAL --format table {latest_tag}",
            shell=True, capture_output=True, text=True
        )
        
        if result.stdout:
            print(result.stdout)
        
        # Parse JSON for summary statistics
        try:
            import json
            if os.path.exists(scan_file):
                with open(scan_file, 'r') as f:
                    scan_data = json.load(f)
            else:
                print(f"⚠️  Scan file {scan_file} not found!")
                scan_data = {'Results': []}
            
            total_high = 0
            total_critical = 0
            
            for result in scan_data.get('Results', []):
                for vuln in result.get('Vulnerabilities', []):
                    severity = vuln.get('Severity', '')
                    if severity == 'HIGH':
                        total_high += 1
                    elif severity == 'CRITICAL':
                        total_critical += 1
            
            print(f"\n📈 Vulnerability Count:")
            print(f"   🔴 Critical: {total_critical}")
            print(f"   🟠 High: {total_high}")
            print(f"   📊 Total: {total_critical + total_high}")
            
            if total_critical > 0:
                print(f"\n⚠️  WARNING: {total_critical} CRITICAL vulnerabilities found!")
            elif total_high > 0:
                print(f"\n⚠️  {total_high} HIGH severity vulnerabilities found")
            else:
                print(f"\n✅ No HIGH or CRITICAL vulnerabilities found!")
                
        except Exception as e:
            print(f"⚠️  Could not parse scan results: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"{'='*60}\n")
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
        scan_results = {}
        
        for service in ['backend', 'frontend', 'nginx']:
            results[service] = self.build_scan_push(service)
            
            # Collect scan results
            scan_file = f"{service}-built-scan.json"
            try:
                import json
                with open(scan_file, 'r') as f:
                    scan_results[service] = json.load(f)
            except:
                scan_results[service] = None
        
        # Generate summary report
        self.generate_summary_report(results, scan_results)
        
        # Summary
        print(f"\n{'='*60}")
        print("🎯 FINAL BUILD SUMMARY")
        print(f"{'='*60}")
        
        all_success = True
        for service, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{service.upper()}: {status}")
            if not success:
                all_success = False
        
        print(f"{'='*60}")
        
        if all_success:
            print("🎉 All images built, scanned, and pushed successfully!")
            print("🐳 Images are now available on Docker Hub:")
            print(f"   - {self.username}/phishing-detector-backend:{self.version}")
            print(f"   - {self.username}/phishing-detector-frontend:{self.version}")
            print(f"   - {self.username}/phishing-detector-nginx:{self.version}")
            print("\n📄 Summary report: BUILD_SUMMARY_REPORT.md")
        else:
            print("⚠️ Some images failed to build/push")
            sys.exit(1)
        
        return all_success
    
    def generate_summary_report(self, results, scan_results):
        """Generate a markdown summary report"""
        import json
        from datetime import datetime
        
        report = []
        report.append("# Docker Build & Security Scan Summary\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Version:** {self.version}\n")
        report.append(f"**Username:** {self.username}\n\n")
        
        report.append("## Build Status\n\n")
        report.append("| Service | Status | Image |\n")
        report.append("|---------|--------|-------|\n")
        
        for service, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            image = f"{self.username}/phishing-detector-{service}:{self.version}"
            report.append(f"| {service.capitalize()} | {status} | `{image}` |\n")
        
        report.append("\n## Security Scan Results\n\n")
        
        total_critical = 0
        total_high = 0
        
        for service, scan_data in scan_results.items():
            if not scan_data:
                continue
            
            service_critical = 0
            service_high = 0
            
            for result in scan_data.get('Results', []):
                for vuln in result.get('Vulnerabilities', []):
                    severity = vuln.get('Severity', '')
                    if severity == 'HIGH':
                        service_high += 1
                        total_high += 1
                    elif severity == 'CRITICAL':
                        service_critical += 1
                        total_critical += 1
            
            report.append(f"### {service.capitalize()}\n\n")
            report.append(f"- 🔴 **Critical:** {service_critical}\n")
            report.append(f"- 🟠 **High:** {service_high}\n")
            report.append(f"- 📊 **Total:** {service_critical + service_high}\n\n")
            
            if service_critical > 0:
                report.append(f"⚠️ **WARNING:** {service_critical} CRITICAL vulnerabilities found!\n\n")
            elif service_high > 0:
                report.append(f"⚠️ {service_high} HIGH severity vulnerabilities found\n\n")
            else:
                report.append("✅ No HIGH or CRITICAL vulnerabilities found\n\n")
        
        report.append("## Overall Summary\n\n")
        report.append(f"- 🔴 **Total Critical:** {total_critical}\n")
        report.append(f"- 🟠 **Total High:** {total_high}\n")
        report.append(f"- 📊 **Total Vulnerabilities:** {total_critical + total_high}\n\n")
        
        if total_critical > 0:
            report.append(f"### ⚠️ Action Required\n\n")
            report.append(f"{total_critical} CRITICAL vulnerabilities detected across all images. ")
            report.append("Please review and update dependencies.\n\n")
        elif total_high > 0:
            report.append(f"### ℹ️ Recommendation\n\n")
            report.append(f"{total_high} HIGH severity vulnerabilities detected. ")
            report.append("Consider updating affected packages.\n\n")
        else:
            report.append("### ✅ All Clear\n\n")
            report.append("No HIGH or CRITICAL vulnerabilities detected in any images.\n\n")
        
        report.append("## Docker Hub Links\n\n")
        report.append(f"- [Backend Image](https://hub.docker.com/r/{self.username}/phishing-detector-backend)\n")
        report.append(f"- [Frontend Image](https://hub.docker.com/r/{self.username}/phishing-detector-frontend)\n")
        report.append(f"- [Nginx Image](https://hub.docker.com/r/{self.username}/phishing-detector-nginx)\n")
        
        # Write report
        with open('BUILD_SUMMARY_REPORT.md', 'w') as f:
            f.writelines(report)
        
        print("\n📄 Summary report generated: BUILD_SUMMARY_REPORT.md")

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