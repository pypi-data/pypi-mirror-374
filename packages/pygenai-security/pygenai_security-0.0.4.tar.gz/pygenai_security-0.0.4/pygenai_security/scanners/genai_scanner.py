"""
GenAI Security Scanner for PyGenAI Security Framework
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from ..core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory

class GenAISecurityScanner:
    """Scans for GenAI/LLM specific security vulnerabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'prompt_injection', 'data_leakage', 'model_manipulation'
        ])
    
    def scan_files(self, files: List[Path]) -> List[Vulnerability]:
        """Scan multiple files for GenAI vulnerabilities"""
        vulnerabilities = []
        for file_path in files:
            if self._is_genai_related_file(file_path):
                vulnerabilities.extend(self.scan_file(file_path))
        return vulnerabilities
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan single file for GenAI vulnerabilities"""
        vulnerabilities = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            if not self._contains_genai_code(content):
                return []
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Prompt Injection patterns
                if 'prompt_injection' in self.enabled_rules:
                    prompt_patterns = [
                        r'f".*{.*user.*}.*"',  # f-string with user input
                        r'prompt.*\+.*user',   # String concatenation with user input
                        r'\.format\(.*user'    # .format() with user input
                    ]
                    for pattern in prompt_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append(Vulnerability(
                                title="Prompt Injection Vulnerability",
                                description="User input directly concatenated into AI prompt without validation",
                                threat_level=ThreatLevel.HIGH,
                                category=VulnerabilityCategory.GENAI_PROMPT_INJECTION,
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line,
                                remediation="Sanitize and validate user input before including in prompts",
                                scanner_name="genai_security",
                                cvss_score=7.5
                            ))
                            break
                
                # Data Leakage patterns
                if 'data_leakage' in self.enabled_rules:
                    leakage_patterns = [
                        r'print\(.*sensitive',
                        r'log.*\(.*user.*data',
                        r'requests\.post\(.*data.*=.*user'
                    ]
                    for pattern in leakage_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append(Vulnerability(
                                title="Potential Data Leakage",
                                description="Sensitive data may be exposed through logging or external calls",
                                threat_level=ThreatLevel.MEDIUM,
                                category=VulnerabilityCategory.GENAI_DATA_LEAKAGE,
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line,
                                remediation="Sanitize data before logging or sending to external services",
                                scanner_name="genai_security",
                                cvss_score=6.2
                            ))
                            break
        
        except Exception:
            pass
        
        return vulnerabilities
    
    def _is_genai_related_file(self, file_path: Path) -> bool:
        """Check if file contains GenAI/LLM related code"""
        if file_path.suffix != '.py':
            return False
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self._contains_genai_code(content)
        except:
            return False
    
    def _contains_genai_code(self, content: str) -> bool:
        """Check if content contains GenAI/LLM related imports or patterns"""
        genai_patterns = [
            'import openai', 'from openai',
            'import anthropic', 'from anthropic',
            'import langchain', 'from langchain',
            'import transformers', 'from transformers',
            'ChatCompletion', 'GPT', 'claude', 'llama'
        ]
        
        content_lower = content.lower()
        return any(pattern.lower() in content_lower for pattern in genai_patterns)
