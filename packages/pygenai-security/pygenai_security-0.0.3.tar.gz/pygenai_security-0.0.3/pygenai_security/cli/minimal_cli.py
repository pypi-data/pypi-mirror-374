"""
Minimal CLI for PyGenAI Security Framework
Works without full framework installation
"""

import click
import sys
import os
from pathlib import Path

@click.group()
@click.version_option(version='1.0.0', prog_name='PyGenAI Security Framework')
def cli():
    """PyGenAI Security Framework - Minimal Version"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--mode', default='fast', help='Scanning mode')
@click.option('--format', default='text', help='Output format') 
@click.option('--output', help='Output file')
def scan(path, mode, format, output):
    """Scan directory or file for security vulnerabilities"""
    
    click.echo(f"🛡️ PyGenAI Security Framework v1.0.0")
    click.echo(f"🔍 Scanning: {path}")
    click.echo(f"📊 Mode: {mode}")
    
    # Simple file analysis
    path_obj = Path(path)
    
    if path_obj.is_file():
        files_to_scan = [path_obj]
    else:
        files_to_scan = list(path_obj.rglob("*.py"))
    
    click.echo(f"📁 Found {len(files_to_scan)} Python files")
    
    vulnerabilities = []
    
    # Basic security checks
    for file_path in files_to_scan:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            vulns = basic_security_scan(file_path, content)
            vulnerabilities.extend(vulns)
            
        except Exception as e:
            click.echo(f"⚠️ Error scanning {file_path}: {e}")
    
    # Display results
    if format == 'text':
        display_text_results(vulnerabilities, len(files_to_scan))
    elif format == 'json':
        import json
        results = {
            'summary': {
                'total_vulnerabilities': len(vulnerabilities),
                'files_scanned': len(files_to_scan)
            },
            'vulnerabilities': [v.__dict__ if hasattr(v, '__dict__') else v for v in vulnerabilities]
        }
        
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"✅ Results saved to {output}")
        else:
            click.echo(json.dumps(results, indent=2))
    
    if vulnerabilities:
        click.echo(f"⚠️ Found {len(vulnerabilities)} potential security issues")
        sys.exit(1)
    else:
        click.echo("✅ No obvious security issues found")
        sys.exit(0)

@cli.command()
def status():
    """Show PyGenAI status"""
    click.echo("🛡️ PyGenAI Security Framework")
    click.echo("Version: 1.0.0 (Minimal)")
    click.echo("Status: ✅ Running")
    click.echo("Features: Basic scanning available")

class BasicVulnerability:
    def __init__(self, title, file_path, line_number, severity="MEDIUM"):
        self.title = title
        self.file_path = str(file_path)
        self.line_number = line_number
        self.severity = severity
        self.description = title

def basic_security_scan(file_path, content):
    """Basic security scanning without full framework"""
    vulnerabilities = []
    lines = content.split('\n')
    
    # Basic patterns to check
    security_patterns = {
        'SQL Injection Risk': [
            r'f"SELECT.*{',
            r"f'SELECT.*{",
            r'execute\(.*format\(',
            r'cursor\.execute\(.*%'
        ],
        'Hardcoded Secret': [
            r'password\s*=\s*["'][^"']{8,}["']',
            r'api_key\s*=\s*["'][^"']{10,}["']',
            r'secret\s*=\s*["'][^"']{8,}["']',
            r'token\s*=\s*["'][^"']{10,}["']'
        ],
        'Command Injection Risk': [
            r'subprocess\.(run|call|Popen).*shell\s*=\s*True',
            r'os\.system\(',
            r'os\.popen\('
        ],
        'Insecure Random': [
            r'random\.random\(\)',
            r'random\.choice\(',
            r'random\.randint\('
        ]
    }
    
    import re
    
    for line_num, line in enumerate(lines, 1):
        for vuln_type, patterns in security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(
                        BasicVulnerability(
                            title=vuln_type,
                            file_path=file_path,
                            line_number=line_num,
                            severity="HIGH" if "injection" in vuln_type.lower() else "MEDIUM"
                        )
                    )
                    break
    
    return vulnerabilities

def display_text_results(vulnerabilities, files_scanned):
    """Display scan results in text format"""
    click.echo()
    click.echo("=" * 60)
    click.echo("🎯 PYGENAI SECURITY SCAN RESULTS")
    click.echo("=" * 60)
    
    click.echo(f"📊 Files Scanned: {files_scanned}")
    click.echo(f"🚨 Vulnerabilities Found: {len(vulnerabilities)}")
    
    if vulnerabilities:
        click.echo()
        click.echo("🔍 Security Issues Found:")
        
        for i, vuln in enumerate(vulnerabilities, 1):
            severity_icon = "🔴" if vuln.severity == "HIGH" else "🟡"
            click.echo(f"  {i}. {severity_icon} {vuln.title}")
            click.echo(f"     File: {vuln.file_path}:{vuln.line_number}")
            click.echo()
    
    click.echo("💡 Note: This is a basic scan. Install full PyGenAI for comprehensive analysis.")

if __name__ == '__main__':
    cli()
