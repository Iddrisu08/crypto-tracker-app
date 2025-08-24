#!/usr/bin/env python3

"""
SECURITY REPORT GENERATOR
Consolidates security scan results from multiple tools into a comprehensive report.
Generates HTML dashboard with vulnerability metrics, trends, and remediation guidance.
"""

import json
import os
import sys
import glob
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from jinja2 import Template
import re

@dataclass
class Vulnerability:
    """Data class representing a security vulnerability."""
    title: str
    severity: str
    description: str
    file_path: str = ""
    line_number: int = 0
    cwe_id: str = ""
    cve_id: str = ""
    tool: str = ""
    category: str = ""
    remediation: str = ""
    confidence: str = "medium"

@dataclass
class SecurityMetrics:
    """Data class for security metrics and statistics."""
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    fixed_count: int = 0
    tools_used: List[str] = None
    scan_timestamp: str = ""
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []

class SecurityReportGenerator:
    """
    SECURITY REPORT GENERATOR
    Processes security scan results from multiple tools and generates comprehensive reports.
    """
    
    def __init__(self, results_directory: str):
        self.results_dir = Path(results_directory)
        self.vulnerabilities: List[Vulnerability] = []
        self.metrics = SecurityMetrics()
        self.scan_timestamp = datetime.datetime.now().isoformat()
        
        # Tool-specific parsers
        self.parsers = {
            'bandit': self._parse_bandit_results,
            'semgrep': self._parse_semgrep_results,
            'trivy': self._parse_trivy_results,
            'npm-audit': self._parse_npm_audit_results,
            'safety': self._parse_safety_results,
            'checkov': self._parse_checkov_results,
            'trufflehog': self._parse_trufflehog_results,
            'eslint': self._parse_eslint_results,
            'actionlint': self._parse_actionlint_results
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive security report."""
        print("🔍 Parsing security scan results...")
        self._parse_all_results()
        
        print("📊 Calculating security metrics...")
        self._calculate_metrics()
        
        print("📄 Generating HTML report...")
        return self._generate_html_report()
    
    def _parse_all_results(self):
        """Parse results from all security tools."""
        # Find all JSON result files
        json_files = list(self.results_dir.rglob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Determine tool type from filename or content
                tool_type = self._identify_tool_type(json_file.name, data)
                
                if tool_type and tool_type in self.parsers:
                    print(f"📝 Parsing {tool_type} results from {json_file.name}")
                    self.parsers[tool_type](data, str(json_file))
                
            except Exception as e:
                print(f"⚠️ Error parsing {json_file}: {e}")
                continue
    
    def _identify_tool_type(self, filename: str, data: Dict) -> Optional[str]:
        """Identify the security tool based on filename and content structure."""
        filename_lower = filename.lower()
        
        # Check filename patterns
        if 'bandit' in filename_lower:
            return 'bandit'
        elif 'semgrep' in filename_lower:
            return 'semgrep'
        elif 'trivy' in filename_lower:
            return 'trivy'
        elif 'npm-audit' in filename_lower or 'npm_audit' in filename_lower:
            return 'npm-audit'
        elif 'safety' in filename_lower:
            return 'safety'
        elif 'checkov' in filename_lower:
            return 'checkov'
        elif 'trufflehog' in filename_lower:
            return 'trufflehog'
        elif 'eslint' in filename_lower:
            return 'eslint'
        elif 'actionlint' in filename_lower:
            return 'actionlint'
        
        # Check data structure patterns
        if isinstance(data, dict):
            if 'results' in data and isinstance(data.get('results'), list):
                if any('test_name' in item for item in data['results'][:1]):
                    return 'bandit'
            elif 'vulnerabilities' in data:
                return 'npm-audit'
            elif 'SchemaVersion' in data or 'Results' in data:
                return 'trivy'
        
        return None
    
    def _parse_bandit_results(self, data: Dict, source_file: str):
        """Parse Bandit security scan results."""
        results = data.get('results', [])
        
        for result in results:
            vulnerability = Vulnerability(
                title=result.get('test_name', 'Unknown Security Issue'),
                severity=self._normalize_severity(result.get('issue_severity', 'medium')),
                description=result.get('issue_text', ''),
                file_path=result.get('filename', ''),
                line_number=result.get('line_number', 0),
                cwe_id=result.get('test_id', ''),
                tool='bandit',
                category='SAST',
                confidence=result.get('issue_confidence', 'medium').lower(),
                remediation=self._get_bandit_remediation(result.get('test_id', ''))
            )
            self.vulnerabilities.append(vulnerability)
    
    def _parse_semgrep_results(self, data: Dict, source_file: str):
        """Parse Semgrep security scan results."""
        results = data.get('results', [])
        
        for result in results:
            vulnerability = Vulnerability(
                title=result.get('check_id', 'Security Issue').split('.')[-1],
                severity=self._normalize_severity(result.get('extra', {}).get('severity', 'medium')),
                description=result.get('extra', {}).get('message', ''),
                file_path=result.get('path', ''),
                line_number=result.get('start', {}).get('line', 0),
                cwe_id=result.get('extra', {}).get('metadata', {}).get('cwe', ''),
                tool='semgrep',
                category='SAST',
                remediation=result.get('extra', {}).get('fix', '')
            )
            self.vulnerabilities.append(vulnerability)
    
    def _parse_trivy_results(self, data: Dict, source_file: str):
        """Parse Trivy container scan results."""
        results = data.get('Results', [])
        
        for result in results:
            vulnerabilities = result.get('Vulnerabilities', [])
            
            for vuln in vulnerabilities:
                vulnerability = Vulnerability(
                    title=vuln.get('Title', vuln.get('VulnerabilityID', 'Container Vulnerability')),
                    severity=self._normalize_severity(vuln.get('Severity', 'medium')),
                    description=vuln.get('Description', ''),
                    file_path=result.get('Target', ''),
                    cve_id=vuln.get('VulnerabilityID', ''),
                    tool='trivy',
                    category='Container Security',
                    remediation=vuln.get('FixedVersion', f"Update {vuln.get('PkgName', 'package')} to fixed version")
                )
                self.vulnerabilities.append(vulnerability)
    
    def _parse_npm_audit_results(self, data: Dict, source_file: str):
        """Parse NPM audit results."""
        vulnerabilities = data.get('vulnerabilities', {})
        
        for package_name, vuln_data in vulnerabilities.items():
            vulnerability = Vulnerability(
                title=f"Vulnerable dependency: {package_name}",
                severity=self._normalize_severity(vuln_data.get('severity', 'medium')),
                description=vuln_data.get('via', [{}])[0].get('title', '') if isinstance(vuln_data.get('via'), list) else str(vuln_data.get('via', '')),
                file_path='package.json',
                tool='npm-audit',
                category='Dependency Security',
                remediation=f"Update {package_name} to version {vuln_data.get('fixAvailable', 'latest')}"
            )
            self.vulnerabilities.append(vulnerability)
    
    def _parse_safety_results(self, data: Dict, source_file: str):
        """Parse Safety (Python) security scan results."""
        vulnerabilities = data if isinstance(data, list) else data.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            vulnerability = Vulnerability(
                title=f"Vulnerable Python package: {vuln.get('package', 'Unknown')}",
                severity=self._normalize_severity('high'),  # Safety reports are typically high severity
                description=vuln.get('advisory', ''),
                file_path='requirements.txt',
                cve_id=vuln.get('id', ''),
                tool='safety',
                category='Dependency Security',
                remediation=f"Update {vuln.get('package', 'package')} to version {vuln.get('analyzed_version', 'latest')}"
            )
            self.vulnerabilities.append(vulnerability)
    
    def _parse_checkov_results(self, data: Dict, source_file: str):
        """Parse Checkov IaC security scan results."""
        failed_checks = data.get('results', {}).get('failed_checks', [])
        
        for check in failed_checks:
            vulnerability = Vulnerability(
                title=check.get('check_name', 'IaC Security Issue'),
                severity=self._normalize_severity(check.get('severity', 'medium')),
                description=check.get('description', ''),
                file_path=check.get('file_path', ''),
                line_number=check.get('file_line_range', [0, 0])[0],
                tool='checkov',
                category='Infrastructure Security',
                remediation=check.get('guideline', 'Review and fix the security misconfiguration')
            )
            self.vulnerabilities.append(vulnerability)
    
    def _parse_trufflehog_results(self, data: Dict, source_file: str):
        """Parse TruffleHog secrets detection results."""
        # TruffleHog can output different formats, handle both
        results = data if isinstance(data, list) else [data]
        
        for result in results:
            if isinstance(result, dict) and 'DetectorName' in result:
                vulnerability = Vulnerability(
                    title=f"Secret detected: {result.get('DetectorName', 'Unknown')}",
                    severity='critical',  # Exposed secrets are always critical
                    description=f"Potential secret found in {result.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', '')}",
                    file_path=result.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', ''),
                    line_number=result.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('line', 0),
                    tool='trufflehog',
                    category='Secrets Detection',
                    remediation="Rotate the exposed secret and remove it from version control"
                )
                self.vulnerabilities.append(vulnerability)
    
    def _parse_eslint_results(self, data: List, source_file: str):
        """Parse ESLint security results."""
        if not isinstance(data, list):
            return
        
        for file_result in data:
            messages = file_result.get('messages', [])
            
            for message in messages:
                # Only include security-related rules
                rule_id = message.get('ruleId', '')
                if any(sec_rule in rule_id for sec_rule in ['security', 'xss', 'sql', 'csrf', 'auth']):
                    vulnerability = Vulnerability(
                        title=f"ESLint Security: {rule_id}",
                        severity=self._normalize_severity(message.get('severity', 1)),
                        description=message.get('message', ''),
                        file_path=file_result.get('filePath', ''),
                        line_number=message.get('line', 0),
                        tool='eslint',
                        category='SAST',
                        remediation="Review and fix the security issue according to ESLint recommendations"
                    )
                    self.vulnerabilities.append(vulnerability)
    
    def _parse_actionlint_results(self, data: List, source_file: str):
        """Parse actionlint GitHub Actions security results."""
        if not isinstance(data, list):
            return
        
        for issue in data:
            vulnerability = Vulnerability(
                title=f"GitHub Actions Issue: {issue.get('kind', 'Unknown')}",
                severity=self._normalize_severity('medium'),
                description=issue.get('message', ''),
                file_path=issue.get('filepath', ''),
                line_number=issue.get('line', 0),
                tool='actionlint',
                category='CI/CD Security',
                remediation="Review and fix the GitHub Actions workflow security issue"
            )
            self.vulnerabilities.append(vulnerability)
    
    def _normalize_severity(self, severity) -> str:
        """Normalize severity levels across different tools."""
        if isinstance(severity, int):
            # ESLint uses numeric severity
            return 'medium' if severity == 1 else 'high'
        
        severity_str = str(severity).upper()
        
        # Map various severity formats to standard levels
        severity_mapping = {
            'CRITICAL': 'critical',
            'HIGH': 'high', 
            'MEDIUM': 'medium',
            'MODERATE': 'medium',
            'LOW': 'low',
            'INFO': 'info',
            'INFORMATIONAL': 'info',
            'WARNING': 'medium',
            'ERROR': 'high',
            'SEVERE': 'high'
        }
        
        return severity_mapping.get(severity_str, 'medium')
    
    def _get_bandit_remediation(self, test_id: str) -> str:
        """Get specific remediation advice for Bandit test IDs."""
        remediation_map = {
            'B101': 'Remove or replace the assert statement with proper error handling',
            'B102': 'Use safe alternatives to exec() or validate input thoroughly',
            'B103': 'Set file permissions explicitly instead of using 0o777',
            'B104': 'Bind to localhost (127.0.0.1) instead of all interfaces (0.0.0.0)',
            'B105': 'Remove hardcoded passwords and use secure configuration management',
            'B106': 'Remove hardcoded passwords and use secure configuration management',
            'B107': 'Remove hardcoded passwords and use secure configuration management',
            'B108': 'Handle exceptions properly instead of using bare except clauses',
            'B110': 'Use logging instead of try/except pass blocks',
            'B112': 'Implement proper request limits or timeouts',
            'B201': 'Use subprocess with shell=False or validate input thoroughly',
            'B301': 'Use safe pickle alternatives or validate data sources',
            'B302': 'Use safe alternatives to marshal.loads()',
            'B303': 'Use hashlib with explicit algorithms instead of MD5',
            'B304': 'Use hashlib with explicit algorithms instead of SHA1',
            'B305': 'Use secrets module for cryptographically secure random numbers',
            'B306': 'Use tempfile.mkstemp() instead of tempfile.mktemp()',
            'B307': 'Use subprocess with shell=False',
            'B308': 'Use subprocess with shell=False',
            'B309': 'Use subprocess with shell=False',
            'B310': 'Validate URLs and use allowlists for urllib.urlopen',
            'B311': 'Use secrets module for cryptographically secure random numbers',
            'B312': 'Use safe alternatives or validate input for telnetlib',
            'B313': 'Use safe XML parsing with defusedxml',
            'B314': 'Use safe XML parsing with defusedxml',
            'B315': 'Use safe XML parsing with defusedxml',
            'B316': 'Use safe XML parsing with defusedxml',
            'B317': 'Use safe XML parsing with defusedxml',
            'B318': 'Use safe XML parsing with defusedxml',
            'B319': 'Use safe XML parsing with defusedxml',
            'B320': 'Use safe XML parsing with defusedxml',
            'B321': 'Use safe FTP alternatives with proper authentication',
            'B322': 'Validate input thoroughly before passing to eval-like functions',
            'B323': 'Use python-pkcs11 or similar secure alternatives',
            'B324': 'Use strong cryptographic hash functions (SHA-256 or better)',
            'B325': 'Use secure random number generation with secrets module',
            'B501': 'Disable SSL certificate verification only in development',
            'B502': 'Use strong SSL/TLS configurations',
            'B503': 'Use strong SSL/TLS configurations',
            'B504': 'Use strong SSL/TLS configurations',
            'B505': 'Use strong SSL/TLS configurations',
            'B506': 'Use safe YAML loading with yaml.safe_load()',
            'B507': 'Validate SSH host keys properly',
            'B601': 'Use subprocess with shell=False or validate input',
            'B602': 'Use subprocess with shell=False',
            'B603': 'Use subprocess with shell=False',
            'B604': 'Use subprocess with shell=False',
            'B605': 'Use subprocess with shell=False',
            'B606': 'Use subprocess with shell=False',
            'B607': 'Use absolute paths for executables',
            'B608': 'Use parameterized queries to prevent SQL injection',
            'B609': 'Use parameterized queries to prevent SQL injection',
            'B610': 'Use parameterized queries to prevent SQL injection',
            'B611': 'Use parameterized queries to prevent SQL injection',
            'B701': 'Use jinja2.select_autoescape() or manual escaping',
            'B702': 'Use jinja2.select_autoescape() or manual escaping',
            'B703': 'Use jinja2.select_autoescape() or manual escaping'
        }
        
        return remediation_map.get(test_id, 'Review Bandit documentation for specific remediation steps')
    
    def _calculate_metrics(self):
        """Calculate security metrics from parsed vulnerabilities."""
        self.metrics.total_vulnerabilities = len(self.vulnerabilities)
        self.metrics.scan_timestamp = self.scan_timestamp
        
        # Count by severity
        for vuln in self.vulnerabilities:
            if vuln.severity == 'critical':
                self.metrics.critical_count += 1
            elif vuln.severity == 'high':
                self.metrics.high_count += 1
            elif vuln.severity == 'medium':
                self.metrics.medium_count += 1
            elif vuln.severity == 'low':
                self.metrics.low_count += 1
            else:
                self.metrics.info_count += 1
        
        # Count tools used
        tools_used = set(vuln.tool for vuln in self.vulnerabilities)
        self.metrics.tools_used = sorted(list(tools_used))
    
    def _generate_html_report(self) -> str:
        """Generate comprehensive HTML security report."""
        
        # Group vulnerabilities by category and severity
        vulnerabilities_by_category = {}
        vulnerabilities_by_severity = {}
        
        for vuln in self.vulnerabilities:
            # Group by category
            if vuln.category not in vulnerabilities_by_category:
                vulnerabilities_by_category[vuln.category] = []
            vulnerabilities_by_category[vuln.category].append(vuln)
            
            # Group by severity
            if vuln.severity not in vulnerabilities_by_severity:
                vulnerabilities_by_severity[vuln.severity] = []
            vulnerabilities_by_severity[vuln.severity].append(vuln)
        
        # Calculate risk score (weighted by severity)
        severity_weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 2, 'info': 1}
        risk_score = sum(severity_weights.get(vuln.severity, 1) for vuln in self.vulnerabilities)
        
        # Generate HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Security Scan Report - Crypto Tracker</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .content { padding: 30px; }
        
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .metric-card { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center; 
            border-left: 4px solid #667eea;
        }
        .metric-number { 
            font-size: 2em; 
            font-weight: bold; 
            color: #667eea; 
        }
        .metric-label { 
            color: #6c757d; 
            font-size: 0.9em; 
            margin-top: 5px; 
        }
        
        .severity-critical .metric-number { color: #dc3545; }
        .severity-critical { border-left-color: #dc3545; }
        .severity-high .metric-number { color: #fd7e14; }
        .severity-high { border-left-color: #fd7e14; }
        .severity-medium .metric-number { color: #ffc107; }
        .severity-medium { border-left-color: #ffc107; }
        .severity-low .metric-number { color: #20c997; }
        .severity-low { border-left-color: #20c997; }
        
        .section { margin: 30px 0; }
        .section h2 { 
            color: #495057; 
            border-bottom: 2px solid #e9ecef; 
            padding-bottom: 10px; 
        }
        
        .vulnerability-table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
        }
        .vulnerability-table th, 
        .vulnerability-table td { 
            border: 1px solid #dee2e6; 
            padding: 12px; 
            text-align: left; 
        }
        .vulnerability-table th { 
            background-color: #f8f9fa; 
            font-weight: 600; 
        }
        
        .severity-badge { 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 0.8em; 
            font-weight: bold; 
            text-transform: uppercase; 
        }
        .severity-critical { background-color: #f8d7da; color: #721c24; }
        .severity-high { background-color: #fdeaa7; color: #856404; }
        .severity-medium { background-color: #fff3cd; color: #856404; }
        .severity-low { background-color: #d1ecf1; color: #0c5460; }
        .severity-info { background-color: #e2e3e5; color: #383d41; }
        
        .tool-badge { 
            background-color: #e9ecef; 
            color: #495057; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-size: 0.7em; 
        }
        
        .remediation { 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-radius: 4px; 
            border-left: 3px solid #17a2b8; 
            margin-top: 10px; 
            font-size: 0.9em; 
        }
        
        .footer { 
            background-color: #f8f9fa; 
            padding: 20px; 
            text-align: center; 
            color: #6c757d; 
            border-top: 1px solid #dee2e6; 
        }
        
        .risk-score { 
            font-size: 1.5em; 
            font-weight: bold; 
            color: {{ 'red' if risk_score > 50 else 'orange' if risk_score > 20 else 'green' }}; 
        }
        
        .expandable { cursor: pointer; }
        .expandable:hover { background-color: #f8f9fa; }
        .details { display: none; }
        
        @media (max-width: 768px) {
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .vulnerability-table { font-size: 0.9em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Security Scan Report</h1>
            <p>Crypto Tracker Application - Generated on {{ metrics.scan_timestamp[:19] }}</p>
        </div>
        
        <div class="content">
            <!-- Security Metrics -->
            <div class="section">
                <h2>📊 Security Overview</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-number">{{ metrics.total_vulnerabilities }}</div>
                        <div class="metric-label">Total Vulnerabilities</div>
                    </div>
                    <div class="metric-card severity-critical">
                        <div class="metric-number">{{ metrics.critical_count }}</div>
                        <div class="metric-label">Critical</div>
                    </div>
                    <div class="metric-card severity-high">
                        <div class="metric-number">{{ metrics.high_count }}</div>
                        <div class="metric-label">High</div>
                    </div>
                    <div class="metric-card severity-medium">
                        <div class="metric-number">{{ metrics.medium_count }}</div>
                        <div class="metric-label">Medium</div>
                    </div>
                    <div class="metric-card severity-low">
                        <div class="metric-number">{{ metrics.low_count }}</div>
                        <div class="metric-label">Low</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number risk-score">{{ risk_score }}</div>
                        <div class="metric-label">Risk Score</div>
                    </div>
                </div>
            </div>
            
            <!-- Tools Used -->
            <div class="section">
                <h2>🔧 Security Tools Used</h2>
                <p>
                    {% for tool in metrics.tools_used %}
                        <span class="tool-badge">{{ tool }}</span>
                    {% endfor %}
                </p>
            </div>
            
            <!-- Vulnerabilities by Severity -->
            {% for severity in ['critical', 'high', 'medium', 'low', 'info'] %}
                {% if vulnerabilities_by_severity.get(severity) %}
                <div class="section">
                    <h2>{{ severity.title() }} Severity Vulnerabilities ({{ vulnerabilities_by_severity[severity]|length }})</h2>
                    <table class="vulnerability-table">
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Tool</th>
                                <th>File</th>
                                <th>Category</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for vuln in vulnerabilities_by_severity[severity][:20] %}
                            <tr class="expandable" onclick="toggleDetails(this)">
                                <td>{{ vuln.title[:80] }}{% if vuln.title|length > 80 %}...{% endif %}</td>
                                <td><span class="tool-badge">{{ vuln.tool }}</span></td>
                                <td>{{ vuln.file_path.split('/')[-1] if vuln.file_path else 'N/A' }}</td>
                                <td>{{ vuln.category }}</td>
                                <td>
                                    <span class="severity-badge severity-{{ severity }}">{{ severity }}</span>
                                </td>
                            </tr>
                            <tr class="details">
                                <td colspan="5">
                                    <p><strong>Description:</strong> {{ vuln.description }}</p>
                                    {% if vuln.file_path %}
                                    <p><strong>File:</strong> {{ vuln.file_path }}
                                    {% if vuln.line_number %} (Line {{ vuln.line_number }}){% endif %}</p>
                                    {% endif %}
                                    {% if vuln.cve_id %}
                                    <p><strong>CVE ID:</strong> {{ vuln.cve_id }}</p>
                                    {% endif %}
                                    {% if vuln.cwe_id %}
                                    <p><strong>CWE ID:</strong> {{ vuln.cwe_id }}</p>
                                    {% endif %}
                                    {% if vuln.remediation %}
                                    <div class="remediation">
                                        <strong>🔧 Remediation:</strong> {{ vuln.remediation }}
                                    </div>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                            {% if vulnerabilities_by_severity[severity]|length > 20 %}
                            <tr>
                                <td colspan="5" style="text-align: center; font-style: italic;">
                                    ... and {{ vulnerabilities_by_severity[severity]|length - 20 }} more {{ severity }} vulnerabilities
                                </td>
                            </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
            {% endfor %}
            
            <!-- Recommendations -->
            <div class="section">
                <h2>💡 Security Recommendations</h2>
                <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; border-left: 4px solid #0066cc;">
                    <h3>Immediate Actions (Critical & High)</h3>
                    <ul>
                        {% if metrics.critical_count > 0 %}
                        <li><strong>🚨 Address {{ metrics.critical_count }} critical vulnerabilities immediately</strong></li>
                        {% endif %}
                        {% if metrics.high_count > 0 %}
                        <li>📋 Plan remediation for {{ metrics.high_count }} high-severity issues</li>
                        {% endif %}
                        <li>🔄 Update dependencies to latest secure versions</li>
                        <li>🔐 Review exposed secrets and rotate if necessary</li>
                        <li>🛡️ Implement security headers and HTTPS enforcement</li>
                    </ul>
                    
                    <h3>Ongoing Security Improvements</h3>
                    <ul>
                        <li>📊 Set up continuous security monitoring</li>
                        <li>🔄 Enable automated dependency updates</li>
                        <li>🧪 Add security testing to CI/CD pipeline</li>
                        <li>📚 Conduct security training for development team</li>
                        <li>📋 Establish incident response procedures</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Crypto Tracker Security Scanner | Report includes {{ metrics.tools_used|length }} security tools</p>
            <p>Next scan recommended: {{ (metrics.scan_timestamp | strptime('%Y-%m-%dT%H:%M:%S.%f') + timedelta(days=1)).strftime('%Y-%m-%d') }}</p>
        </div>
    </div>
    
    <script>
        function toggleDetails(row) {
            const detailsRow = row.nextElementSibling;
            if (detailsRow.classList.contains('details')) {
                detailsRow.style.display = detailsRow.style.display === 'none' || detailsRow.style.display === '' ? 'table-row' : 'none';
            }
        }
        
        // Auto-expand critical vulnerabilities
        document.addEventListener('DOMContentLoaded', function() {
            const criticalSection = document.querySelector('h2:contains("Critical")');
            if (criticalSection) {
                const table = criticalSection.nextElementSibling;
                const detailRows = table.querySelectorAll('.details');
                detailRows.forEach(row => row.style.display = 'table-row');
            }
        });
    </script>
</body>
</html>
        """
        
        # Render template with data
        template = Template(html_template)
        html_content = template.render(
            metrics=self.metrics,
            vulnerabilities=self.vulnerabilities,
            vulnerabilities_by_category=vulnerabilities_by_category,
            vulnerabilities_by_severity=vulnerabilities_by_severity,
            risk_score=risk_score
        )
        
        return html_content

def main():
    """Main function to generate security report."""
    if len(sys.argv) != 2:
        print("Usage: python generate-security-report.py <results_directory>")
        sys.exit(1)
    
    results_directory = sys.argv[1]
    
    if not os.path.exists(results_directory):
        print(f"❌ Results directory not found: {results_directory}")
        sys.exit(1)
    
    print(f"🔍 Generating security report from: {results_directory}")
    
    generator = SecurityReportGenerator(results_directory)
    html_report = generator.generate_report()
    
    print("✅ Security report generated successfully!")
    print(f"📊 Found {generator.metrics.total_vulnerabilities} vulnerabilities")
    print(f"🚨 Critical: {generator.metrics.critical_count}")
    print(f"⚠️ High: {generator.metrics.high_count}")
    print(f"🔶 Medium: {generator.metrics.medium_count}")
    print(f"🔷 Low: {generator.metrics.low_count}")
    
    return html_report

if __name__ == '__main__':
    html_output = main()
    print(html_output)