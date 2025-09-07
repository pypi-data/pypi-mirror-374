"""
GenAI Security Scanner for PyGenAI Security Framework
Specialized scanner for GenAI/LLM security vulnerabilities including prompt injection,
data leakage, model manipulation, and AI ethics issues.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import json

from ..core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GenAISecurityScanner:
    """
    Specialized security scanner for GenAI/LLM applications
    
    Detects GenAI-specific vulnerabilities:
    - Prompt Injection attacks
    - Data leakage in AI contexts
    - Model manipulation and theft
    - Bias and discrimination issues
    - Privacy violations in AI processing
    - Training data poisoning indicators
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'prompt_injection', 'data_leakage', 'model_manipulation', 
            'bias_detection', 'privacy_violation', 'training_data_exposure'
        ])
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.logger = get_logger(f'{__name__}.GenAISecurityScanner')
        
        # GenAI framework patterns for detection
        self.genai_frameworks = {
            'openai': ['openai', 'ChatOpenAI', 'GPT', 'gpt-', 'text-davinci', 'text-ada', 'text-babbage'],
            'anthropic': ['anthropic', 'claude', 'Claude', 'claude-'],
            'huggingface': ['transformers', 'AutoModel', 'AutoTokenizer', 'pipeline', 'huggingface'],
            'langchain': ['langchain', 'LangChain', 'LLMChain', 'ConversationChain'],
            'llamaindex': ['llama_index', 'GPTIndex', 'LlamaIndex', 'SimpleDirectoryReader'],
            'cohere': ['cohere', 'co.generate', 'co.embed'],
            'ai21': ['ai21', 'j1-', 'j2-'],
            'google': ['palm', 'bard', 'vertex', 'google.generativeai']
        }
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'
        }
    
    def scan_files(self, files: List[Path]) -> List[Vulnerability]:
        """Scan multiple files for GenAI security issues"""
        vulnerabilities = []
        
        for file_path in files:
            try:
                if self._is_genai_related_file(file_path):
                    file_vulnerabilities = self.scan_file(file_path)
                    vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"Error scanning GenAI file {file_path}: {e}")
        
        return vulnerabilities
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan single file for GenAI security vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Only scan files that contain GenAI-related code
            if not self._contains_genai_code(content):
                return vulnerabilities
            
            lines = content.split('\n')
            
            # AST-based analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                ast_vulnerabilities = self._analyze_genai_ast(tree, file_path, content, lines)
                vulnerabilities.extend(ast_vulnerabilities)
            except SyntaxError:
                self.logger.debug(f"Syntax error in {file_path}, skipping AST analysis")
            
            # Pattern-based analysis
            pattern_vulnerabilities = self._analyze_genai_patterns(lines, file_path, content)
            vulnerabilities.extend(pattern_vulnerabilities)
            
        except Exception as e:
            self.logger.error(f"Error scanning GenAI file {file_path}: {e}")
        
        return vulnerabilities
    
    def _is_genai_related_file(self, file_path: Path) -> bool:
        """Quick check if file might contain GenAI-related code"""
        try:
            # Check filename for GenAI indicators
            filename_lower = file_path.name.lower()
            genai_indicators = ['ai', 'llm', 'gpt', 'chat', 'model', 'openai', 'anthropic', 'langchain']
            
            if any(indicator in filename_lower for indicator in genai_indicators):
                return True
            
            # Check first few lines for imports
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = ''.join(f.readlines()[:20]).lower()
                
                for framework_patterns in self.genai_frameworks.values():
                    if any(pattern.lower() in first_lines for pattern in framework_patterns):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _contains_genai_code(self, content: str) -> bool:
        """Check if content contains GenAI-related code"""
        content_lower = content.lower()
        
        for framework_patterns in self.genai_frameworks.values():
            if any(pattern.lower() in content_lower for pattern in framework_patterns):
                return True
        
        return False
    
    def _analyze_genai_ast(self, tree: ast.AST, file_path: Path, content: str, lines: List[str]) -> List[Vulnerability]:
        """Analyze AST for GenAI security vulnerabilities"""
        vulnerabilities = []
        
        class GenAISecurityVisitor(ast.NodeVisitor):
            def __init__(self, scanner, file_path, content, lines):
                self.scanner = scanner
                self.file_path = file_path
                self.content = content
                self.lines = lines
                self.vulnerabilities = []
                self.current_function = None
                self.genai_api_calls = []
            
            def visit_FunctionDef(self, node):
                """Track current function for context"""
                old_function = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = old_function
            
            def visit_Call(self, node):
                """Analyze function calls for GenAI security issues"""
                try:
                    # Prompt injection detection
                    if self.scanner._is_enabled('prompt_injection'):
                        self._check_prompt_injection(node)
                    
                    # Data leakage detection
                    if self.scanner._is_enabled('data_leakage'):
                        self._check_data_leakage(node)
                    
                    # Model manipulation detection
                    if self.scanner._is_enabled('model_manipulation'):
                        self._check_model_manipulation(node)
                    
                    # Track GenAI API calls for context
                    self._track_genai_api_calls(node)
                
                except Exception as e:
                    logger.debug(f"Error analyzing GenAI call node: {e}")
                
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                """Analyze assignments for GenAI security issues"""
                try:
                    if self.scanner._is_enabled('data_leakage'):
                        self._check_sensitive_data_assignment(node)
                    
                    if self.scanner._is_enabled('model_manipulation'):
                        self._check_model_parameter_assignment(node)
                
                except Exception as e:
                    logger.debug(f"Error analyzing GenAI assignment: {e}")
                
                self.generic_visit(node)
            
            def _check_prompt_injection(self, node):
                """Check for prompt injection vulnerabilities"""
                # Look for dangerous prompt construction patterns
                if self._is_genai_api_call(node):
                    for arg in node.args + [kw.value for kw in node.keywords]:
                        if self._has_unsafe_prompt_construction(arg):
                            line_num = getattr(node, 'lineno', 1)
                            code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                            
                            # Determine severity based on pattern
                            threat_level = self._assess_prompt_injection_severity(arg, code_snippet)
                            
                            vuln = Vulnerability(
                                title="Prompt Injection Vulnerability",
                                description="Unsafe prompt construction with user input that may be vulnerable to prompt injection attacks",
                                threat_level=threat_level,
                                category=VulnerabilityCategory.GENAI_PROMPT_INJECTION,
                                file_path=str(self.file_path),
                                line_number=line_num,
                                code_snippet=code_snippet.strip(),
                                remediation="Implement input validation, prompt templates, and user input sanitization",
                                remediation_examples=[
                                    "Use structured prompts with clear delimiters",
                                    "Sanitize user input before including in prompts",
                                    "Implement prompt injection detection filters",
                                    "Use system/user message separation in chat APIs"
                                ],
                                business_impact="Could allow attackers to manipulate AI behavior and extract sensitive information",
                                technical_impact="AI model manipulation, unauthorized data access, system prompt extraction",
                                cvss_score=7.3 if threat_level == ThreatLevel.HIGH else 5.5,
                                cwe_id="CWE-74",
                                confidence=0.85,
                                scanner_name="genai_security",
                                scan_rule_id="PROMPT_INJECTION_001",
                                compliance_mappings=["AI_ETHICS", "GDPR"]
                            )
                            self.vulnerabilities.append(vuln)
            
            def _check_data_leakage(self, node):
                """Check for potential data leakage in GenAI contexts"""
                # Check for logging or printing of GenAI responses
                if isinstance(node.func, ast.Name) and node.func.id in ['print', 'log']:
                    for arg in node.args:
                        if self._contains_genai_response_reference(arg):
                            line_num = getattr(node, 'lineno', 1)
                            code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                            
                            vuln = Vulnerability(
                                title="Potential Data Leakage in GenAI Context",
                                description="GenAI model responses may contain sensitive data being logged or printed",
                                threat_level=ThreatLevel.MEDIUM,
                                category=VulnerabilityCategory.GENAI_DATA_LEAKAGE,
                                file_path=str(self.file_path),
                                line_number=line_num,
                                code_snippet=code_snippet.strip(),
                                remediation="Sanitize GenAI responses before logging and implement data loss prevention",
                                remediation_examples=[
                                    "Filter sensitive data from logs",
                                    "Use structured logging with field filtering",
                                    "Implement data anonymization for GenAI outputs"
                                ],
                                business_impact="Could expose sensitive user or business data through GenAI interactions",
                                cvss_score=6.5,
                                cwe_id="CWE-200",
                                confidence=0.75,
                                scanner_name="genai_security",
                                scan_rule_id="DATA_LEAKAGE_001",
                                compliance_mappings=["GDPR", "HIPAA", "PCI_DSS"]
                            )
                            self.vulnerabilities.append(vuln)
            
            def _check_model_manipulation(self, node):
                """Check for model manipulation vulnerabilities"""
                if self._is_genai_api_call(node):
                    # Check for user-controlled model parameters
                    dangerous_params = ['model', 'engine', 'temperature', 'max_tokens', 'top_p', 'frequency_penalty']
                    
                    for keyword in node.keywords:
                        if keyword.arg in dangerous_params:
                            if self._is_user_controlled_input(keyword.value):
                                line_num = getattr(node, 'lineno', 1)
                                code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                                
                                vuln = Vulnerability(
                                    title="Model Parameter Manipulation Vulnerability",
                                    description=f"User-controlled input affects model parameter '{keyword.arg}' without validation",
                                    threat_level=ThreatLevel.MEDIUM,
                                    category=VulnerabilityCategory.GENAI_MODEL_MANIPULATION,
                                    file_path=str(self.file_path),
                                    line_number=line_num,
                                    code_snippet=code_snippet.strip(),
                                    remediation="Validate and restrict model parameters to safe ranges",
                                    remediation_examples=[
                                        f"Validate {keyword.arg} parameter range and whitelist allowed values",
                                        "Use configuration-based parameter management",
                                        "Implement parameter sanitization and bounds checking"
                                    ],
                                    business_impact="Could allow unauthorized manipulation of AI model behavior",
                                    cvss_score=5.4,
                                    cwe_id="CWE-20",
                                    confidence=0.8,
                                    scanner_name="genai_security",
                                    scan_rule_id="MODEL_MANIPULATION_001"
                                )
                                self.vulnerabilities.append(vuln)
            
            def _check_sensitive_data_assignment(self, node):
                """Check for assignment of sensitive data to GenAI contexts"""
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        # Check if variable name suggests GenAI use
                        if any(word in var_name for word in ['prompt', 'query', 'input', 'message']):
                            # Check if assigned value contains sensitive patterns
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                for pattern_name, pattern in self.scanner.sensitive_patterns.items():
                                    if re.search(pattern, node.value.value):
                                        line_num = getattr(node, 'lineno', 1)
                                        code_snippet = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                                        
                                        vuln = Vulnerability(
                                            title=f"Sensitive Data in GenAI Context: {pattern_name}",
                                            description=f"Potential {pattern_name} data detected in GenAI-related variable",
                                            threat_level=ThreatLevel.HIGH,
                                            category=VulnerabilityCategory.GENAI_PRIVACY_VIOLATION,
                                            file_path=str(self.file_path),
                                            line_number=line_num,
                                            code_snippet=code_snippet.strip(),
                                            remediation="Remove or anonymize sensitive data before GenAI processing",
                                            remediation_examples=[
                                                "Implement data anonymization before AI processing",
                                                "Use data masking for sensitive information",
                                                "Apply privacy-preserving techniques"
                                            ],
                                            business_impact="Could expose sensitive personal or business data to AI models",
                                            cvss_score=7.5,
                                            cwe_id="CWE-200",
                                            confidence=0.85,
                                            scanner_name="genai_security",
                                            scan_rule_id=f"SENSITIVE_DATA_{pattern_name.upper()}",
                                            compliance_mappings=["GDPR", "HIPAA", "PCI_DSS"]
                                        )
                                        self.vulnerabilities.append(vuln)
            
            def _check_model_parameter_assignment(self, node):
                """Check for insecure model parameter assignments"""
                # Implementation for model parameter security checks
                pass
            
            def _is_genai_api_call(self, node):
                """Check if node represents a GenAI API call"""
                if isinstance(node.func, ast.Attribute):
                    # Check method name patterns
                    method_name = node.func.attr.lower()
                    genai_methods = [
                        'create', 'generate', 'complete', 'chat', 'embed',
                        'search', 'classify', 'summarize', 'translate'
                    ]
                    
                    if any(method in method_name for method in genai_methods):
                        return True
                    
                    # Check object name patterns
                    if hasattr(node.func.value, 'id'):
                        obj_name = node.func.value.id.lower()
                        if any(framework in obj_name for framework_patterns in self.scanner.genai_frameworks.values() for framework in framework_patterns):
                            return True
                
                return False
            
            def _has_unsafe_prompt_construction(self, node):
                """Check if node contains unsafe prompt construction"""
                # String concatenation with user input
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                    return True
                
                # f-string with variables
                if isinstance(node, ast.JoinedStr):
                    return True
                
                # .format() calls
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'format':
                        return True
                
                return False
            
            def _assess_prompt_injection_severity(self, node, code_snippet):
                """Assess severity of prompt injection vulnerability"""
                # High severity indicators
                high_severity_patterns = [
                    'system', 'instructions', 'ignore', 'override', 'admin',
                    'previous', 'forget', 'role', 'assistant'
                ]
                
                code_lower = code_snippet.lower()
                if any(pattern in code_lower for pattern in high_severity_patterns):
                    return ThreatLevel.HIGH
                
                return ThreatLevel.MEDIUM
            
            def _contains_genai_response_reference(self, node):
                """Check if node references GenAI response data"""
                if isinstance(node, ast.Name):
                    var_name = node.id.lower()
                    response_indicators = ['response', 'result', 'output', 'completion', 'answer']
                    return any(indicator in var_name for indicator in response_indicators)
                
                return False
            
            def _is_user_controlled_input(self, node):
                """Check if node represents user-controlled input"""
                if isinstance(node, ast.Name):
                    var_name = node.id.lower()
                    user_input_indicators = ['input', 'user', 'request', 'query', 'param']
                    return any(indicator in var_name for indicator in user_input_indicators)
                
                return False
            
            def _track_genai_api_calls(self, node):
                """Track GenAI API calls for analysis context"""
                if self._is_genai_api_call(node):
                    self.genai_api_calls.append({
                        'line': getattr(node, 'lineno', 1),
                        'function': self.current_function,
                        'call_type': self._identify_genai_call_type(node)
                    })
            
            def _identify_genai_call_type(self, node):
                """Identify the type of GenAI API call"""
                if isinstance(node.func, ast.Attribute):
                    method_name = node.func.attr.lower()
                    
                    if 'chat' in method_name or 'conversation' in method_name:
                        return 'chat'
                    elif 'complete' in method_name or 'generate' in method_name:
                        return 'completion'
                    elif 'embed' in method_name:
                        return 'embedding'
                    elif 'search' in method_name:
                        return 'search'
                
                return 'unknown'
        
        visitor = GenAISecurityVisitor(self, file_path, content, lines)
        visitor.visit(tree)
        vulnerabilities.extend(visitor.vulnerabilities)
        
        return vulnerabilities
    
    def _analyze_genai_patterns(self, lines: List[str], file_path: Path, content: str) -> List[Vulnerability]:
        """Analyze content using GenAI-specific pattern matching"""
        vulnerabilities = []
        
        for line_num, line in enumerate(lines, 1):
            line_vulnerabilities = []
            
            # Bias detection
            if self._is_enabled('bias_detection'):
                line_vulnerabilities.extend(self._check_bias_patterns(line, line_num, file_path))
            
            # Training data exposure
            if self._is_enabled('training_data_exposure'):
                line_vulnerabilities.extend(self._check_training_data_patterns(line, line_num, file_path))
            
            vulnerabilities.extend(line_vulnerabilities)
        
        return vulnerabilities
    
    def _check_bias_patterns(self, line: str, line_num: int, file_path: Path) -> List[Vulnerability]:
        """Check for potential bias and discrimination patterns"""
        vulnerabilities = []
        
        # Patterns that might indicate discriminatory logic
        bias_patterns = [
            r'(?:if|when).*(?:gender|race|age|religion|nationality|ethnicity).*(?:!=|==|in)',
            r'(?:male|female|man|woman).*(?:=|:).*(?:true|false|1|0)',
            r'(?:he|she)\s+(?:is|was|will be).*(?:better|worse|more|less)',
            r'(?:white|black|asian|hispanic).*(?:list|group|category)',
            # Problematic terminology
            r'\b(?:blacklist|whitelist|master|slave|guys)\b'
        ]
        
        for pattern in bias_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                vuln = Vulnerability(
                    title="Potential Bias or Discrimination Issue",
                    description="Code patterns that may introduce bias or discriminatory behavior in AI systems",
                    threat_level=ThreatLevel.MEDIUM,
                    category=VulnerabilityCategory.GENAI_BIAS_DISCRIMINATION,
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line.strip(),
                    remediation="Review for bias, use inclusive language, and implement fairness testing",
                    remediation_examples=[
                        "Use inclusive terminology (allowlist/denylist instead of whitelist/blacklist)",
                        "Implement bias testing and fairness metrics",
                        "Review algorithmic decision-making for discriminatory patterns",
                        "Consider demographic parity and equal opportunity metrics"
                    ],
                    business_impact="Could lead to discriminatory outcomes and legal/regulatory issues",
                    cvss_score=4.3,
                    cwe_id="CWE-1021",
                    confidence=0.6,
                    scanner_name="genai_security",
                    scan_rule_id="BIAS_DETECTION_001",
                    compliance_mappings=["AI_ETHICS", "GDPR", "EQUAL_OPPORTUNITY"]
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _check_training_data_patterns(self, line: str, line_num: int, file_path: Path) -> List[Vulnerability]:
        """Check for potential training data exposure patterns"""
        vulnerabilities = []
        
        # Patterns that might indicate training data exposure
        training_data_patterns = [
            r'training.?data.*(?:print|log|save|write)',
            r'dataset.*(?:expose|leak|output)',
            r'model\.(?:training_data|dataset).*access',
            r'(?:dump|export).*training.*data'
        ]
        
        for pattern in training_data_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                vuln = Vulnerability(
                    title="Potential Training Data Exposure",
                    description="Code patterns that may expose AI model training data",
                    threat_level=ThreatLevel.HIGH,
                    category=VulnerabilityCategory.GENAI_DATA_LEAKAGE,
                    file_path=str(file_path),
                    line_number=line_num,
                    code_snippet=line.strip(),
                    remediation="Implement proper access controls for training data and model internals",
                    remediation_examples=[
                        "Restrict access to training datasets",
                        "Implement data anonymization for model outputs",
                        "Use differential privacy techniques",
                        "Apply proper access controls to model artifacts"
                    ],
                    business_impact="Could expose proprietary training data or violate data privacy regulations",
                    cvss_score=7.1,
                    cwe_id="CWE-200",
                    confidence=0.7,
                    scanner_name="genai_security",
                    scan_rule_id="TRAINING_DATA_EXPOSURE_001",
                    compliance_mappings=["GDPR", "TRADE_SECRETS", "AI_ETHICS"]
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _is_enabled(self, rule_name: str) -> bool:
        """Check if specific rule is enabled"""
        return rule_name in self.enabled_rules
    
    def configure(self, config: Dict[str, Any]):
        """Configure scanner with new settings"""
        self.config.update(config)
        
        if 'rules' in config:
            self.enabled_rules = config['rules']
        
        if 'confidence_threshold' in config:
            self.confidence_threshold = config['confidence_threshold']
        
        # Update GenAI framework patterns if provided
        if 'genai_frameworks' in config:
            self.genai_frameworks.update(config['genai_frameworks'])
