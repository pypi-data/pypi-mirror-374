"""
Traditional Python Security Scanner
Detects common Python security vulnerabilities using AST analysis and pattern matching.
"""

import ast
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from ..core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TraditionalPythonScanner:
    """
    Traditional Python security scanner using AST analysis and pattern matching
    
    Detects common vulnerabilities such as:
    - SQL Injection
    - Command Injection  
    - Cross-Site Scripting (XSS)
    - Path Traversal
    - Hardcoded Secrets
    - Insecure Random Number Generation
    - Weak Cryptography
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'sql_injection', 'command_injection', 'xss', 'path_traversal',
            'hardcoded_secrets', 'weak_crypto', 'insecure_random'
        ])
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.logger = get_logger(f'{__name__}.TraditionalPythonScanner')
    
    def scan_files(self, files: List[Path]) -> List[Vulnerability]:
        """Scan multiple files for traditional Python security issues"""
        vulnerabilities = []
        
        for file_path in files:
            try:
                file_vulnerabilities = self.scan_file(file_path)
                vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"Error scanning file {file_path}: {e}")
        
        return vulnerabilities
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan single file for security vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST for advanced analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                ast_vulnerabilities = self._analyze_ast(tree, file_path, content)
                vulnerabilities.extend(ast_vulnerabilities)
            except SyntaxError as e:
                self.logger.debug(f"Syntax error in {file_path}, skipping AST analysis: {e}")
            
            # Pattern-based analysis
            lines = content.split('\n')
            pattern_vulnerabilities = self._analyze_patterns(lines, file_path, content)
            vulnerabilities.extend(pattern_vulnerabilities)
            
        except Exception as e:
            self.logger.error(f"Error scanning file {file_path}: {e}")
        
        return vulnerabilities
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, content: str) -> List[Vulnerability]:
        """Analyze AST for security vulnerabilities"""
        vulnerabilities = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, scanner, file_path, content):
                self.scanner = scanner
                self.file_path = file_path
                self.content = content
                self.lines = content.split('\n')
                self.vulnerabilities = []
            
            def visit_Call(self, node):
                """Analyze function calls for security issues"""
                try:
                    # SQL Injection detection
                    if self.scanner._is_enabled('sql_injection'):
                        self._check_sql_injection(node)
                    
                    # Command Injection detection
                    if self.scanner._is_enabled('command_injection'):
                        self._check_command_injection(node)
                    
                    # Weak cryptography detection
                    if self.scanner._is_enabled('weak_crypto'):
                        self._check_weak_crypto(node)
                    
                    # Insecure random detection
                    if self.scanner._is_enabled('insecure_random'):
                        self._check_insecure_random(node)
                
                except Exception as e:
                    logger.debug(f"Error analyzing call node: {e}")
                
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                """Analyze assignments for hardcoded secrets"""
                try:
                    if self.scanner._is_enabled('hardcoded_secrets'):
                        self._check_hardcoded_secrets(node)
                except Exception as e:
                    logger.debug(f"Error analyzing assignment node: {e}")
                
                self.generic_visit(node)
            
            def _check_sql_injection(self, node):
                """Check for SQL injection vulnerabilities"""
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr
                    
                    # Check for dangerous SQL methods with string concatenation
                    if method_name in ['execute', 'executemany', 'raw']:
                        for arg in node.args:
                            if self._has_string_concatenation(arg):
                                line_num = getattr(node, 'lineno', 1)
                                code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                                
                                vuln = Vulnerability(
                                    title="SQL Injection Vulnerability",
                                    description="Dynamic SQL query construction detected. This may allow SQL injection attacks.",
                                    threat_level=ThreatLevel.HIGH,
                                    category=VulnerabilityCategory.INJECTION,
                                    file_path=str(self.file_path),
                                    line_number=line_num,
                                    code_snippet=code_snippet.strip(),
                                    remediation="Use parameterized queries or prepared statements instead of string concatenation",
                                    remediation_examples=[
                                        "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                                        "Use SQLAlchemy ORM with proper parameter binding"
                                    ],
                                    business_impact="Could allow attackers to access, modify, or delete database data",
                                    technical_impact="Database compromise, data exfiltration, privilege escalation",
                                    cvss_score=8.1,
                                    cwe_id="CWE-89",
                                    owasp_category="A03:2021 � Injection",
                                    confidence=0.85,
                                    scanner_name="traditional_python",
                                    scan_rule_id="SQL_INJECTION_001"
                                )
                                self.vulnerabilities.append(vuln)
            
            def _check_command_injection(self, node):
                """Check for command injection vulnerabilities"""
                dangerous_functions = [
                    'system', 'popen', 'call', 'run', 'Popen', 'check_call', 
                    'check_output', 'getstatusoutput', 'getoutput'
                ]
                
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name in dangerous_functions:
                    # Check for shell=True with user input
                    has_shell_true = False
                    has_user_input = False
                    
                    for keyword in node.keywords:
                        if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                            if keyword.value.value is True:
                                has_shell_true = True
                    
                    # Check if arguments contain string concatenation or variables
                    for arg in node.args:
                        if self._has_string_concatenation(arg) or isinstance(arg, ast.Name):
                            has_user_input = True
                    
                    if has_shell_true or func_name in ['system', 'popen']:
                        line_num = getattr(node, 'lineno', 1)
                        code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                        
                        threat_level = ThreatLevel.CRITICAL if has_shell_true else ThreatLevel.HIGH
                        
                        vuln = Vulnerability(
                            title="Command Injection Vulnerability",
                            description="Dynamic command execution detected. This may allow command injection attacks.",
                            threat_level=threat_level,
                            category=VulnerabilityCategory.INJECTION,
                            file_path=str(self.file_path),
                            line_number=line_num,
                            code_snippet=code_snippet.strip(),
                            remediation="Use subprocess with shell=False and validate all inputs, or use safer alternatives",
                            remediation_examples=[
                                "subprocess.run(['ls', directory], check=True)",
                                "Use shlex.quote() for shell arguments",
                                "Avoid shell=True parameter"
                            ],
                            business_impact="Could allow attackers to execute arbitrary system commands",
                            technical_impact="Complete system compromise, data theft, malware installation",
                            cvss_score=9.8 if has_shell_true else 7.5,
                            cwe_id="CWE-78",
                            owasp_category="A03:2021 � Injection",
                            confidence=0.9 if has_shell_true else 0.75,
                            scanner_name="traditional_python",
                            scan_rule_id="COMMAND_INJECTION_001"
                        )
                        self.vulnerabilities.append(vuln)
            
            def _check_weak_crypto(self, node):
                """Check for weak cryptographic practices"""
                weak_crypto_functions = {
                    'md5': ('MD5 hash function is cryptographically broken', 8.1),
                    'sha1': ('SHA1 hash function is deprecated and weak', 6.5),
                    'des': ('DES encryption is extremely weak', 9.0),
                    'rc4': ('RC4 cipher is broken and should not be used', 8.5)
                }
                
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr.lower()
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id.lower()
                
                for weak_func, (description, cvss) in weak_crypto_functions.items():
                    if weak_func in func_name:
                        line_num = getattr(node, 'lineno', 1)
                        code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                        
                        vuln = Vulnerability(
                            title=f"Weak Cryptography: {weak_func.upper()}",
                            description=description + ". Use stronger cryptographic algorithms.",
                            threat_level=ThreatLevel.HIGH if cvss >= 8.0 else ThreatLevel.MEDIUM,
                            category=VulnerabilityCategory.CRYPTOGRAPHIC_FAILURES,
                            file_path=str(self.file_path),
                            line_number=line_num,
                            code_snippet=code_snippet.strip(),
                            remediation=f"Replace {weak_func.upper()} with SHA-256, SHA-3, or other secure algorithms",
                            remediation_examples=[
                                "Use hashlib.sha256() instead of md5()",
                                "Use AES encryption instead of DES/RC4",
                                "Consider bcrypt or Argon2 for password hashing"
                            ],
                            business_impact="Weak cryptography may be broken by attackers",
                            cvss_score=cvss,
                            cwe_id="CWE-327",
                            owasp_category="A02:2021 � Cryptographic Failures",
                            confidence=0.9,
                            scanner_name="traditional_python",
                            scan_rule_id=f"WEAK_CRYPTO_{weak_func.upper()}"
                        )
                        self.vulnerabilities.append(vuln)
            
            def _check_insecure_random(self, node):
                """Check for insecure random number generation"""
                if isinstance(node.func, ast.Attribute):
                    if (hasattr(node.func.value, 'id') and 
                        node.func.value.id == 'random' and
                        node.func.attr in ['random', 'randint', 'choice', 'shuffle']):
                        
                        line_num = getattr(node, 'lineno', 1)
                        code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                        
                        vuln = Vulnerability(
                            title="Insecure Random Number Generation",
                            description="Use of predictable random number generator for security-sensitive operations",
                            threat_level=ThreatLevel.MEDIUM,
                            category=VulnerabilityCategory.CRYPTOGRAPHIC_FAILURES,
                            file_path=str(self.file_path),
                            line_number=line_num,
                            code_snippet=code_snippet.strip(),
                            remediation="Use secrets module for cryptographically secure random numbers",
                            remediation_examples=[
                                "import secrets; secrets.randbelow(10)",
                                "secrets.token_hex(16) for random tokens",
                                "os.urandom() for random bytes"
                            ],
                            business_impact="Predictable random numbers may be exploited by attackers",
                            cvss_score=5.3,
                            cwe_id="CWE-338",
                            owasp_category="A02:2021 � Cryptographic Failures",
                            confidence=0.8,
                            scanner_name="traditional_python",
                            scan_rule_id="INSECURE_RANDOM_001"
                        )
                        self.vulnerabilities.append(vuln)
            
            def _check_hardcoded_secrets(self, node):
                """Check for hardcoded secrets in assignments"""
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        # Check for secret-like variable names
                        secret_patterns = [
                            'password', 'passwd', 'pwd', 'secret', 'key', 'token', 
                            'api_key', 'apikey', 'private_key', 'auth_token'
                        ]
                        
                        if any(pattern in var_name for pattern in secret_patterns):
                            # Check if assigned a string literal
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                secret_value = node.value.value
                                
                                # Skip obvious dummy values
                                if (len(secret_value) >= 8 and 
                                    secret_value not in ['password', 'secret', 'change_me', 'todo'] and
                                    not secret_value.startswith('${') and
                                    not secret_value.startswith('$(')):
                                    
                                    line_num = getattr(node, 'lineno', 1)
                                    code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                                    
                                    vuln = Vulnerability(
                                        title=f"Hardcoded Secret: {var_name}",
                                        description=f"Hardcoded {var_name} detected in source code",
                                        threat_level=ThreatLevel.CRITICAL,
                                        category=VulnerabilityCategory.SECRETS_MANAGEMENT,
                                        file_path=str(self.file_path),
                                        line_number=line_num,
                                        code_snippet=code_snippet.strip(),
                                        remediation=f"Move {var_name} to environment variables or secure configuration",
                                        remediation_examples=[
                                            f"{var_name} = os.environ.get('{var_name.upper()}')",
                                            "Use Azure Key Vault, AWS Secrets Manager, or similar",
                                            "Implement proper secrets rotation"
                                        ],
                                        business_impact="Hardcoded secrets can be easily discovered and misused",
                                        technical_impact="Unauthorized access to services, data breaches",
                                        cvss_score=9.1,
                                        cwe_id="CWE-798",
                                        owasp_category="A02:2021 � Cryptographic Failures",
                                        confidence=0.95,
                                        scanner_name="traditional_python",
                                        scan_rule_id="HARDCODED_SECRET_001"
                                    )
                                    self.vulnerabilities.append(vuln)
            
            def _has_string_concatenation(self, node):
                """Check if node contains string concatenation"""
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                    return True
                elif isinstance(node, ast.JoinedStr):  # f-strings
                    return True
                elif isinstance(node, ast.Call):
                    # Check for .format() or % formatting
                    if isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
                        return True
                return False
        
        visitor = SecurityVisitor(self, file_path, content)
        visitor.visit(tree)
        vulnerabilities.extend(visitor.vulnerabilities)
        
        return vulnerabilities
    
    def _analyze_patterns(self, lines: List[str], file_path: Path, content: str) -> List[Vulnerability]:
        """Analyze content using pattern matching"""
        vulnerabilities = []
        
        for line_num, line in enumerate(lines, 1):
            line_vulnerabilities = []
            
            # XSS detection
            if self._is_enabled('xss'):
                line_vulnerabilities.extend(self._check_xss_patterns(line, line_num, file_path))
            
            # Path traversal detection
            if self._is_enabled('path_traversal'):
                line_vulnerabilities.extend(self._check_path_traversal_patterns(line, line_num, file_path))
            
            vulnerabilities.extend(line_vulnerabilities)
        
        return vulnerabilities
    
    def _check_xss_patterns(self, line: str, line_num: int, file_path: Path) -> List[Vulnerability]:
        """Check for XSS vulnerability patterns"""
        vulnerabilities = []
        
        xss_patterns = [
            r'render_template\s*\([^)]*\+[^)]*\)',
            r'return\s+[""][^""]*[""]\s*\+',
            r'innerHTML\s*=\s*[^;]*\+',
            r'document\.write\s*\([^)]*\+[^)]*\)'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                vuln = Vulnerability(
                    title="Cross-Site Scripting (XSS) Vulnerability",
                    description="Dynamic content generation without proper output encoding detected",
                    threat_level=ThreatLevel.MEDIUM,
                    category=VulnerabilityCategory.INJECTION,
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line.strip(),
                    remediation="Use proper output encoding and Content Security Policy (CSP)",
                    remediation_examples=[
                        "Use html.escape() for HTML contexts",
                        "Use template engines with auto-escaping",
                        "Implement Content Security Policy headers"
                    ],
                    business_impact="Could allow attackers to execute malicious scripts in user browsers",
                    cvss_score=6.1,
                    cwe_id="CWE-79",
                    owasp_category="A03:2021 � Injection",
                    confidence=0.75,
                    scanner_name="traditional_python",
                    scan_rule_id="XSS_PATTERN_001"
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _check_path_traversal_patterns(self, line: str, line_num: int, file_path: Path) -> List[Vulnerability]:
        """Check for path traversal vulnerability patterns"""
        vulnerabilities = []
        
        path_patterns = [
            r'open\s*\([^)]*\+[^)]*\.\./[^)]*\)',
            r'Path\s*\([^)]*\+[^)]*\)',
            r'os\.path\.join\s*\([^)]*\+[^)]*\)',
            r'file\s*=\s*[^;]*\+[^;]*\.\./[^;]*'
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                vuln = Vulnerability(
                    title="Path Traversal Vulnerability",
                    description="Dynamic file path construction may allow directory traversal attacks",
                    threat_level=ThreatLevel.HIGH,
                    category=VulnerabilityCategory.BROKEN_ACCESS_CONTROL,
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line.strip(),
                    remediation="Validate and sanitize file paths, use os.path.abspath() and whitelist allowed directories",
                    remediation_examples=[
                        "Use os.path.realpath() and validate against allowed directories",
                        "Implement file extension whitelist",
                        "Use secure path joining methods"
                    ],
                    business_impact="Could allow access to sensitive files outside intended directories",
                    cvss_score=7.5,
                    cwe_id="CWE-22",
                    owasp_category="A01:2021 � Broken Access Control",
                    confidence=0.8,
                    scanner_name="traditional_python",
                    scan_rule_id="PATH_TRAVERSAL_001"
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _is_enabled(self, rule_name: str) -> bool:
        """Check if specific rule is enabled"""
        return rule_name in self.enabled_rules
    
    def configure(self, config: Dict[str, Any]):
        """Configure scanner with new settings"""
        self.config.update(config)
        
        # Update enabled rules if provided
        if 'rules' in config:
            self.enabled_rules = config['rules']
        
        # Update confidence threshold
        if 'confidence_threshold' in config:
            self.confidence_threshold = config['confidence_threshold']
