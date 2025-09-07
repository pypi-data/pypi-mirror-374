"""
Traditional Python Security Scanner
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from ..core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory

class TraditionalPythonScanner:
    """Scans for traditional Python security vulnerabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'sql_injection', 'command_injection', 'hardcoded_secrets', 'xss'
        ])
    
    def scan_files(self, files: List[Path]) -> List[Vulnerability]:
        """Scan multiple Python files"""
        vulnerabilities = []
        for file_path in files:
            if file_path.suffix == '.py':
                vulnerabilities.extend(self.scan_file(file_path))
        return vulnerabilities
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan single Python file"""
        if file_path.suffix != '.py':
            return []
        
        vulnerabilities = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # SQL Injection patterns
                if 'sql_injection' in self.enabled_rules:
                    sql_patterns = [
                        r'f"SELECT.*{', r"f'SELECT.*{",
                        r'execute\(.*format\(', r'cursor\.execute\(.*%'
                    ]
                    for pattern in sql_patterns:
                        if re.search(pattern, line):
                            vulnerabilities.append(Vulnerability(
                                title="Potential SQL Injection",
                                description="SQL query construction may be vulnerable to injection",
                                threat_level=ThreatLevel.HIGH,
                                category=VulnerabilityCategory.INJECTION,
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line,
                                remediation="Use parameterized queries or ORM methods",
                                scanner_name="traditional_python",
                                cvss_score=8.1
                            ))
                            break
                
                # Command Injection patterns
                if 'command_injection' in self.enabled_rules:
                    cmd_patterns = [
                        r'subprocess\.(run|call|Popen).*shell\s*=\s*True',
                        r'os\.system\(', r'os\.popen\('
                    ]
                    for pattern in cmd_patterns:
                        if re.search(pattern, line):
                            vulnerabilities.append(Vulnerability(
                                title="Command Injection Risk",
                                description="Command execution with user input may allow injection",
                                threat_level=ThreatLevel.HIGH,
                                category=VulnerabilityCategory.INJECTION,
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line,
                                remediation="Validate input and use subprocess with list arguments",
                                scanner_name="traditional_python",
                                cvss_score=7.8
                            ))
                            break
                
                # Hardcoded secrets
                if 'hardcoded_secrets' in self.enabled_rules:
                    secret_patterns = [
                        r'password\s*=\s*[""][^""]{8,}[""]',
                        r'api_key\s*=\s*[""][^""]{10,}[""]',
                        r'secret\s*=\s*[""][^""]{8,}[""]',
                        r'token\s*=\s*[""][^""]{10,}[""]'
                    ]
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append(Vulnerability(
                                title="Hardcoded Secret",
                                description="Sensitive credential hardcoded in source code",
                                threat_level=ThreatLevel.CRITICAL,
                                category=VulnerabilityCategory.SECRETS_MANAGEMENT,
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line,
                                remediation="Move secrets to environment variables or secure storage",
                                scanner_name="traditional_python",
                                cvss_score=9.1
                            ))
                            break
        
        except Exception:
            pass
        
        return vulnerabilities
