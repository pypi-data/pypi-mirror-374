"""
Dependency Security Scanner for PyGenAI Security Framework
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from ..core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory

class DependencyScanner:
    """Scans dependencies for known vulnerabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'known_vulnerabilities', 'outdated_packages'
        ])
        
        # Mock vulnerability database
        self.vulnerability_db = {
            'requests': {
                '2.25.1': {'cve': 'CVE-2021-33503', 'severity': ThreatLevel.HIGH},
                '2.24.0': {'cve': 'CVE-2021-33503', 'severity': ThreatLevel.MEDIUM}
            },
            'flask': {
                '1.1.4': {'cve': 'CVE-2023-30861', 'severity': ThreatLevel.HIGH}
            },
            'django': {
                '3.1.0': {'cve': 'CVE-2021-35042', 'severity': ThreatLevel.CRITICAL}
            }
        }
    
    def scan_files(self, files: List[Path]) -> List[Vulnerability]:
        """Scan dependency files"""
        vulnerabilities = []
        for file_path in files:
            if self._is_dependency_file(file_path):
                vulnerabilities.extend(self.scan_file(file_path))
        return vulnerabilities
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan single dependency file"""
        if not self._is_dependency_file(file_path):
            return []
        
        vulnerabilities = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            dependencies = self._parse_requirements(content)
            
            for line_num, dep_info in dependencies:
                package_name = dep_info.get('name')
                version = dep_info.get('version')
                
                if package_name in self.vulnerability_db and version:
                    if version in self.vulnerability_db[package_name]:
                        vuln_info = self.vulnerability_db[package_name][version]
                        
                        vulnerabilities.append(Vulnerability(
                            title=f"Known Vulnerability in {package_name}",
                            description=f"{package_name} {version} has known vulnerability: {vuln_info['cve']}",
                            threat_level=vuln_info['severity'],
                            category=VulnerabilityCategory.VULNERABLE_COMPONENTS,
                            file_path=str(file_path),
                            line_number=line_num,
                            code_snippet=f"{package_name}=={version}",
                            remediation=f"Update {package_name} to a secure version",
                            scanner_name="dependency_scanner"
                        ))
        
        except Exception:
            pass
        
        return vulnerabilities
    
    def _is_dependency_file(self, file_path: Path) -> bool:
        """Check if file is a dependency specification file"""
        return file_path.name in [
            'requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py'
        ]
    
    def _parse_requirements(self, content: str) -> List[tuple]:
        """Parse requirements.txt format"""
        dependencies = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Simple parsing for package==version format
            match = re.match(r'^([a-zA-Z0-9_.-]+)\s*==\s*([0-9.]+)', line)
            if match:
                dependencies.append((line_num, {
                    'name': match.group(1),
                    'version': match.group(2)
                }))
        
        return dependencies
