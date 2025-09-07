"""
Configuration Security Scanner for PyGenAI Security Framework
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from ..core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory

class ConfigurationScanner:
    """Scans configuration files for security issues"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'debug_enabled', 'weak_secrets', 'insecure_defaults'
        ])
    
    def scan_files(self, files: List[Path]) -> List[Vulnerability]:
        """Scan multiple files"""
        vulnerabilities = []
        for file_path in files:
            if self._is_config_file(file_path):
                vulnerabilities.extend(self.scan_file(file_path))
        return vulnerabilities
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan single configuration file"""
        if not self._is_config_file(file_path):
            return []
        
        vulnerabilities = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for debug mode
                if re.search(r'DEBUG\s*=\s*True', line, re.IGNORECASE):
                    vulnerabilities.append(Vulnerability(
                        title="Debug Mode Enabled",
                        description="Debug mode should be disabled in production",
                        threat_level=ThreatLevel.HIGH,
                        category=VulnerabilityCategory.SECURITY_MISCONFIG,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line,
                        remediation="Set DEBUG = False in production",
                        scanner_name="configuration_scanner"
                    ))
                
                # Check for weak secrets
                if re.search(r'(password|secret|key)\s*=\s*[""]?(test|dev|123|password)[""]?', line, re.IGNORECASE):
                    vulnerabilities.append(Vulnerability(
                        title="Weak Secret Configuration",
                        description="Weak or default secret detected in configuration",
                        threat_level=ThreatLevel.CRITICAL,
                        category=VulnerabilityCategory.SECRETS_MANAGEMENT,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line,
                        remediation="Use strong, randomly generated secrets",
                        scanner_name="configuration_scanner"
                    ))
        
        except Exception:
            pass
        
        return vulnerabilities
    
    def _is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration file"""
        config_patterns = [
            r'config\.py$', r'settings\.py$', r'\.env$',
            r'\.ya?ml$', r'\.json$', r'\.ini$', r'\.cfg$'
        ]
        
        filename = file_path.name
        return any(re.search(pattern, filename, re.IGNORECASE) for pattern in config_patterns)
