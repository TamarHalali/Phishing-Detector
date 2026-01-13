#!/usr/bin/env python3
"""
Security Scan Report Generator
Processes scan results and generates a comprehensive security report
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

class SecurityReportGenerator:
    def __init__(self):
        self.report_lines = []
        self.vulnerabilities_by_package = defaultdict(list)
        self.fixed_packages = []
        self.unfixed_packages = []
        
    def add_section(self, title: str, level: int = 1):
        """Add a section header"""
        prefix = "#" * level
        self.report_lines.append(f"\n{prefix} {title}\n")
        
    def add_line(self, text: str = ""):
        """Add a line to the report"""
        self.report_lines.append(text)
        
    def format_json(self, data: Any, indent: int = 2) -> str:
        """Format JSON in a readable way"""
        return json.dumps(data, indent=indent, ensure_ascii=False)
        
    def process_pip_audit_results(self, file_path: str) -> Dict[str, Any]:
        """Process pip-audit JSON results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            vulnerabilities = []
            if isinstance(data, dict):
                if 'vulnerabilities' in data:
                    vulnerabilities = data['vulnerabilities']
                elif 'dependencies' in data:
                    # pip-audit v2 format
                    for dep in data.get('dependencies', []):
                        for vuln in dep.get('vulnerabilities', []):
                            vuln['package'] = dep.get('name', 'Unknown')
                            vulnerabilities.append(vuln)
            elif isinstance(data, list):
                vulnerabilities = data
                
            return {
                'source': 'pip-audit',
                'vulnerabilities': vulnerabilities,
                'total': len(vulnerabilities)
            }
        except Exception as e:
            return {'source': 'pip-audit', 'error': str(e), 'vulnerabilities': [], 'total': 0}
    
    def process_safety_results(self, file_path: str) -> Dict[str, Any]:
        """Process Safety JSON results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            vulnerabilities = []
            if isinstance(data, list):
                vulnerabilities = data
            elif isinstance(data, dict) and 'vulnerabilities' in data:
                vulnerabilities = data['vulnerabilities']
                
            return {
                'source': 'Safety',
                'vulnerabilities': vulnerabilities,
                'total': len(vulnerabilities)
            }
        except Exception as e:
            return {'source': 'Safety', 'error': str(e), 'vulnerabilities': [], 'total': 0}
    
    def process_npm_audit_results(self, file_path: str) -> Dict[str, Any]:
        """Process npm audit JSON results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            vulnerabilities = []
            if isinstance(data, dict):
                if 'vulnerabilities' in data:
                    for pkg_name, pkg_data in data['vulnerabilities'].items():
                        if isinstance(pkg_data, dict) and 'via' in pkg_data:
                            for vuln in pkg_data.get('via', []):
                                if isinstance(vuln, dict):
                                    vulnerabilities.append({
                                        'package': pkg_name,
                                        'severity': pkg_data.get('severity', 'unknown'),
                                        'title': vuln.get('title', ''),
                                        'url': vuln.get('url', ''),
                                        'cwe': vuln.get('cwe', []),
                                        'cve': vuln.get('cve', ''),
                                        'range': pkg_data.get('range', ''),
                                        'fixAvailable': pkg_data.get('fixAvailable', False)
                                    })
                
            return {
                'source': 'npm audit',
                'vulnerabilities': vulnerabilities,
                'total': len(vulnerabilities)
            }
        except Exception as e:
            return {'source': 'npm audit', 'error': str(e), 'vulnerabilities': [], 'total': 0}
    
    def process_trivy_results(self, file_path: str, image_name: str) -> Dict[str, Any]:
        """Process Trivy JSON results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            vulnerabilities = []
            if isinstance(data, dict):
                results = data.get('Results', [])
                for result in results:
                    if 'Vulnerabilities' in result:
                        for vuln in result['Vulnerabilities']:
                            vulnerabilities.append({
                                'vulnerabilityID': vuln.get('VulnerabilityID', ''),
                                'pkgName': vuln.get('PkgName', ''),
                                'installedVersion': vuln.get('InstalledVersion', ''),
                                'fixedVersion': vuln.get('FixedVersion', ''),
                                'severity': vuln.get('Severity', 'UNKNOWN'),
                                'title': vuln.get('Title', ''),
                                'description': vuln.get('Description', ''),
                                'primaryURL': vuln.get('PrimaryURL', ''),
                                'cweIDs': vuln.get('CweIDs', [])
                            })
            
            return {
                'source': 'Trivy',
                'image': image_name,
                'vulnerabilities': vulnerabilities,
                'total': len(vulnerabilities)
            }
        except Exception as e:
            return {'source': 'Trivy', 'image': image_name, 'error': str(e), 'vulnerabilities': [], 'total': 0}
    
    def try_fix_python_package(self, package_name: str, current_version: str, fix_version: str) -> bool:
        """Try to update a Python package to a fixed version"""
        try:
            # Check if fix_version is available
            if fix_version and fix_version != 'N/A':
                # Try to install the fixed version
                result = subprocess.run(
                    ['pip', 'install', f'{package_name}=={fix_version}'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    return True
            return False
        except Exception:
            return False
    
    def generate_package_summary(self, package_name: str, vulnerabilities: List[Dict], source: str):
        """Generate summary for a specific package"""
        self.add_line(f"### 📦 {package_name}")
        self.add_line(f"**Source:** {source}")
        self.add_line(f"**Total Vulnerabilities:** {len(vulnerabilities)}")
        self.add_line("")
        
        if not vulnerabilities:
            self.add_line("✅ **No vulnerabilities found**")
            self.add_line("")
            return
        
        # Group by severity
        by_severity = defaultdict(list)
        fixed_count = 0
        unfixed_count = 0
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', vuln.get('Severity', 'UNKNOWN')).upper()
            by_severity[severity].append(vuln)
            
            # Check if fixable
            fix_version = vuln.get('fixedVersion', vuln.get('fixAvailable', False))
            if fix_version and fix_version != 'N/A' and fix_version != False:
                fixed_count += 1
            else:
                unfixed_count += 1
        
        # Status
        if fixed_count > 0:
            self.add_line(f"⚠️ **Status:** {fixed_count} fixable, {unfixed_count} unfixed")
        else:
            self.add_line(f"❌ **Status:** {unfixed_count} unfixed vulnerabilities")
        self.add_line("")
        
        # Details by severity
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']
        for sev in severity_order:
            if sev in by_severity:
                self.add_line(f"#### {sev} Severity ({len(by_severity[sev])} vulnerabilities)")
                self.add_line("")
                
                for vuln in by_severity[sev]:
                    # Extract CVE - try multiple field names
                    cve = (vuln.get('vulnerabilityID') or 
                           vuln.get('VulnerabilityID') or 
                           vuln.get('cve') or 
                           vuln.get('id') or 
                           'N/A')
                    
                    # Extract title/description
                    title = (vuln.get('title') or 
                            vuln.get('Title') or 
                            vuln.get('name') or 
                            vuln.get('summary') or 
                            'Unknown vulnerability')
                    description = vuln.get('description') or vuln.get('Description') or ''
                    
                    # Extract versions
                    installed = (vuln.get('installedVersion') or 
                                vuln.get('InstalledVersion') or 
                                vuln.get('version') or 
                                'N/A')
                    
                    # Extract fixed version - check multiple sources
                    fixed = (vuln.get('fixedVersion') or 
                            vuln.get('FixedVersion') or 
                            None)
                    
                    # Check fix_versions array (can be list or dict)
                    if not fixed:
                        fix_versions = vuln.get('fix_versions', [])
                        if fix_versions:
                            if isinstance(fix_versions, list) and len(fix_versions) > 0:
                                fixed = fix_versions[0]
                            elif isinstance(fix_versions, dict) and len(fix_versions) > 0:
                                fixed = list(fix_versions.values())[0]
                    
                    # Check fixAvailable for npm
                    if not fixed:
                        fix_available = vuln.get('fixAvailable', False)
                        if fix_available:
                            fixed = 'Available (check package)'
                        else:
                            fixed = 'N/A'
                    
                    # Extract URL
                    url = (vuln.get('primaryURL') or 
                          vuln.get('PrimaryURL') or 
                          vuln.get('url') or 
                          vuln.get('link') or 
                          '')
                    
                    self.add_line(f"- **CVE/ID:** `{cve}`")
                    self.add_line(f"  - **Title:** {title}")
                    if description:
                        desc_short = description[:200] + "..." if len(description) > 200 else description
                        self.add_line(f"  - **Description:** {desc_short}")
                    self.add_line(f"  - **Installed Version:** `{installed}`")
                    self.add_line(f"  - **Fixed Version:** `{fixed}`")
                    if url:
                        self.add_line(f"  - **Reference:** {url}")
                    self.add_line("")
        
        self.add_line("---")
        self.add_line("")
    
    def generate_report(self, scan_results: Dict[str, Any]):
        """Generate the complete security report"""
        from datetime import datetime
        self.add_line("# 🔒 Security Scan Report")
        self.add_line("")
        self.add_line(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.add_line("")
        
        # Summary section
        self.add_section("📊 Executive Summary", 2)
        
        total_vulns = 0
        total_fixed = 0
        total_unfixed = 0
        
        for scan_type, results in scan_results.items():
            if 'error' in results:
                continue
            total_vulns += results.get('total', 0)
            # Count fixable vs unfixable
            for vuln in results.get('vulnerabilities', []):
                fix_version = vuln.get('fixedVersion', vuln.get('FixedVersion', vuln.get('fixAvailable', False)))
                if fix_version and fix_version != 'N/A' and fix_version != False:
                    total_fixed += 1
                else:
                    total_unfixed += 1
        
        self.add_line(f"- **Total Vulnerabilities Found:** {total_vulns}")
        self.add_line(f"- **Fixable:** {total_fixed}")
        self.add_line(f"- **Unfixable/No Fix Available:** {total_unfixed}")
        self.add_line("")
        
        # Detailed results by source
        self.add_section("📋 Detailed Results", 2)
        
        # Python dependencies
        if 'pip_audit' in scan_results:
            self.add_section("Python Dependencies (pip-audit)", 3)
            results = scan_results['pip_audit']
            if 'error' in results:
                self.add_line(f"❌ Error: {results['error']}")
            else:
                packages = defaultdict(list)
                for vuln in results.get('vulnerabilities', []):
                    # Try different field names for package name
                    pkg = vuln.get('name') or vuln.get('package') or vuln.get('dependency') or 'Unknown'
                    # Normalize vulnerability data
                    normalized_vuln = {
                        'severity': vuln.get('severity', vuln.get('aliases', [{}])[0].get('severity', 'UNKNOWN')),
                        'vulnerabilityID': vuln.get('id') or vuln.get('vulnerability_id') or vuln.get('aliases', [{}])[0].get('alias', 'N/A'),
                        'title': vuln.get('summary') or vuln.get('description', '')[:100],
                        'description': vuln.get('description', ''),
                        'installedVersion': vuln.get('version') or vuln.get('installed_version', 'N/A'),
                        'fixedVersion': vuln.get('fix_versions', [None])[0] if vuln.get('fix_versions') else None,
                        'fix_versions': vuln.get('fix_versions', []),
                        'primaryURL': vuln.get('link') or vuln.get('url', '')
                    }
                    packages[pkg].append(normalized_vuln)
                
                for pkg, vulns in sorted(packages.items()):
                    self.generate_package_summary(pkg, vulns, 'pip-audit')
        
        if 'safety' in scan_results:
            self.add_section("Python Dependencies (Safety)", 3)
            results = scan_results['safety']
            if 'error' in results:
                self.add_line(f"❌ Error: {results['error']}")
            else:
                packages = defaultdict(list)
                for vuln in results.get('vulnerabilities', []):
                    # Safety format
                    pkg = vuln.get('package_name') or vuln.get('name', 'Unknown')
                    # Normalize vulnerability data
                    normalized_vuln = {
                        'severity': vuln.get('severity', 'UNKNOWN'),
                        'vulnerabilityID': vuln.get('vulnerability_id') or vuln.get('cve', 'N/A'),
                        'title': vuln.get('advisory', '')[:100],
                        'description': vuln.get('advisory', ''),
                        'installedVersion': vuln.get('installed_version', 'N/A'),
                        'fixedVersion': vuln.get('spec', '') if vuln.get('spec', '').startswith('>=') else None,
                        'primaryURL': vuln.get('more_info_url', '')
                    }
                    packages[pkg].append(normalized_vuln)
                
                for pkg, vulns in sorted(packages.items()):
                    self.generate_package_summary(pkg, vulns, 'Safety')
        
        # Node.js dependencies
        if 'npm_audit' in scan_results:
            self.add_section("Node.js Dependencies (npm audit)", 3)
            results = scan_results['npm_audit']
            if 'error' in results:
                self.add_line(f"❌ Error: {results['error']}")
            else:
                packages = defaultdict(list)
                for vuln in results.get('vulnerabilities', []):
                    pkg = vuln.get('package', 'Unknown')
                    packages[pkg].append(vuln)
                
                for pkg, vulns in sorted(packages.items()):
                    self.generate_package_summary(pkg, vulns, 'npm audit')
        
        # Docker images - base images
        self.add_section("🐳 Docker Base Images", 3)
        for key in ['trivy_python', 'trivy_node', 'trivy_mysql']:
            if key in scan_results:
                image_name = key.replace('trivy_', '').replace('_', ':')
                self.add_section(f"Base Image: {image_name}", 4)
                results = scan_results[key]
                if 'error' in results:
                    self.add_line(f"❌ Error: {results['error']}")
                else:
                    packages = defaultdict(list)
                    for vuln in results.get('vulnerabilities', []):
                        pkg = vuln.get('pkgName', vuln.get('PkgName', 'Unknown'))
                        packages[pkg].append(vuln)

                    for pkg, vulns in sorted(packages.items()):
                        self.generate_package_summary(pkg, vulns, f"Trivy ({results.get('image', image_name)})")

        # Docker images - built application images
        self.add_section("🏗️ Built Application Images", 3)
        for key in ['trivy_backend_built', 'trivy_frontend_built']:
            if key in scan_results:
                image_name = results.get('image', key.replace('trivy_', '').replace('_built', ''))
                self.add_section(f"Built Image: {image_name}", 4)
                results = scan_results[key]
                if 'error' in results:
                    self.add_line(f"❌ Error: {results['error']}")
                else:
                    packages = defaultdict(list)
                    for vuln in results.get('vulnerabilities', []):
                        pkg = vuln.get('pkgName', vuln.get('PkgName', 'Unknown'))
                        packages[pkg].append(vuln)

                    for pkg, vulns in sorted(packages.items()):
                        self.generate_package_summary(pkg, vulns, f"Trivy ({results.get('image', image_name)})")
        
        # Recommendations
        self.add_section("💡 Recommendations", 2)
        if total_fixed > 0:
            self.add_line(f"- ⚠️ **{total_fixed} vulnerabilities have fixes available** - Consider updating packages")
        if total_unfixed > 0:
            self.add_line(f"- ❌ **{total_unfixed} vulnerabilities have no fix available** - Monitor for updates")
        self.add_line("- 🔄 Regularly update dependencies to latest stable versions")
        self.add_line("- 📚 Review CVE details and assess risk for your specific use case")
        self.add_line("")
        
        return "\n".join(self.report_lines)


def main():
    """Main function"""
    # Paths
    base_dir = Path(__file__).parent.parent.parent
    backend_dir = base_dir / 'phishing_detector' / 'backend'
    frontend_dir = base_dir / 'phishing_detector' / 'frontend'
    
    generator = SecurityReportGenerator()
    scan_results = {}
    
    # Process pip-audit results
    pip_audit_file = backend_dir / 'pip-audit-results.json'
    if pip_audit_file.exists():
        print(f"📄 Processing pip-audit results from {pip_audit_file}")
        scan_results['pip_audit'] = generator.process_pip_audit_results(str(pip_audit_file))
    else:
        print(f"⚠️ pip-audit results file not found: {pip_audit_file}")
    
    # Process Safety results
    safety_file = backend_dir / 'safety-results.json'
    if safety_file.exists():
        print(f"📄 Processing Safety results from {safety_file}")
        scan_results['safety'] = generator.process_safety_results(str(safety_file))
    else:
        print(f"⚠️ Safety results file not found: {safety_file}")
    
    # Process npm audit results
    npm_audit_file = frontend_dir / 'npm-audit-results.json'
    if npm_audit_file.exists():
        print(f"📄 Processing npm audit results from {npm_audit_file}")
        scan_results['npm_audit'] = generator.process_npm_audit_results(str(npm_audit_file))
    else:
        print(f"⚠️ npm audit results file not found: {npm_audit_file}")
    
    # Process Trivy results - base images
    trivy_files = {
        'trivy_python': base_dir / 'python-base-scan.json',
        'trivy_node': base_dir / 'node-base-scan.json',
        'trivy_mysql': base_dir / 'mysql-base-scan.json'
    }

    for key, file_path in trivy_files.items():
        if file_path.exists():
            print(f"📄 Processing Trivy results from {file_path}")
            image_name = key.replace('trivy_', '').replace('_', ':')
            scan_results[key] = generator.process_trivy_results(str(file_path), image_name)
        else:
            print(f"⚠️ Trivy results file not found: {file_path}")

    # Process Trivy results - built images
    built_image_files = {
        'trivy_backend_built': backend_dir / 'backend-built-scan.json',
        'trivy_frontend_built': frontend_dir / 'frontend-built-scan.json'
    }

    for key, file_path in built_image_files.items():
        if file_path.exists():
            print(f"📄 Processing built image Trivy results from {file_path}")
            image_name = key.replace('trivy_', '').replace('_built', '').replace('_', '-')
            scan_results[key] = generator.process_trivy_results(str(file_path), f"Built: {image_name}")
        else:
            print(f"⚠️ Built image Trivy results file not found: {file_path}")
    
    if not scan_results:
        print("❌ No scan results found! Cannot generate report.")
        sys.exit(1)
    
    # Generate report
    print("\n📝 Generating security report...")
    report = generator.generate_report(scan_results)
    
    # Write report
    report_file = base_dir / 'SECURITY_SCAN_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Security report generated: {report_file}")
    
    total_vulns = sum(r.get('total', 0) for r in scan_results.values() if 'error' not in r)
    print(f"\n📊 Summary:")
    print(f"   Total vulnerabilities: {total_vulns}")
    
    # Also print formatted JSON for easier reading
    json_report_file = base_dir / 'security-scan-summary.json'
    with open(json_report_file, 'w', encoding='utf-8') as f:
        json.dump(scan_results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON summary saved: {json_report_file}")


if __name__ == '__main__':
    main()
