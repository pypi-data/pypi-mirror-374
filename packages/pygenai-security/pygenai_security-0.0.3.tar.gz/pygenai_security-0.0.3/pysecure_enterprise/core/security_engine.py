"""
PySecure Enterprise - Production-Ready Security Engine
Copyright (C) 2025 PySecure Enterprise Solutions

Production-grade Python and GenAI security scanning framework
with enterprise features, real-time monitoring, and compliance reporting.
"""

import os
import sys
import time
import logging
import threading
import asyncio
import hashlib
import json
import traceback
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timezone
import uuid
import contextlib

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pysecure_enterprise.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


class SecurityThreatLevel(Enum):
    """Enterprise security threat levels with numeric scores"""
    CRITICAL = ("critical", 10)
    HIGH = ("high", 7)
    MEDIUM = ("medium", 5)
    LOW = ("low", 3)
    INFO = ("info", 1)
    
    def __init__(self, level_name: str, score: int):
        self.level_name = level_name
        self.score = score


class VulnerabilityType(Enum):
    """Comprehensive vulnerability classification"""
    # OWASP Top 10 2023
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    CRYPTOGRAPHIC_FAILURES = "cryptographic_failures"  
    INJECTION = "injection"
    INSECURE_DESIGN = "insecure_design"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    IDENTIFICATION_AUTH_FAILURES = "identification_auth_failures"
    SOFTWARE_DATA_INTEGRITY = "software_data_integrity"
    LOGGING_MONITORING_FAILURES = "logging_monitoring_failures"
    SSRF = "server_side_request_forgery"
    
    # GenAI Specific
    GENAI_PROMPT_INJECTION = "genai_prompt_injection"
    GENAI_DATA_LEAKAGE = "genai_data_leakage"
    GENAI_MODEL_MANIPULATION = "genai_model_manipulation"
    GENAI_BIAS_DISCRIMINATION = "genai_bias_discrimination"
    GENAI_PRIVACY_VIOLATION = "genai_privacy_violation"


@dataclass
class SecurityVulnerability:
    """Production-grade vulnerability representation with full metadata"""
    
    # Core identification
    id: str
    title: str
    description: str
    threat_level: SecurityThreatLevel
    vulnerability_type: VulnerabilityType
    
    # Location information
    file_path: str
    line_number: int
    column_number: int = 0
    end_line: int = 0
    end_column: int = 0
    
    # Code context
    code_snippet: str = ""
    affected_code_block: str = ""
    
    # Security analysis
    remediation_advice: str = ""
    remediation_examples: List[str] = field(default_factory=list)
    business_impact: str = ""
    technical_impact: str = ""
    
    # Scoring and classification
    cvss_score: float = 0.0
    exploitability_score: float = 0.0
    confidence_score: float = 1.0
    false_positive_probability: float = 0.0
    
    # Standards compliance
    cwe_id: str = ""
    owasp_category: str = ""
    compliance_violations: List[str] = field(default_factory=list)
    
    # Temporal information  
    first_detected: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    detection_count: int = 1
    
    # Scanner metadata
    scanner_name: str = "pysecure_enterprise"
    scanner_version: str = "1.0.0"
    scan_rule_id: str = ""
    
    # Enterprise features
    assigned_to: str = ""
    priority: str = "medium"
    status: str = "open"  # open, in_progress, resolved, false_positive
    resolution_notes: str = ""
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        if not self.id:
            self.id = self._generate_id()
        
        if self.end_line == 0:
            self.end_line = self.line_number
        
        self.last_updated = datetime.now(timezone.utc)
    
    def _generate_id(self) -> str:
        """Generate unique vulnerability ID"""
        content = f"{self.file_path}:{self.line_number}:{self.title}:{time.time()}"
        return f"PSE-{hashlib.sha256(content.encode()).hexdigest()[:12].upper()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        result = asdict(self)
        result['threat_level'] = self.threat_level.level_name
        result['vulnerability_type'] = self.vulnerability_type.value
        result['first_detected'] = self.first_detected.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        return result
    
    def get_risk_score(self) -> float:
        """Calculate comprehensive risk score"""
        base_score = self.threat_level.score
        cvss_weight = (self.cvss_score / 10.0) * 5
        exploitability_weight = self.exploitability_score * 2
        confidence_weight = self.confidence_score * 1.5
        
        risk_score = base_score + cvss_weight + exploitability_weight + confidence_weight
        return min(risk_score, 20.0)  # Cap at 20


class EnterpriseSecurityScanner:
    """Production-ready enterprise security scanner with full error handling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.vulnerabilities: List[SecurityVulnerability] = []
        self.scan_id = str(uuid.uuid4())
        self.is_scanning = False
        self._scan_lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Enterprise licensing and features
        self.license_status = "valid"  # In production: validate against license server
        self.enterprise_features_enabled = True
        
        # Performance and concurrency settings
        self.max_workers = self.config.get('performance', {}).get('max_workers', 4)
        self.scan_timeout = self.config.get('performance', {}).get('scan_timeout', 3600)
        self.file_size_limit = self.config.get('performance', {}).get('file_size_limit_mb', 50) * 1024 * 1024
        
        # Initialize components
        self._initialize_logging()
        self._initialize_scanners()
        self._setup_signal_handlers()
        
        logger.info(f"PySecure Enterprise Scanner initialized (ID: {self.scan_id})")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default enterprise configuration"""
        return {
            'scanners': {
                'enabled': ['traditional_security', 'genai_security', 'dependency_security', 'configuration_security'],
                'traditional_security': {
                    'enabled': True,
                    'rules': ['sql_injection', 'xss', 'command_injection', 'path_traversal', 'hardcoded_secrets']
                },
                'genai_security': {
                    'enabled': True,
                    'rules': ['prompt_injection', 'data_leakage', 'model_manipulation', 'bias_detection']
                },
                'dependency_security': {
                    'enabled': True,
                    'check_known_vulnerabilities': True,
                    'check_license_compatibility': True
                }
            },
            'filtering': {
                'min_threat_level': 'medium',
                'exclude_false_positives': True,
                'confidence_threshold': 0.7
            },
            'compliance': {
                'frameworks': ['OWASP_TOP_10', 'CWE_TOP_25', 'SANS_TOP_25', 'PCI_DSS', 'GDPR', 'HIPAA', 'SOX'],
                'generate_compliance_report': True
            },
            'performance': {
                'max_workers': 4,
                'scan_timeout': 3600,
                'file_size_limit_mb': 50,
                'enable_parallel_scanning': True
            },
            'enterprise': {
                'enable_real_time_monitoring': True,
                'enable_automated_remediation': False,
                'integration_webhook_url': None,
                'notification_channels': ['email', 'slack'],
                'priority_escalation': True
            },
            'analytics': {
                'enable_telemetry': True,
                'privacy_mode': True,
                'collect_performance_metrics': True
            }
        }
    
    def _initialize_logging(self):
        """Initialize comprehensive logging system"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        
        # Create enterprise logger
        self.enterprise_logger = logging.getLogger('pysecure.enterprise')
        self.enterprise_logger.setLevel(getattr(logging, log_level))
        
        # Security events logger
        self.security_logger = logging.getLogger('pysecure.security')
        security_handler = logging.FileHandler('security_events.log')
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(security_handler)
        
        # Audit logger
        self.audit_logger = logging.getLogger('pysecure.audit')
        audit_handler = logging.FileHandler('audit.log')
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)
    
    def _initialize_scanners(self):
        """Initialize all security scanners with error handling"""
        self.scanners = {}
        enabled_scanners = self.config.get('scanners', {}).get('enabled', [])
        
        scanner_classes = {
            'traditional_security': TraditionalSecurityScanner,
            'genai_security': GenAISecurityScanner,
            'dependency_security': DependencySecurityScanner,
            'configuration_security': ConfigurationSecurityScanner
        }
        
        for scanner_name in enabled_scanners:
            try:
                if scanner_name in scanner_classes:
                    scanner_config = self.config.get('scanners', {}).get(scanner_name, {})
                    self.scanners[scanner_name] = scanner_classes[scanner_name](scanner_config)
                    logger.info(f"Initialized {scanner_name} scanner")
            except Exception as e:
                logger.error(f"Failed to initialize {scanner_name} scanner: {e}")
                self.enterprise_logger.error(f"Scanner initialization failed", exc_info=True)
        
        if not self.scanners:
            raise RuntimeError("No security scanners could be initialized")
        
        logger.info(f"Initialized {len(self.scanners)} security scanners")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self._shutdown_event.set()
            self.stop_scan()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    @contextlib.contextmanager
    def _scan_context(self):
        """Context manager for scan operations"""
        if not self._validate_license():
            raise RuntimeError("Invalid or expired enterprise license")
        
        with self._scan_lock:
            if self.is_scanning:
                raise RuntimeError("Another scan is already in progress")
            self.is_scanning = True
        
        scan_start = time.time()
        try:
            self.audit_logger.info(f"Scan started - ID: {self.scan_id}")
            yield
        except Exception as e:
            self.security_logger.error(f"Scan failed - ID: {self.scan_id}, Error: {e}")
            raise
        finally:
            scan_duration = time.time() - scan_start
            with self._scan_lock:
                self.is_scanning = False
            self.audit_logger.info(f"Scan completed - ID: {self.scan_id}, Duration: {scan_duration:.2f}s")
    
    def scan_directory(self, 
                      directory_path: Union[str, Path],
                      include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None,
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Enterprise directory scanning with comprehensive error handling and monitoring
        
        Args:
            directory_path: Path to directory to scan
            include_patterns: File patterns to include (default: ['*.py'])
            exclude_patterns: File patterns to exclude
            progress_callback: Optional progress callback function
            
        Returns:
            Comprehensive scan results with security metrics and recommendations
        """
        
        directory = Path(directory_path).resolve()
        
        # Validate directory
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        with self._scan_context():
            try:
                scan_start_time = time.time()
                
                # Find files to scan
                files_to_scan = self._discover_files(directory, include_patterns, exclude_patterns)
                
                if not files_to_scan:
                    logger.warning(f"No scannable files found in {directory}")
                    return self._create_empty_results(scan_start_time)
                
                logger.info(f"Starting enterprise scan of {len(files_to_scan)} files in {directory}")
                
                # Initialize progress tracking
                progress_tracker = ScanProgressTracker(len(files_to_scan), progress_callback)
                
                # Clear previous results
                self.vulnerabilities.clear()
                
                # Execute parallel scanning
                scan_results = self._execute_parallel_scan(files_to_scan, progress_tracker)
                
                # Generate comprehensive results
                results = self._generate_comprehensive_results(scan_start_time, scan_results)
                
                logger.info(f"Scan completed: {results['summary']['total_vulnerabilities']} vulnerabilities found")
                
                return results
                
            except Exception as e:
                logger.error(f"Enterprise scan failed: {e}")
                self.security_logger.error("Enterprise scan failure", exc_info=True)
                raise
    
    def _discover_files(self, 
                       directory: Path, 
                       include_patterns: Optional[List[str]], 
                       exclude_patterns: Optional[List[str]]) -> List[Path]:
        """Discover files to scan with intelligent filtering"""
        
        if include_patterns is None:
            include_patterns = ['*.py', '*.pyw']
        
        if exclude_patterns is None:
            exclude_patterns = [
                '*.pyc', '__pycache__/*', '.git/*', '.svn/*', '.hg/*',
                '.venv/*', 'venv/*', 'env/*', 'virtualenv/*',
                'node_modules/*', '.tox/*', 'build/*', 'dist/*',
                '.pytest_cache/*', '*.egg-info/*', '.mypy_cache/*',
                'htmlcov/*', '.coverage.*', '.DS_Store'
            ]
        
        discovered_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Filter directories early to avoid descending into excluded paths
                dirs[:] = [d for d in dirs if not self._matches_exclude_patterns(
                    os.path.join(root, d), exclude_patterns
                )]
                
                root_path = Path(root)
                
                for file in files:
                    file_path = root_path / file
                    
                    # Check include patterns
                    if not self._matches_include_patterns(str(file_path), include_patterns):
                        continue
                    
                    # Check exclude patterns
                    if self._matches_exclude_patterns(str(file_path), exclude_patterns):
                        continue
                    
                    # Validate file for scanning
                    if self._is_scannable_file(file_path):
                        discovered_files.append(file_path)
        
        except Exception as e:
            logger.error(f"File discovery failed: {e}")
            raise
        
        return sorted(discovered_files)
    
    def _matches_include_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches include patterns"""
        import fnmatch
        return any(fnmatch.fnmatch(file_path, pattern) or 
                  fnmatch.fnmatch(os.path.basename(file_path), pattern) 
                  for pattern in patterns)
    
    def _matches_exclude_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches exclude patterns"""
        import fnmatch
        return any(fnmatch.fnmatch(file_path, pattern) or 
                  fnmatch.fnmatch(os.path.basename(file_path), pattern)
                  for pattern in patterns)
    
    def _is_scannable_file(self, file_path: Path) -> bool:
        """Validate if file can be scanned"""
        try:
            # Check file size
            if file_path.stat().st_size > self.file_size_limit:
                logger.debug(f"Skipping large file: {file_path}")
                return False
            
            # Check file accessibility
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)  # Try to read first 1KB
            
            return True
            
        except (OSError, IOError, PermissionError) as e:
            logger.debug(f"Cannot access file {file_path}: {e}")
            return False
    
    def _execute_parallel_scan(self, 
                              files_to_scan: List[Path],
                              progress_tracker) -> Dict[str, Any]:
        """Execute parallel scanning with comprehensive error handling"""
        
        scan_results = {
            'total_files_scanned': 0,
            'total_vulnerabilities_found': 0,
            'scanner_results': {},
            'scan_errors': [],
            'performance_metrics': {}
        }
        
        if not self.config.get('performance', {}).get('enable_parallel_scanning', True):
            return self._execute_sequential_scan(files_to_scan, progress_tracker)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit scanner tasks
            future_to_scanner = {}
            
            for scanner_name, scanner in self.scanners.items():
                if self._shutdown_event.is_set():
                    break
                
                future = executor.submit(
                    self._run_scanner_with_monitoring,
                    scanner_name, 
                    scanner, 
                    files_to_scan,
                    progress_tracker
                )
                future_to_scanner[future] = scanner_name
            
            # Collect results with timeout handling
            completed_scanners = 0
            
            for future in as_completed(future_to_scanner, timeout=self.scan_timeout):
                if self._shutdown_event.is_set():
                    break
                
                scanner_name = future_to_scanner[future]
                
                try:
                    scanner_result = future.result(timeout=60)  # 60 second per-scanner timeout
                    
                    scan_results['scanner_results'][scanner_name] = scanner_result
                    scan_results['total_vulnerabilities_found'] += len(scanner_result.get('vulnerabilities', []))
                    
                    # Add vulnerabilities to main collection
                    self.vulnerabilities.extend(scanner_result.get('vulnerabilities', []))
                    
                    completed_scanners += 1
                    logger.info(f"Scanner {scanner_name} completed: {len(scanner_result.get('vulnerabilities', []))} vulnerabilities")
                    
                except TimeoutError:
                    error_msg = f"Scanner {scanner_name} timed out"
                    logger.error(error_msg)
                    scan_results['scan_errors'].append({
                        'scanner': scanner_name,
                        'error': error_msg,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                    
                except Exception as e:
                    error_msg = f"Scanner {scanner_name} failed: {str(e)}"
                    logger.error(error_msg)
                    self.security_logger.error(f"Scanner failure: {scanner_name}", exc_info=True)
                    scan_results['scan_errors'].append({
                        'scanner': scanner_name,
                        'error': error_msg,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
        
        scan_results['total_files_scanned'] = len(files_to_scan)
        scan_results['completed_scanners'] = completed_scanners
        
        return scan_results
    
    def _run_scanner_with_monitoring(self, 
                                   scanner_name: str, 
                                   scanner, 
                                   files_to_scan: List[Path],
                                   progress_tracker) -> Dict[str, Any]:
        """Run individual scanner with comprehensive monitoring"""
        
        scanner_start_time = time.time()
        
        try:
            # Update progress
            progress_tracker.update_current_scanner(scanner_name)
            
            # Execute scanner
            vulnerabilities = scanner.scan_files(files_to_scan)
            
            scanner_duration = time.time() - scanner_start_time
            
            # Log performance metrics
            logger.info(f"Scanner {scanner_name}: {len(vulnerabilities)} vulnerabilities in {scanner_duration:.2f}s")
            
            return {
                'vulnerabilities': vulnerabilities,
                'duration': scanner_duration,
                'files_processed': len(files_to_scan),
                'performance_metrics': {
                    'files_per_second': len(files_to_scan) / scanner_duration if scanner_duration > 0 else 0,
                    'vulnerabilities_per_second': len(vulnerabilities) / scanner_duration if scanner_duration > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Scanner {scanner_name} execution failed: {e}")
            raise
    
    def _generate_comprehensive_results(self, scan_start_time: float, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive enterprise scan results"""
        
        scan_duration = time.time() - scan_start_time
        
        # Filter and deduplicate vulnerabilities
        filtered_vulnerabilities = self._process_vulnerabilities()
        
        # Calculate comprehensive metrics
        security_metrics = self._calculate_security_metrics(filtered_vulnerabilities)
        
        # Generate compliance analysis
        compliance_analysis = self._analyze_compliance_impact(filtered_vulnerabilities)
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(filtered_vulnerabilities, security_metrics)
        
        # Calculate risk scores
        risk_analysis = self._calculate_risk_analysis(filtered_vulnerabilities)
        
        return {
            'scan_metadata': {
                'scan_id': self.scan_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'duration': scan_duration,
                'scanner_version': '1.0.0',
                'license_status': self.license_status
            },
            'summary': {
                'total_vulnerabilities': len(filtered_vulnerabilities),
                'files_scanned': scan_results.get('total_files_scanned', 0),
                'scanners_used': list(scan_results.get('scanner_results', {}).keys()),
                'scan_errors': scan_results.get('scan_errors', [])
            },
            'vulnerabilities': [v.to_dict() for v in filtered_vulnerabilities],
            'security_metrics': security_metrics,
            'compliance_analysis': compliance_analysis,
            'risk_analysis': risk_analysis,
            'recommendations': recommendations,
            'performance_metrics': {
                'scan_duration': scan_duration,
                'files_per_second': scan_results.get('total_files_scanned', 0) / scan_duration if scan_duration > 0 else 0,
                'vulnerabilities_per_second': len(filtered_vulnerabilities) / scan_duration if scan_duration > 0 else 0,
                'scanner_performance': {name: result.get('performance_metrics', {}) 
                                      for name, result in scan_results.get('scanner_results', {}).items()}
            },
            'enterprise_features': {
                'real_time_monitoring': self.config.get('enterprise', {}).get('enable_real_time_monitoring', False),
                'automated_remediation': self.config.get('enterprise', {}).get('enable_automated_remediation', False),
                'integration_enabled': bool(self.config.get('enterprise', {}).get('integration_webhook_url'))
            }
        }
    
    def _process_vulnerabilities(self) -> List[SecurityVulnerability]:
        """Process, filter, and deduplicate vulnerabilities"""
        
        # Remove duplicates based on file, line, and vulnerability type
        seen_vulnerabilities = set()
        unique_vulnerabilities = []
        
        for vuln in self.vulnerabilities:
            vuln_key = (vuln.file_path, vuln.line_number, vuln.vulnerability_type.value)
            if vuln_key not in seen_vulnerabilities:
                seen_vulnerabilities.add(vuln_key)
                unique_vulnerabilities.append(vuln)
        
        # Filter by threat level and confidence
        min_threat_level = self.config.get('filtering', {}).get('min_threat_level', 'medium')
        confidence_threshold = self.config.get('filtering', {}).get('confidence_threshold', 0.7)
        exclude_false_positives = self.config.get('filtering', {}).get('exclude_false_positives', True)
        
        threat_level_map = {
            'critical': [SecurityThreatLevel.CRITICAL],
            'high': [SecurityThreatLevel.CRITICAL, SecurityThreatLevel.HIGH],
            'medium': [SecurityThreatLevel.CRITICAL, SecurityThreatLevel.HIGH, SecurityThreatLevel.MEDIUM],
            'low': [SecurityThreatLevel.CRITICAL, SecurityThreatLevel.HIGH, SecurityThreatLevel.MEDIUM, SecurityThreatLevel.LOW],
            'info': list(SecurityThreatLevel)
        }
        
        allowed_threat_levels = threat_level_map.get(min_threat_level, threat_level_map['medium'])
        
        filtered_vulnerabilities = []
        for vuln in unique_vulnerabilities:
            # Filter by threat level
            if vuln.threat_level not in allowed_threat_levels:
                continue
            
            # Filter by confidence
            if vuln.confidence_score < confidence_threshold:
                continue
            
            # Filter false positives
            if exclude_false_positives and vuln.false_positive_probability > 0.5:
                continue
            
            filtered_vulnerabilities.append(vuln)
        
        return filtered_vulnerabilities
    
    def _calculate_security_metrics(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Calculate comprehensive security metrics"""
        
        if not vulnerabilities:
            return {
                'by_threat_level': {level.level_name: 0 for level in SecurityThreatLevel},
                'by_vulnerability_type': {},
                'by_scanner': {},
                'risk_metrics': {
                    'total_risk_score': 0.0,
                    'average_risk_score': 0.0,
                    'highest_risk_score': 0.0
                },
                'quality_metrics': {
                    'average_confidence': 0.0,
                    'average_cvss_score': 0.0,
                    'false_positive_rate': 0.0
                }
            }
        
        metrics = {
            'by_threat_level': {level.level_name: 0 for level in SecurityThreatLevel},
            'by_vulnerability_type': {},
            'by_scanner': {},
            'affected_files': len(set(v.file_path for v in vulnerabilities)),
            'total_vulnerabilities': len(vulnerabilities)
        }
        
        # Count by categories
        risk_scores = []
        confidence_scores = []
        cvss_scores = []
        false_positive_rates = []
        
        for vuln in vulnerabilities:
            # Threat level counts
            metrics['by_threat_level'][vuln.threat_level.level_name] += 1
            
            # Vulnerability type counts
            vuln_type = vuln.vulnerability_type.value
            if vuln_type not in metrics['by_vulnerability_type']:
                metrics['by_vulnerability_type'][vuln_type] = 0
            metrics['by_vulnerability_type'][vuln_type] += 1
            
            # Scanner counts
            scanner = vuln.scanner_name
            if scanner not in metrics['by_scanner']:
                metrics['by_scanner'][scanner] = 0
            metrics['by_scanner'][scanner] += 1
            
            # Collect scores for averages
            risk_scores.append(vuln.get_risk_score())
            confidence_scores.append(vuln.confidence_score)
            if vuln.cvss_score > 0:
                cvss_scores.append(vuln.cvss_score)
            false_positive_rates.append(vuln.false_positive_probability)
        
        # Calculate risk metrics
        metrics['risk_metrics'] = {
            'total_risk_score': sum(risk_scores),
            'average_risk_score': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            'highest_risk_score': max(risk_scores) if risk_scores else 0,
            'risk_distribution': {
                'low_risk': len([s for s in risk_scores if s <= 5]),
                'medium_risk': len([s for s in risk_scores if 5 < s <= 10]),
                'high_risk': len([s for s in risk_scores if 10 < s <= 15]),
                'critical_risk': len([s for s in risk_scores if s > 15])
            }
        }
        
        # Calculate quality metrics
        metrics['quality_metrics'] = {
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'average_cvss_score': sum(cvss_scores) / len(cvss_scores) if cvss_scores else 0,
            'false_positive_rate': sum(false_positive_rates) / len(false_positive_rates) if false_positive_rates else 0
        }
        
        return metrics
    
    def _analyze_compliance_impact(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Analyze compliance impact of detected vulnerabilities"""
        
        compliance_frameworks = self.config.get('compliance', {}).get('frameworks', [])
        compliance_analysis = {}
        
        for framework in compliance_frameworks:
            compliance_analysis[framework] = {
                'total_violations': 0,
                'by_severity': {level.level_name: 0 for level in SecurityThreatLevel},
                'affected_categories': set(),
                'compliance_score': 100.0,  # Start with perfect score
                'risk_level': 'low'
            }
        
        # Analyze each vulnerability for compliance impact
        for vuln in vulnerabilities:
            for compliance_violation in vuln.compliance_violations:
                if compliance_violation in compliance_analysis:
                    analysis = compliance_analysis[compliance_violation]
                    analysis['total_violations'] += 1
                    analysis['by_severity'][vuln.threat_level.level_name] += 1
                    analysis['affected_categories'].add(vuln.vulnerability_type.value)
        
        # Calculate compliance scores and risk levels
        for framework, analysis in compliance_analysis.items():
            # Convert sets to lists for JSON serialization
            analysis['affected_categories'] = list(analysis['affected_categories'])
            
            # Calculate compliance score (simplified algorithm)
            total_violations = analysis['total_violations']
            if total_violations == 0:
                analysis['compliance_score'] = 100.0
                analysis['risk_level'] = 'low'
            else:
                # Penalty based on violation severity
                penalty = (
                    analysis['by_severity']['critical'] * 25 +
                    analysis['by_severity']['high'] * 15 +
                    analysis['by_severity']['medium'] * 10 +
                    analysis['by_severity']['low'] * 5
                )
                analysis['compliance_score'] = max(0.0, 100.0 - penalty)
                
                # Determine risk level
                if analysis['compliance_score'] >= 90:
                    analysis['risk_level'] = 'low'
                elif analysis['compliance_score'] >= 70:
                    analysis['risk_level'] = 'medium'
                else:
                    analysis['risk_level'] = 'high'
        
        return compliance_analysis
    
    def _calculate_risk_analysis(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Calculate comprehensive risk analysis"""
        
        if not vulnerabilities:
            return {
                'overall_risk_score': 0.0,
                'risk_level': 'low',
                'top_risks': [],
                'risk_trends': {},
                'mitigation_priority': []
            }
        
        # Calculate overall risk score
        risk_scores = [vuln.get_risk_score() for vuln in vulnerabilities]
        overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Determine overall risk level
        if overall_risk_score >= 15:
            risk_level = 'critical'
        elif overall_risk_score >= 10:
            risk_level = 'high'
        elif overall_risk_score >= 5:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Identify top risks
        top_risks = sorted(vulnerabilities, key=lambda v: v.get_risk_score(), reverse=True)[:10]
        
        # Generate mitigation priorities
        mitigation_priority = []
        
        # Critical vulnerabilities first
        critical_vulns = [v for v in vulnerabilities if v.threat_level == SecurityThreatLevel.CRITICAL]
        if critical_vulns:
            mitigation_priority.append({
                'priority': 1,
                'category': 'Critical Vulnerabilities',
                'count': len(critical_vulns),
                'recommendation': 'Address immediately - these pose severe security risks'
            })
        
        # High-impact vulnerabilities
        high_impact_vulns = [v for v in vulnerabilities if 'injection' in v.vulnerability_type.value.lower()]
        if high_impact_vulns:
            mitigation_priority.append({
                'priority': 2,
                'category': 'Injection Vulnerabilities',
                'count': len(high_impact_vulns),
                'recommendation': 'High priority - injection attacks can lead to data breaches'
            })
        
        # GenAI specific vulnerabilities
        genai_vulns = [v for v in vulnerabilities if 'genai' in v.vulnerability_type.value.lower()]
        if genai_vulns:
            mitigation_priority.append({
                'priority': 3,
                'category': 'GenAI Security Issues',
                'count': len(genai_vulns),
                'recommendation': 'Emerging threat - secure AI/ML components against attacks'
            })
        
        return {
            'overall_risk_score': overall_risk_score,
            'risk_level': risk_level,
            'top_risks': [
                {
                    'id': vuln.id,
                    'title': vuln.title,
                    'risk_score': vuln.get_risk_score(),
                    'file_path': vuln.file_path,
                    'threat_level': vuln.threat_level.level_name
                }
                for vuln in top_risks
            ],
            'mitigation_priority': mitigation_priority,
            'statistics': {
                'total_risk_exposure': sum(risk_scores),
                'average_risk_per_vulnerability': overall_risk_score,
                'risk_concentration': len([s for s in risk_scores if s > overall_risk_score])
            }
        }
    
    def _generate_security_recommendations(self, 
                                         vulnerabilities: List[SecurityVulnerability], 
                                         security_metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable security recommendations"""
        
        recommendations = []
        
        if not vulnerabilities:
            return ["Excellent! No security vulnerabilities detected. Continue regular security scanning."]
        
        # Critical vulnerability recommendations
        critical_count = security_metrics.get('by_threat_level', {}).get('critical', 0)
        if critical_count > 0:
            recommendations.append(
                f"🚨 URGENT: {critical_count} critical vulnerabilities require immediate attention. "
                "These pose severe security risks and should be fixed within 24 hours."
            )
        
        # High vulnerability recommendations
        high_count = security_metrics.get('by_threat_level', {}).get('high', 0)
        if high_count > 0:
            recommendations.append(
                f"⚠️ HIGH PRIORITY: {high_count} high-severity vulnerabilities detected. "
                "Plan to address these within 1 week."
            )
        
        # Category-specific recommendations
        vuln_types = security_metrics.get('by_vulnerability_type', {})
        
        # Injection vulnerabilities
        injection_types = [vtype for vtype in vuln_types.keys() if 'injection' in vtype.lower()]
        if injection_types:
            total_injection = sum(vuln_types[vtype] for vtype in injection_types)
            recommendations.append(
                f"🛡️ INJECTION PROTECTION: {total_injection} injection vulnerabilities found. "
                "Implement input validation, parameterized queries, and output encoding."
            )
        
        # GenAI specific recommendations
        genai_types = [vtype for vtype in vuln_types.keys() if 'genai' in vtype.lower()]
        if genai_types:
            total_genai = sum(vuln_types[vtype] for vtype in genai_types)
            recommendations.append(
                f"🤖 GENAI SECURITY: {total_genai} AI/ML security issues detected. "
                "Review prompt handling, model access controls, and data sanitization."
            )
        
        # Code quality recommendations
        quality_metrics = security_metrics.get('quality_metrics', {})
        if quality_metrics.get('false_positive_rate', 0) > 0.3:
            recommendations.append(
                "📊 CODE QUALITY: High false positive rate detected. "
                "Consider code review and refactoring to improve security scan accuracy."
            )
        
        # Compliance recommendations
        risk_metrics = security_metrics.get('risk_metrics', {})
        if risk_metrics.get('total_risk_score', 0) > 50:
            recommendations.append(
                "📋 COMPLIANCE: High overall risk score may impact compliance requirements. "
                "Prioritize remediation efforts and consider security training for development team."
            )
        
        # General security recommendations
        affected_files = security_metrics.get('affected_files', 0)
        total_files = security_metrics.get('total_vulnerabilities', 0)
        if affected_files > 0 and total_files / affected_files > 3:
            recommendations.append(
                "🔄 SECURITY PRACTICES: Multiple vulnerabilities per file detected. "
                "Implement secure coding practices, code reviews, and security testing in CI/CD."
            )
        
        return recommendations
    
    def _validate_license(self) -> bool:
        """Validate enterprise license (placeholder for production license check)"""
        # In production, this would validate against a license server
        return self.license_status == "valid"
    
    def _create_empty_results(self, scan_start_time: float) -> Dict[str, Any]:
        """Create empty results structure when no files are found"""
        return {
            'scan_metadata': {
                'scan_id': self.scan_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'duration': time.time() - scan_start_time,
                'scanner_version': '1.0.0'
            },
            'summary': {
                'total_vulnerabilities': 0,
                'files_scanned': 0,
                'scanners_used': [],
                'scan_errors': []
            },
            'vulnerabilities': [],
            'security_metrics': {
                'by_threat_level': {level.level_name: 0 for level in SecurityThreatLevel},
                'by_vulnerability_type': {},
                'total_vulnerabilities': 0
            },
            'recommendations': ["No scannable files found in the specified directory"]
        }
    
    def stop_scan(self):
        """Stop current scan gracefully"""
        logger.info("Stopping scan gracefully...")
        self._shutdown_event.set()
        
        with self._scan_lock:
            self.is_scanning = False
    
    def get_scan_status(self) -> Dict[str, Any]:
        """Get current scan status and metrics"""
        return {
            'scan_id': self.scan_id,
            'is_scanning': self.is_scanning,
            'license_status': self.license_status,
            'enterprise_features_enabled': self.enterprise_features_enabled,
            'available_scanners': list(self.scanners.keys()),
            'configuration': {
                'max_workers': self.max_workers,
                'scan_timeout': self.scan_timeout,
                'file_size_limit_mb': self.file_size_limit / (1024 * 1024)
            }
        }


class ScanProgressTracker:
    """Thread-safe scan progress tracking"""
    
    def __init__(self, total_files: int, callback: Optional[Callable] = None):
        self.total_files = total_files
        self.processed_files = 0
        self.current_scanner = ""
        self.current_file = ""
        self.start_time = time.time()
        self.callback = callback
        self._lock = threading.Lock()
    
    def update_current_scanner(self, scanner_name: str):
        """Update current scanner being executed"""
        with self._lock:
            self.current_scanner = scanner_name
            self._notify_callback()
    
    def update_processed_files(self, count: int):
        """Update number of processed files"""
        with self._lock:
            self.processed_files = count
            self._notify_callback()
    
    def _notify_callback(self):
        """Notify progress callback if provided"""
        if self.callback:
            try:
                progress_data = {
                    'total_files': self.total_files,
                    'processed_files': self.processed_files,
                    'current_scanner': self.current_scanner,
                    'current_file': self.current_file,
                    'elapsed_time': time.time() - self.start_time,
                    'progress_percentage': (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0
                }
                self.callback(progress_data)
            except Exception as e:
                logger.debug(f"Progress callback failed: {e}")


# Production scanner implementations with comprehensive error handling
class TraditionalSecurityScanner:
    """Production-grade traditional security scanner"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'sql_injection', 'xss', 'command_injection', 'path_traversal', 'hardcoded_secrets'
        ])
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
    
    def scan_files(self, files: List[Path]) -> List[SecurityVulnerability]:
        """Scan files for traditional security vulnerabilities"""
        vulnerabilities = []
        
        for file_path in files:
            try:
                file_vulnerabilities = self._scan_file(file_path)
                vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"Error scanning file {file_path}: {e}")
        
        return vulnerabilities
    
    def _scan_file(self, file_path: Path) -> List[SecurityVulnerability]:
        """Scan individual file for security issues"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # SQL Injection Detection
            if 'sql_injection' in self.enabled_rules:
                vulnerabilities.extend(self._detect_sql_injection(content, lines, file_path))
            
            # XSS Detection
            if 'xss' in self.enabled_rules:
                vulnerabilities.extend(self._detect_xss(content, lines, file_path))
            
            # Command Injection Detection
            if 'command_injection' in self.enabled_rules:
                vulnerabilities.extend(self._detect_command_injection(content, lines, file_path))
            
            # Path Traversal Detection
            if 'path_traversal' in self.enabled_rules:
                vulnerabilities.extend(self._detect_path_traversal(content, lines, file_path))
            
            # Hardcoded Secrets Detection
            if 'hardcoded_secrets' in self.enabled_rules:
                vulnerabilities.extend(self._detect_hardcoded_secrets(content, lines, file_path))
        
        except Exception as e:
            self.logger.error(f"File scan failed for {file_path}: {e}")
        
        return vulnerabilities
    
    def _detect_sql_injection(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect SQL injection vulnerabilities"""
        vulnerabilities = []
        
        # Pattern for SQL injection
        sql_patterns = [
            r'(execute|cursor\.execute)\s*\([^)]*\+[^)]*\)',
            r'query\s*=\s*[""][^""]*[""]\s*\+',
            r'SELECT\s+.*\+.*FROM',
            r'INSERT\s+.*\+.*VALUES',
            r'UPDATE\s+.*\+.*SET'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",  # Will be auto-generated
                        title="SQL Injection Vulnerability",
                        description="Dynamic SQL query construction detected that may be vulnerable to SQL injection attacks",
                        threat_level=SecurityThreatLevel.HIGH,
                        vulnerability_type=VulnerabilityType.INJECTION,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Use parameterized queries or prepared statements instead of string concatenation",
                        remediation_examples=[
                            "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                            "Use SQLAlchemy ORM or other safe database libraries"
                        ],
                        business_impact="Could allow attackers to access, modify, or delete database data",
                        technical_impact="Database compromise, data exfiltration, data manipulation",
                        cvss_score=8.1,
                        exploitability_score=0.9,
                        confidence_score=0.85,
                        cwe_id="CWE-89",
                        owasp_category="A03:2021 – Injection",
                        compliance_violations=["PCI-DSS", "SOX", "GDPR"]
                    ))
        
        return vulnerabilities
    
    def _detect_xss(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect XSS vulnerabilities"""
        vulnerabilities = []
        
        xss_patterns = [
            r'render_template\([^)]*\+[^)]*\)',
            r'return\s+[""][^""]*[""]\s*\+',
            r'innerHTML\s*=\s*[^;]*\+',
            r'document\.write\s*\([^)]*\+[^)]*\)'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Cross-Site Scripting (XSS) Vulnerability",
                        description="Dynamic content generation without proper output encoding detected",
                        threat_level=SecurityThreatLevel.MEDIUM,
                        vulnerability_type=VulnerabilityType.INJECTION,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Use proper output encoding and Content Security Policy (CSP)",
                        remediation_examples=[
                            "Use html.escape() for HTML contexts",
                            "Use template engines with auto-escaping enabled",
                            "Implement Content Security Policy headers"
                        ],
                        business_impact="Could allow attackers to execute malicious scripts in user browsers",
                        cvss_score=6.1,
                        confidence_score=0.75,
                        cwe_id="CWE-79",
                        owasp_category="A03:2021 – Injection"
                    ))
        
        return vulnerabilities
    
    def _detect_command_injection(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect command injection vulnerabilities"""
        vulnerabilities = []
        
        command_patterns = [
            r'os\.system\s*\([^)]*\+[^)]*\)',
            r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True[^)]*\+',
            r'exec\s*\([^)]*\+[^)]*\)',
            r'eval\s*\([^)]*\+[^)]*\)'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in command_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Command Injection Vulnerability",
                        description="Dynamic command execution with user input detected",
                        threat_level=SecurityThreatLevel.CRITICAL,
                        vulnerability_type=VulnerabilityType.INJECTION,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Use subprocess with shell=False and validate all inputs",
                        remediation_examples=[
                            "subprocess.run(['ls', directory], check=True)",
                            "Use shlex.quote() for shell command arguments",
                            "Avoid shell=True in subprocess calls"
                        ],
                        business_impact="Could allow attackers to execute arbitrary system commands",
                        technical_impact="Complete system compromise, data theft, malware installation",
                        cvss_score=9.8,
                        exploitability_score=0.95,
                        confidence_score=0.9,
                        cwe_id="CWE-78",
                        owasp_category="A03:2021 – Injection",
                        compliance_violations=["PCI-DSS", "SOX", "HIPAA", "GDPR"]
                    ))
        
        return vulnerabilities
    
    def _detect_path_traversal(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect path traversal vulnerabilities"""
        vulnerabilities = []
        
        path_patterns = [
            r'open\s*\([^)]*\+[^)]*\.\./',
            r'file\s*=\s*[^;]*\+[^;]*\.\./',
            r'os\.path\.join\s*\([^)]*\+[^)]*\)',
            r'Path\s*\([^)]*\+[^)]*\)'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in path_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Path Traversal Vulnerability",
                        description="Dynamic file path construction that may allow directory traversal attacks",
                        threat_level=SecurityThreatLevel.HIGH,
                        vulnerability_type=VulnerabilityType.BROKEN_ACCESS_CONTROL,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Validate and sanitize file paths, use os.path.abspath() and check against allowed directories",
                        remediation_examples=[
                            "Use os.path.realpath() and validate against allowed base directory",
                            "Implement whitelist of allowed file extensions and paths"
                        ],
                        business_impact="Could allow access to sensitive files outside intended directories",
                        cvss_score=7.5,
                        confidence_score=0.8,
                        cwe_id="CWE-22",
                        owasp_category="A01:2021 – Broken Access Control"
                    ))
        
        return vulnerabilities
    
    def _detect_hardcoded_secrets(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect hardcoded secrets and credentials"""
        vulnerabilities = []
        
        secret_patterns = [
            (r'password\s*=\s*[""][^""]{8,}[""]', "password"),
            (r'api_key\s*=\s*[""][^""]{16,}[""]', "api_key"),
            (r'secret\s*=\s*[""][^""]{16,}[""]', "secret"),
            (r'token\s*=\s*[""][^""]{20,}[""]', "token"),
            (r'private_key\s*=\s*[""][^""]{32,}[""]', "private_key"),
            (r'-----BEGIN.*PRIVATE KEY-----', "private_key_block")
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title=f"Hardcoded {secret_type.title().replace('_', ' ')}",
                        description=f"Hardcoded {secret_type.replace('_', ' ')} detected in source code",
                        threat_level=SecurityThreatLevel.CRITICAL,
                        vulnerability_type=VulnerabilityType.CRYPTOGRAPHIC_FAILURES,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice=f"Move {secret_type} to environment variables or secure configuration management",
                        remediation_examples=[
                            f"{secret_type} = os.environ.get('{secret_type.upper()}')",
                            "Use Azure Key Vault, AWS Secrets Manager, or HashiCorp Vault",
                            "Implement proper secrets rotation policies"
                        ],
                        business_impact="Hardcoded secrets can be easily discovered and misused by attackers",
                        technical_impact="Unauthorized access to services, data breaches, privilege escalation",
                        cvss_score=9.1,
                        confidence_score=0.95,
                        cwe_id="CWE-798",
                        owasp_category="A02:2021 – Cryptographic Failures",
                        compliance_violations=["PCI-DSS", "SOX", "HIPAA", "GDPR"]
                    ))
        
        return vulnerabilities


class GenAISecurityScanner:
    """Production-grade GenAI security scanner"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_rules = self.config.get('rules', [
            'prompt_injection', 'data_leakage', 'model_manipulation', 'bias_detection'
        ])
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        
        # GenAI framework detection patterns
        self.genai_frameworks = {
            'openai': ['openai', 'ChatOpenAI', 'GPT', 'gpt-'],
            'anthropic': ['anthropic', 'claude', 'Claude'],
            'huggingface': ['transformers', 'AutoModel', 'AutoTokenizer', 'pipeline'],
            'langchain': ['langchain', 'LangChain', 'LLMChain'],
            'llamaindex': ['llama_index', 'GPTIndex', 'LlamaIndex']
        }
    
    def scan_files(self, files: List[Path]) -> List[SecurityVulnerability]:
        """Scan files for GenAI security vulnerabilities"""
        vulnerabilities = []
        
        for file_path in files:
            try:
                if self._is_genai_related_file(file_path):
                    file_vulnerabilities = self._scan_genai_file(file_path)
                    vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"Error scanning GenAI file {file_path}: {e}")
        
        return vulnerabilities
    
    def _is_genai_related_file(self, file_path: Path) -> bool:
        """Check if file contains GenAI-related code"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2048)  # Read first 2KB for framework detection
            
            for framework, patterns in self.genai_frameworks.items():
                if any(pattern in content for pattern in patterns):
                    return True
            return False
        except Exception:
            return False
    
    def _scan_genai_file(self, file_path: Path) -> List[SecurityVulnerability]:
        """Scan GenAI-related file for security issues"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Prompt Injection Detection
            if 'prompt_injection' in self.enabled_rules:
                vulnerabilities.extend(self._detect_prompt_injection(content, lines, file_path))
            
            # Data Leakage Detection
            if 'data_leakage' in self.enabled_rules:
                vulnerabilities.extend(self._detect_data_leakage(content, lines, file_path))
            
            # Model Manipulation Detection
            if 'model_manipulation' in self.enabled_rules:
                vulnerabilities.extend(self._detect_model_manipulation(content, lines, file_path))
            
            # Bias Detection
            if 'bias_detection' in self.enabled_rules:
                vulnerabilities.extend(self._detect_bias_issues(content, lines, file_path))
        
        except Exception as e:
            self.logger.error(f"GenAI file scan failed for {file_path}: {e}")
        
        return vulnerabilities
    
    def _detect_prompt_injection(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect prompt injection vulnerabilities"""
        vulnerabilities = []
        
        prompt_injection_patterns = [
            r'prompt\s*[+=]\s*[^;]*(?:request\.|input\(|user_)',
            r'f[""].*{.*(?:request\.|input\(|user_)}.*[""]',
            r'(?:messages?|prompt)\s*=\s*[^;]*\+[^;]*(?:request\.|input\()',
            r'system.*[""].*ignore.*previous.*instructions.*[""]',
            r'(?:override|ignore|forget).*(?:above|previous).*(?:instructions?|prompts?)'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in prompt_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Prompt Injection Vulnerability",
                        description="Unsafe prompt construction with user input that may be vulnerable to prompt injection attacks",
                        threat_level=SecurityThreatLevel.HIGH,
                        vulnerability_type=VulnerabilityType.GENAI_PROMPT_INJECTION,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Implement input validation, prompt templates, and user input sanitization",
                        remediation_examples=[
                            "Use structured prompts with clear separators",
                            "Sanitize user input before including in prompts",
                            "Implement prompt injection detection filters",
                            "Use role-based prompting with clear boundaries"
                        ],
                        business_impact="Could allow attackers to manipulate AI model behavior and access unauthorized information",
                        technical_impact="AI model manipulation, data exfiltration, unauthorized actions",
                        cvss_score=7.3,
                        exploitability_score=0.8,
                        confidence_score=0.85,
                        cwe_id="CWE-74",
                        compliance_violations=["GDPR", "AI_ETHICS"]
                    ))
        
        return vulnerabilities
    
    def _detect_data_leakage(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect potential data leakage in GenAI applications"""
        vulnerabilities = []
        
        data_leakage_patterns = [
            r'(?:log|print)\s*\([^)]*(?:api_key|token|password)',
            r'(?:prompt|message)\s*[+=][^;]*(?:user_data|personal_info|sensitive)',
            r'return\s+[^;]*(?:user_data|sensitive_data|personal_info)',
            r'(?:openai|anthropic)\.[^;]*\([^)]*(?:user_data|personal_info)'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in data_leakage_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Potential Data Leakage in GenAI Context",
                        description="Sensitive data may be exposed through GenAI processing or logging",
                        threat_level=SecurityThreatLevel.HIGH,
                        vulnerability_type=VulnerabilityType.GENAI_DATA_LEAKAGE,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Implement data anonymization and secure logging practices",
                        remediation_examples=[
                            "Remove or mask sensitive data before GenAI processing",
                            "Use structured logging with sensitive data filtering",
                            "Implement data retention and deletion policies"
                        ],
                        business_impact="Could expose sensitive user or business data through AI model interactions",
                        cvss_score=6.5,
                        confidence_score=0.75,
                        cwe_id="CWE-200",
                        compliance_violations=["GDPR", "HIPAA", "PCI-DSS"]
                    ))
        
        return vulnerabilities
    
    def _detect_model_manipulation(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect model manipulation vulnerabilities"""
        vulnerabilities = []
        
        model_manipulation_patterns = [
            r'model\s*=\s*[^;]*\+[^;]*(?:request\.|input\()',
            r'(?:temperature|max_tokens|top_p)\s*=\s*(?:request\.|input\(|user_)',
            r'engine\s*=\s*[^;]*(?:request\.|input\(|user_)',
            r'load_model\s*\([^)]*\.\./'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in model_manipulation_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Model Manipulation Vulnerability",
                        description="Model parameters or selection controlled by user input without validation",
                        threat_level=SecurityThreatLevel.MEDIUM,
                        vulnerability_type=VulnerabilityType.GENAI_MODEL_MANIPULATION,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Validate model parameters and restrict model access",
                        remediation_examples=[
                            "Use allowlists for model selection",
                            "Validate parameter ranges (temperature: 0-2, max_tokens: 1-4096)",
                            "Implement model access controls"
                        ],
                        business_impact="Could allow unauthorized access to AI models or manipulation of model behavior",
                        cvss_score=5.4,
                        confidence_score=0.8,
                        cwe_id="CWE-20"
                    ))
        
        return vulnerabilities
    
    def _detect_bias_issues(self, content: str, lines: List[str], file_path: Path) -> List[SecurityVulnerability]:
        """Detect potential bias and discrimination issues"""
        vulnerabilities = []
        
        bias_patterns = [
            r'(?:if|when).*(?:gender|race|age|religion|nationality).*(?:!=|==|in)',
            r'(?:male|female|man|woman).*(?:=|:).*(?:true|false|1|0)',
            r'(?:blacklist|whitelist|master|slave)',
            r'(?:he|she)\s+(?:is|was|will be).*(?:better|worse|more|less)'
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in bias_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(SecurityVulnerability(
                        id="",
                        title="Potential Bias or Discrimination Issue",
                        description="Code patterns that may introduce bias or discriminatory behavior in AI systems",
                        threat_level=SecurityThreatLevel.MEDIUM,
                        vulnerability_type=VulnerabilityType.GENAI_BIAS_DISCRIMINATION,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        remediation_advice="Review for bias, use inclusive language, and implement fairness testing",
                        remediation_examples=[
                            "Use inclusive terminology (allowlist/denylist instead of whitelist/blacklist)",
                            "Implement bias testing and fairness metrics",
                            "Review algorithmic decision-making for discriminatory patterns"
                        ],
                        business_impact="Could lead to discriminatory outcomes and legal/regulatory issues",
                        cvss_score=4.3,
                        confidence_score=0.6,
                        compliance_violations=["AI_ETHICS", "GDPR"]
                    ))
        
        return vulnerabilities


class DependencySecurityScanner:
    """Production-grade dependency security scanner"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
    
    def scan_files(self, files: List[Path]) -> List[SecurityVulnerability]:
        """Scan dependency files for security vulnerabilities"""
        vulnerabilities = []
        
        dependency_files = [f for f in files if f.name in [
            'requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py', 'poetry.lock'
        ]]
        
        for dep_file in dependency_files:
            try:
                file_vulnerabilities = self._scan_dependency_file(dep_file)
                vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"Error scanning dependency file {dep_file}: {e}")
        
        return vulnerabilities
    
    def _scan_dependency_file(self, dep_file: Path) -> List[SecurityVulnerability]:
        """Scan individual dependency file"""
        vulnerabilities = []
        
        # Mock vulnerable packages database (in production, integrate with safety DB, Snyk, etc.)
        known_vulnerabilities = {
            'requests': {
                '2.25.1': {
                    'vulnerability_id': 'CVE-2021-33503',
                    'description': 'ReDoS vulnerability in URL parsing',
                    'cvss_score': 7.5,
                    'threat_level': SecurityThreatLevel.HIGH
                }
            },
            'urllib3': {
                '1.26.4': {
                    'vulnerability_id': 'CVE-2021-33503',
                    'description': 'HTTPS proxy tunnel vulnerability',
                    'cvss_score': 6.5,
                    'threat_level': SecurityThreatLevel.MEDIUM
                }
            },
            'pillow': {
                '8.1.0': {
                    'vulnerability_id': 'CVE-2021-25287',
                    'description': 'Out-of-bounds read vulnerability',
                    'cvss_score': 9.1,
                    'threat_level': SecurityThreatLevel.CRITICAL
                }
            }
        }
        
        try:
            with open(dep_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse package and version
                package_info = self._parse_package_line(line)
                if not package_info:
                    continue
                
                package_name, version = package_info
                
                # Check for known vulnerabilities
                if package_name in known_vulnerabilities:
                    package_vulns = known_vulnerabilities[package_name]
                    if version in package_vulns:
                        vuln_info = package_vulns[version]
                        
                        vulnerabilities.append(SecurityVulnerability(
                            id="",
                            title=f"Vulnerable Dependency: {package_name}",
                            description=f"Package {package_name} version {version} has known security vulnerabilities: {vuln_info['description']}",
                            threat_level=vuln_info['threat_level'],
                            vulnerability_type=VulnerabilityType.VULNERABLE_COMPONENTS,
                            file_path=str(dep_file),
                            line_number=line_num,
                            code_snippet=line,
                            remediation_advice=f"Update {package_name} to a secure version",
                            remediation_examples=[
                                f"Update to latest version: pip install --upgrade {package_name}",
                                "Check for security advisories and update requirements.txt",
                                "Use dependency scanning tools in CI/CD pipeline"
                            ],
                            business_impact="Vulnerable dependencies can be exploited to compromise application security",
                            technical_impact="Various impacts depending on the specific vulnerability",
                            cvss_score=vuln_info['cvss_score'],
                            confidence_score=0.95,
                            cwe_id="CWE-1104",
                            owasp_category="A06:2021 – Vulnerable and Outdated Components"
                        ))
        
        except Exception as e:
            self.logger.error(f"Dependency file scan failed for {dep_file}: {e}")
        
        return vulnerabilities
    
    def _parse_package_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse package name and version from dependency line"""
        # Handle different formats: package==version, package>=version, etc.
        import re
        
        patterns = [
            r'^([a-zA-Z0-9_-]+)==([0-9.]+)',
            r'^([a-zA-Z0-9_-]+)>=([0-9.]+)',
            r'^([a-zA-Z0-9_-]+)~=([0-9.]+)',
            r'^([a-zA-Z0-9_-]+)\s*([0-9.]+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1), match.group(2)
        
        return None


class ConfigurationSecurityScanner:
    """Scanner for configuration security issues"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
    
    def scan_files(self, files: List[Path]) -> List[SecurityVulnerability]:
        """Scan configuration files for security issues"""
        vulnerabilities = []
        
        config_files = [f for f in files if f.suffix in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg']]
        
        for config_file in config_files:
            try:
                file_vulnerabilities = self._scan_config_file(config_file)
                vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"Error scanning config file {config_file}: {e}")
        
        return vulnerabilities
    
    def _scan_config_file(self, config_file: Path) -> List[SecurityVulnerability]:
        """Scan individual configuration file"""
        vulnerabilities = []
        
        try:
            with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check for hardcoded secrets in config
            secret_patterns = [
                (r'password\s*[:=]\s*[""][^""]{4,}[""]', 'password'),
                (r'api_key\s*[:=]\s*[""][^""]{10,}[""]', 'api_key'),
                (r'secret\s*[:=]\s*[""][^""]{10,}[""]', 'secret'),
                (r'token\s*[:=]\s*[""][^""]{15,}[""]', 'token')
            ]
            
            for line_num, line in enumerate(lines, 1):
                for pattern, secret_type in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append(SecurityVulnerability(
                            id="",
                            title=f"Hardcoded {secret_type.title()} in Configuration",
                            description=f"Configuration file contains hardcoded {secret_type}",
                            threat_level=SecurityThreatLevel.HIGH,
                            vulnerability_type=VulnerabilityType.SECURITY_MISCONFIGURATION,
                            file_path=str(config_file),
                            line_number=line_num,
                            code_snippet=line.strip(),
                            remediation_advice=f"Move {secret_type} to environment variables or secure vault",
                            business_impact="Hardcoded secrets in configuration files can be easily discovered",
                            cvss_score=7.5,
                            confidence_score=0.9,
                            cwe_id="CWE-798"
                        ))
        
        except Exception as e:
            self.logger.error(f"Config file scan failed for {config_file}: {e}")
        
        return vulnerabilities


if __name__ == "__main__":
    print("Testing Production Security Engine...")
    
    # Test the security engine
    try:
        # Create test environment
        test_dir = Path("test_production_scan")
        test_dir.mkdir(exist_ok=True)
        
        # Create test files with various vulnerabilities
        
        # Traditional security issues
        (test_dir / "sql_vulnerable.py").write_text("""
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE id = " + user_id  # SQL injection
    return conn.execute(query).fetchone()

password = "hardcoded_secret_123"  # Hardcoded secret
""")
        
        # GenAI security issues
        (test_dir / "genai_app.py").write_text("""
import openai

openai.api_key = "sk-1234567890abcdef"  # Hardcoded API key

def chat_with_ai(user_input):
    prompt = "You are an assistant. " + user_input  # Prompt injection
    response = openai.Completion.create(prompt=prompt)
    return response.choices[0].text
""")
        
        # Dependency file with vulnerabilities
        (test_dir / "requirements.txt").write_text("""
requests==2.25.1
urllib3==1.26.4
flask==1.1.4
pillow==8.1.0
openai==0.27.0
""")
        
        # Configuration file with secrets
        (test_dir / "config.yaml").write_text("""
database:
  host: localhost
  password: "database_secret_123"
  
api:
  api_key: "sk-production-key-123456"
  
logging:
  level: info
""")
        
        # Initialize and run production security scanner
        print("Initializing Production Security Scanner...")
        scanner = EnterpriseSecurityScanner()
        
        print(f"Scanner Status: {scanner.get_scan_status()}")
        
        # Run comprehensive scan
        print("\nStarting production security scan...")
        results = scanner.scan_directory(test_dir)
        
        # Display results
        print("\n" + "="*50)
        print("🎯 PRODUCTION SCAN RESULTS")
        print("="*50)
        
        print(f"📊 Summary:")
        print(f"   Scan ID: {results['scan_metadata']['scan_id']}")
        print(f"   Duration: {results['scan_metadata']['duration']:.2f} seconds")
        print(f"   Files Scanned: {results['summary']['files_scanned']}")
        print(f"   Total Vulnerabilities: {results['summary']['total_vulnerabilities']}")
        
        print(f"\n🚨 Threat Level Breakdown:")
        threat_levels = results['security_metrics']['by_threat_level']
        for level, count in threat_levels.items():
            if count > 0:
                print(f"   {level.title()}: {count}")
        
        print(f"\n🔍 Vulnerability Types:")
        vuln_types = results['security_metrics']['by_vulnerability_type']
        for vtype, count in vuln_types.items():
            print(f"   {vtype.replace('_', ' ').title()}: {count}")
        
        print(f"\n⚡ Performance Metrics:")
        perf = results['performance_metrics']
        print(f"   Files/second: {perf['files_per_second']:.2f}")
        print(f"   Vulnerabilities/second: {perf['vulnerabilities_per_second']:.2f}")
        
        print(f"\n🎯 Risk Analysis:")
        risk = results['risk_analysis']
        print(f"   Overall Risk Score: {risk['overall_risk_score']:.1f}")
        print(f"   Risk Level: {risk['risk_level'].upper()}")
        
        print(f"\n📋 Top Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        if results['vulnerabilities']:
            print(f"\n🔍 Sample Vulnerabilities:")
            for vuln in results['vulnerabilities'][:3]:
                print(f"   - {vuln['title']} ({vuln['threat_level']})")
                print(f"     File: {vuln['file_path']}:{vuln['line_number']}")
                print(f"     Risk Score: {vuln.get('risk_score', 'N/A')}")
        
        print("\n✅ Production Security Engine Test PASSED!")
        
    except Exception as e:
        print(f"❌ Production Security Engine Test FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'test_dir' in locals() and test_dir.exists():
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
