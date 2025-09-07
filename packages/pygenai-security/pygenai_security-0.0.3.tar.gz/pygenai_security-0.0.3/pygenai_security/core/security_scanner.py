"""
Core PyGenAI Security Scanner
Production-ready security scanning engine with enterprise features.
"""

import os
import sys
import time
import logging
import threading
import asyncio
import hashlib
import json
import signal
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from .vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory
from .config_manager import ConfigManager
from .exceptions import ScanError, ConfigurationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ScanMode(Enum):
    """Scanning modes for different use cases"""
    FAST = "fast"           # Quick scan with basic checks
    STANDARD = "standard"   # Standard comprehensive scan
    THOROUGH = "thorough"   # Deep scan with all checks
    COMPLIANCE = "compliance" # Compliance-focused scan
    GENAI_FOCUS = "genai_focus" # GenAI security focused


class PyGenAIScanner:
    """
    Production-ready PyGenAI Security Scanner
    
    A comprehensive security scanner for Python and GenAI applications with:
    - Traditional Python security vulnerabilities
    - GenAI-specific security issues (prompt injection, data leakage, etc.)
    - Enterprise features and compliance reporting
    - Real-time monitoring and analytics
    - VS Code integration support
    """
    
    def __init__(self, config: Optional[Union[Dict[str, Any], ConfigManager]] = None):
        """
        Initialize PyGenAI Security Scanner
        
        Args:
            config: Configuration dictionary or ConfigManager instance
        """
        # Initialize configuration
        if isinstance(config, ConfigManager):
            self.config = config
        else:
            self.config = ConfigManager(config or {})
        
        # Scanner metadata
        self.scanner_id = str(uuid.uuid4())
        self.version = "1.0.0"
        self.start_time = time.time()
        
        # Scanning state
        self.is_scanning = False
        self.current_scan_id = None
        self._scan_lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Results storage
        self.vulnerabilities: List[Vulnerability] = []
        self.scan_statistics = {}
        
        # Enterprise features
        self.enterprise_enabled = self.config.get('enterprise.enabled', False)
        self.license_valid = self._validate_license()
        
        # Performance settings
        self.max_workers = self.config.get('performance.max_workers', 4)
        self.scan_timeout = self.config.get('performance.scan_timeout', 3600)
        self.file_size_limit = self.config.get('performance.file_size_limit_mb', 50) * 1024 * 1024
        
        # Initialize components
        self._setup_logging()
        self._initialize_scanners()
        self._setup_signal_handlers()
        
        logger.info(f"PyGenAI Scanner initialized (ID: {self.scanner_id})")
    
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        log_config = self.config.get('logging', {})
        
        # Create specialized loggers
        self.security_logger = get_logger('pygenai_security.security_events')
        self.audit_logger = get_logger('pygenai_security.audit')
        self.performance_logger = get_logger('pygenai_security.performance')
        
        # Set log levels
        log_level = log_config.get('level', 'INFO')
        for log in [self.security_logger, self.audit_logger, self.performance_logger]:
            log.setLevel(getattr(logging, log_level.upper()))
    
    def _initialize_scanners(self):
        """Initialize all security scanners"""
        self.scanners = {}
        enabled_scanners = self.config.get('scanners.enabled', [
            'traditional_python', 'genai_security', 'dependency_check', 'configuration_audit'
        ])
        
        # Import and initialize scanner modules
        scanner_mapping = {
            'traditional_python': 'TraditionalPythonScanner',
            'genai_security': 'GenAISecurityScanner', 
            'dependency_check': 'DependencyScanner',
            'configuration_audit': 'ConfigurationScanner',
            'secrets_detection': 'SecretsScanner',
            'code_quality': 'CodeQualityScanner'
        }
        
        for scanner_name in enabled_scanners:
            try:
                if scanner_name in scanner_mapping:
                    # Dynamic import (in production, use static imports)
                    scanner_class = self._get_scanner_class(scanner_name)
                    scanner_config = self.config.get(f'scanners.{scanner_name}', {})
                    self.scanners[scanner_name] = scanner_class(scanner_config)
                    logger.info(f"Initialized {scanner_name} scanner")
            except Exception as e:
                logger.error(f"Failed to initialize {scanner_name} scanner: {e}")
                if self.config.get('strict_mode', False):
                    raise ConfigurationError(f"Required scanner {scanner_name} failed to initialize")
        
        if not self.scanners:
            raise ConfigurationError("No scanners could be initialized")
        
        logger.info(f"Initialized {len(self.scanners)} security scanners")
    
    def _get_scanner_class(self, scanner_name: str):
        """Get scanner class (mock implementation for demo)"""
        # In production, import from actual scanner modules
        from ..scanners.traditional_scanner import TraditionalPythonScanner
        from ..scanners.genai_scanner import GenAISecurityScanner
        from ..scanners.dependency_scanner import DependencyScanner
        from ..scanners.configuration_scanner import ConfigurationScanner
        
        scanner_classes = {
            'traditional_python': TraditionalPythonScanner,
            'genai_security': GenAISecurityScanner,
            'dependency_check': DependencyScanner,
            'configuration_audit': ConfigurationScanner
        }
        
        return scanner_classes.get(scanner_name)
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            self.stop_scan()
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def scan_directory(self, 
                      directory_path: Union[str, Path],
                      scan_mode: Union[str, ScanMode] = ScanMode.STANDARD,
                      include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None,
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scan directory for security vulnerabilities
        
        Args:
            directory_path: Directory to scan
            scan_mode: Scanning mode (fast, standard, thorough, compliance, genai_focus)
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude  
            progress_callback: Progress callback function
            
        Returns:
            Comprehensive scan results dictionary
        """
        # Validate inputs
        directory = Path(directory_path).resolve()
        if not directory.exists() or not directory.is_dir():
            raise ScanError(f"Invalid directory: {directory_path}")
        
        if isinstance(scan_mode, str):
            scan_mode = ScanMode(scan_mode)
        
        # Check licensing for enterprise features
        if scan_mode == ScanMode.COMPLIANCE and not self._validate_enterprise_license():
            raise ScanError("Compliance scanning requires valid enterprise license")
        
        with self._scan_context():
            try:
                scan_start = time.time()
                self.current_scan_id = str(uuid.uuid4())
                
                # Log scan initiation
                self.audit_logger.info(f"Scan started - ID: {self.current_scan_id}, Directory: {directory}")
                
                # Configure scanners based on mode
                self._configure_scanners_for_mode(scan_mode)
                
                # Discover files to scan
                files_to_scan = self._discover_scannable_files(directory, include_patterns, exclude_patterns)
                
                if not files_to_scan:
                    logger.warning(f"No scannable files found in {directory}")
                    return self._create_empty_results(scan_start)
                
                logger.info(f"Starting {scan_mode.value} scan of {len(files_to_scan)} files")
                
                # Initialize progress tracking
                progress_tracker = ScanProgressTracker(len(files_to_scan), progress_callback)
                
                # Clear previous results
                self.vulnerabilities.clear()
                
                # Execute scan based on mode
                scan_results = self._execute_scan(files_to_scan, scan_mode, progress_tracker)
                
                # Generate comprehensive results
                results = self._generate_scan_results(scan_start, scan_results, scan_mode)
                
                # Log completion
                scan_duration = time.time() - scan_start
                self.audit_logger.info(f"Scan completed - ID: {self.current_scan_id}, Duration: {scan_duration:.2f}s, Vulnerabilities: {results['summary']['total_vulnerabilities']}")
                
                return results
                
            except Exception as e:
                self.security_logger.error(f"Scan failed - ID: {self.current_scan_id}, Error: {str(e)}")
                raise ScanError(f"Scan execution failed: {str(e)}") from e
    
    def scan_file(self, file_path: Union[str, Path]) -> List[Vulnerability]:
        """
        Scan single file for vulnerabilities
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            List of vulnerabilities found
        """
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            raise ScanError(f"Invalid file: {file_path}")
        
        if not self._is_scannable_file(file_path):
            return []
        
        vulnerabilities = []
        
        for scanner_name, scanner in self.scanners.items():
            try:
                file_vulns = scanner.scan_file(file_path)
                vulnerabilities.extend(file_vulns)
            except Exception as e:
                logger.error(f"Scanner {scanner_name} failed on file {file_path}: {e}")
        
        return vulnerabilities
    
    def _configure_scanners_for_mode(self, scan_mode: ScanMode):
        """Configure scanners based on scan mode"""
        mode_configs = {
            ScanMode.FAST: {
                'quick_scan': True,
                'skip_advanced_checks': True,
                'confidence_threshold': 0.8
            },
            ScanMode.STANDARD: {
                'comprehensive_scan': True,
                'confidence_threshold': 0.7
            },
            ScanMode.THOROUGH: {
                'deep_scan': True,
                'advanced_analysis': True,
                'confidence_threshold': 0.5
            },
            ScanMode.COMPLIANCE: {
                'compliance_checks': True,
                'regulatory_focus': True,
                'detailed_reporting': True
            },
            ScanMode.GENAI_FOCUS: {
                'genai_priority': True,
                'ai_model_analysis': True,
                'prompt_security': True
            }
        }
        
        mode_config = mode_configs.get(scan_mode, mode_configs[ScanMode.STANDARD])
        
        for scanner in self.scanners.values():
            if hasattr(scanner, 'configure'):
                scanner.configure(mode_config)
    
    def _discover_scannable_files(self, 
                                 directory: Path, 
                                 include_patterns: Optional[List[str]], 
                                 exclude_patterns: Optional[List[str]]) -> List[Path]:
        """Discover files that can be scanned"""
        
        if include_patterns is None:
            include_patterns = ['*.py', '*.pyw', '*.pyi']
        
        if exclude_patterns is None:
            exclude_patterns = [
                '*.pyc', '__pycache__/*', '.git/*', '.svn/*',
                '.venv/*', 'venv/*', 'env/*', 'virtualenv/*', 
                'node_modules/*', '.tox/*', 'build/*', 'dist/*',
                '.pytest_cache/*', '*.egg-info/*', '.mypy_cache/*',
                'htmlcov/*', '.coverage.*', '.DS_Store', 'Thumbs.db'
            ]
        
        discovered_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Filter directories early
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
            raise ScanError(f"Failed to discover files in {directory}: {e}")
        
        return sorted(discovered_files)
    
    def _matches_include_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches include patterns"""
        import fnmatch
        return any(
            fnmatch.fnmatch(file_path, pattern) or 
            fnmatch.fnmatch(os.path.basename(file_path), pattern)
            for pattern in patterns
        )
    
    def _matches_exclude_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches exclude patterns"""
        import fnmatch
        return any(
            fnmatch.fnmatch(file_path, pattern) or
            fnmatch.fnmatch(os.path.basename(file_path), pattern)
            for pattern in patterns
        )
    
    def _is_scannable_file(self, file_path: Path) -> bool:
        """Check if file can be scanned"""
        try:
            # Check file size
            if file_path.stat().st_size > self.file_size_limit:
                logger.debug(f"Skipping large file: {file_path}")
                return False
            
            # Check file accessibility and encoding
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)  # Try to read first 1KB
            
            return True
            
        except (OSError, IOError, PermissionError) as e:
            logger.debug(f"Cannot access file {file_path}: {e}")
            return False
    
    def _execute_scan(self, 
                     files_to_scan: List[Path],
                     scan_mode: ScanMode,
                     progress_tracker) -> Dict[str, Any]:
        """Execute the actual security scan"""
        
        scan_results = {
            'files_processed': 0,
            'total_vulnerabilities': 0,
            'scanner_results': {},
            'scan_errors': [],
            'performance_data': {}
        }
        
        # Parallel execution for better performance
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_scanner = {}
            
            # Submit scanner tasks
            for scanner_name, scanner in self.scanners.items():
                if self._shutdown_event.is_set():
                    break
                
                future = executor.submit(
                    self._execute_scanner_with_monitoring,
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
                    scanner_result = future.result(timeout=120)  # 2 minute per-scanner timeout
                    
                    # Store scanner results
                    scan_results['scanner_results'][scanner_name] = scanner_result
                    scan_results['total_vulnerabilities'] += len(scanner_result.get('vulnerabilities', []))
                    
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
                    scan_results['scan_errors'].append({
                        'scanner': scanner_name, 
                        'error': error_msg,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
        
        scan_results['files_processed'] = len(files_to_scan)
        scan_results['completed_scanners'] = completed_scanners
        
        return scan_results
    
    def _execute_scanner_with_monitoring(self,
                                       scanner_name: str,
                                       scanner,
                                       files_to_scan: List[Path],
                                       progress_tracker) -> Dict[str, Any]:
        """Execute individual scanner with performance monitoring"""
        
        scanner_start = time.time()
        
        try:
            # Update progress
            progress_tracker.update_current_scanner(scanner_name)
            
            # Execute scanner
            if hasattr(scanner, 'scan_files'):
                vulnerabilities = scanner.scan_files(files_to_scan)
            else:
                # Fallback to file-by-file scanning
                vulnerabilities = []
                for file_path in files_to_scan:
                    try:
                        file_vulns = scanner.scan_file(file_path)
                        vulnerabilities.extend(file_vulns)
                    except Exception as e:
                        logger.debug(f"Scanner {scanner_name} failed on file {file_path}: {e}")
            
            scanner_duration = time.time() - scanner_start
            
            # Log performance
            self.performance_logger.info(f"Scanner {scanner_name}: {len(vulnerabilities)} vulnerabilities in {scanner_duration:.2f}s")
            
            return {
                'vulnerabilities': vulnerabilities,
                'duration': scanner_duration,
                'files_processed': len(files_to_scan),
                'success_rate': 1.0,
                'performance_metrics': {
                    'files_per_second': len(files_to_scan) / scanner_duration if scanner_duration > 0 else 0,
                    'vulnerabilities_per_second': len(vulnerabilities) / scanner_duration if scanner_duration > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Scanner {scanner_name} execution failed: {e}")
            raise
    
    def _generate_scan_results(self, 
                              scan_start: float,
                              scan_results: Dict[str, Any],
                              scan_mode: ScanMode) -> Dict[str, Any]:
        """Generate comprehensive scan results"""
        
        scan_duration = time.time() - scan_start
        
        # Process and filter vulnerabilities
        processed_vulnerabilities = self._process_vulnerabilities()
        
        # Calculate security metrics
        security_metrics = self._calculate_security_metrics(processed_vulnerabilities)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(processed_vulnerabilities, security_metrics)
        
        # Compliance analysis (if enterprise enabled)
        compliance_analysis = {}
        if self.enterprise_enabled:
            compliance_analysis = self._analyze_compliance(processed_vulnerabilities)
        
        # Risk analysis
        risk_analysis = self._calculate_risk_analysis(processed_vulnerabilities)
        
        return {
            'scan_metadata': {
                'scan_id': self.current_scan_id,
                'scanner_id': self.scanner_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'duration': scan_duration,
                'scan_mode': scan_mode.value,
                'scanner_version': self.version,
                'framework_version': '1.0.0'
            },
            'summary': {
                'total_vulnerabilities': len(processed_vulnerabilities),
                'files_scanned': scan_results.get('files_processed', 0),
                'scanners_executed': list(scan_results.get('scanner_results', {}).keys()),
                'scan_errors': scan_results.get('scan_errors', []),
                'success_rate': self._calculate_success_rate(scan_results)
            },
            'vulnerabilities': [vuln.to_dict() for vuln in processed_vulnerabilities],
            'security_metrics': security_metrics,
            'risk_analysis': risk_analysis,
            'recommendations': recommendations,
            'compliance_analysis': compliance_analysis,
            'performance_metrics': {
                'scan_duration': scan_duration,
                'files_per_second': scan_results.get('files_processed', 0) / scan_duration if scan_duration > 0 else 0,
                'vulnerabilities_per_second': len(processed_vulnerabilities) / scan_duration if scan_duration > 0 else 0,
                'scanner_performance': {
                    name: result.get('performance_metrics', {})
                    for name, result in scan_results.get('scanner_results', {}).items()
                }
            },
            'enterprise_features': {
                'enabled': self.enterprise_enabled,
                'license_valid': self.license_valid,
                'compliance_reporting': bool(compliance_analysis),
                'advanced_analytics': self.enterprise_enabled
            }
        }
    
    def _process_vulnerabilities(self) -> List[Vulnerability]:
        """Process, deduplicate, and filter vulnerabilities"""
        
        # Remove duplicates based on file, line, and vulnerability type
        seen_vulnerabilities = set()
        unique_vulnerabilities = []
        
        for vuln in self.vulnerabilities:
            vuln_signature = (vuln.file_path, vuln.line_number, vuln.category.value, vuln.title)
            if vuln_signature not in seen_vulnerabilities:
                seen_vulnerabilities.add(vuln_signature)
                unique_vulnerabilities.append(vuln)
        
        # Apply filtering based on configuration
        filtered_vulnerabilities = []
        
        min_threat_level = ThreatLevel(self.config.get('filtering.min_threat_level', 'medium'))
        confidence_threshold = self.config.get('filtering.confidence_threshold', 0.7)
        exclude_false_positives = self.config.get('filtering.exclude_false_positives', True)
        
        for vuln in unique_vulnerabilities:
            # Filter by threat level
            if vuln.threat_level.value < min_threat_level.value:
                continue
            
            # Filter by confidence
            if vuln.confidence < confidence_threshold:
                continue
            
            # Filter false positives
            if exclude_false_positives and hasattr(vuln, 'false_positive_probability') and vuln.false_positive_probability > 0.5:
                continue
            
            filtered_vulnerabilities.append(vuln)
        
        return filtered_vulnerabilities
    
    def _calculate_security_metrics(self, vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        """Calculate comprehensive security metrics"""
        
        if not vulnerabilities:
            return {
                'by_threat_level': {level.name.lower(): 0 for level in ThreatLevel},
                'by_category': {cat.value: 0 for cat in VulnerabilityCategory},
                'by_scanner': {},
                'summary_statistics': {
                    'total_risk_score': 0.0,
                    'average_confidence': 0.0,
                    'affected_files': 0
                }
            }
        
        metrics = {
            'by_threat_level': {level.name.lower(): 0 for level in ThreatLevel},
            'by_category': {cat.value: 0 for cat in VulnerabilityCategory},
            'by_scanner': {},
            'affected_files': len(set(vuln.file_path for vuln in vulnerabilities))
        }
        
        # Count by categories
        confidence_scores = []
        risk_scores = []
        
        for vuln in vulnerabilities:
            # Threat level counts
            metrics['by_threat_level'][vuln.threat_level.name.lower()] += 1
            
            # Category counts
            metrics['by_category'][vuln.category.value] += 1
            
            # Scanner counts
            scanner = getattr(vuln, 'scanner_name', 'unknown')
            if scanner not in metrics['by_scanner']:
                metrics['by_scanner'][scanner] = 0
            metrics['by_scanner'][scanner] += 1
            
            # Collect scores
            confidence_scores.append(vuln.confidence)
            if hasattr(vuln, 'risk_score'):
                risk_scores.append(vuln.risk_score)
        
        # Summary statistics
        metrics['summary_statistics'] = {
            'total_risk_score': sum(risk_scores),
            'average_risk_score': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'affected_files': metrics['affected_files'],
            'vulnerability_density': len(vulnerabilities) / max(1, metrics['affected_files'])
        }
        
        return metrics
    
    def _calculate_risk_analysis(self, vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        """Calculate risk analysis"""
        
        if not vulnerabilities:
            return {
                'overall_risk_level': 'low',
                'risk_score': 0.0,
                'top_risks': [],
                'mitigation_priority': []
            }
        
        # Calculate overall risk
        threat_level_weights = {
            ThreatLevel.CRITICAL: 10,
            ThreatLevel.HIGH: 7,
            ThreatLevel.MEDIUM: 4,
            ThreatLevel.LOW: 2,
            ThreatLevel.INFO: 1
        }
        
        risk_score = sum(threat_level_weights.get(vuln.threat_level, 1) for vuln in vulnerabilities)
        avg_risk = risk_score / len(vulnerabilities)
        
        # Determine overall risk level
        if avg_risk >= 8:
            overall_risk_level = 'critical'
        elif avg_risk >= 6:
            overall_risk_level = 'high'
        elif avg_risk >= 4:
            overall_risk_level = 'medium'
        else:
            overall_risk_level = 'low'
        
        # Top risks (highest threat level vulnerabilities)
        top_risks = sorted(vulnerabilities, key=lambda v: threat_level_weights.get(v.threat_level, 1), reverse=True)[:5]
        
        return {
            'overall_risk_level': overall_risk_level,
            'risk_score': risk_score,
            'average_risk': avg_risk,
            'top_risks': [
                {
                    'id': vuln.id,
                    'title': vuln.title,
                    'threat_level': vuln.threat_level.name.lower(),
                    'file_path': vuln.file_path,
                    'line_number': vuln.line_number
                }
                for vuln in top_risks
            ],
            'mitigation_priority': self._generate_mitigation_priority(vulnerabilities)
        }
    
    def _generate_mitigation_priority(self, vulnerabilities: List[Vulnerability]) -> List[Dict[str, Any]]:
        """Generate mitigation priority recommendations"""
        
        priorities = []
        
        # Critical vulnerabilities first
        critical_vulns = [v for v in vulnerabilities if v.threat_level == ThreatLevel.CRITICAL]
        if critical_vulns:
            priorities.append({
                'priority': 1,
                'category': 'Critical Security Issues',
                'count': len(critical_vulns),
                'timeframe': '24 hours',
                'recommendation': 'Address immediately - these pose severe security risks'
            })
        
        # Injection vulnerabilities
        injection_vulns = [v for v in vulnerabilities if 'injection' in v.category.value.lower()]
        if injection_vulns:
            priorities.append({
                'priority': 2,
                'category': 'Injection Vulnerabilities',
                'count': len(injection_vulns),
                'timeframe': '1 week',
                'recommendation': 'High priority - injection attacks can lead to data breaches'
            })
        
        # GenAI specific vulnerabilities
        genai_vulns = [v for v in vulnerabilities if v.category in [
            VulnerabilityCategory.GENAI_PROMPT_INJECTION, 
            VulnerabilityCategory.GENAI_DATA_LEAKAGE,
            VulnerabilityCategory.GENAI_MODEL_MANIPULATION
        ]]
        if genai_vulns:
            priorities.append({
                'priority': 3,
                'category': 'GenAI Security Issues',
                'count': len(genai_vulns),
                'timeframe': '2 weeks',
                'recommendation': 'Emerging threat - secure AI/ML components against manipulation'
            })
        
        return priorities
    
    def _generate_recommendations(self, 
                                vulnerabilities: List[Vulnerability], 
                                security_metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable security recommendations"""
        
        recommendations = []
        
        if not vulnerabilities:
            return ["Excellent! No security vulnerabilities detected. Continue regular security scanning."]
        
        # Critical vulnerability recommendations
        critical_count = security_metrics.get('by_threat_level', {}).get('critical', 0)
        if critical_count > 0:
            recommendations.append(
                f"🚨 URGENT: {critical_count} critical vulnerabilities require immediate attention within 24 hours."
            )
        
        # High vulnerability recommendations  
        high_count = security_metrics.get('by_threat_level', {}).get('high', 0)
        if high_count > 0:
            recommendations.append(
                f"⚠️ HIGH PRIORITY: {high_count} high-severity vulnerabilities should be addressed within 1 week."
            )
        
        # Category-specific recommendations
        categories = security_metrics.get('by_category', {})
        
        if categories.get('injection', 0) > 0:
            recommendations.append(
                f"🛡️ INJECTION PROTECTION: {categories['injection']} injection vulnerabilities found. "
                "Implement input validation, parameterized queries, and output encoding."
            )
        
        if categories.get('genai_prompt_injection', 0) + categories.get('genai_data_leakage', 0) > 0:
            genai_total = categories.get('genai_prompt_injection', 0) + categories.get('genai_data_leakage', 0)
            recommendations.append(
                f"🤖 GENAI SECURITY: {genai_total} AI/ML security issues detected. "
                "Review prompt handling, model access controls, and data sanitization."
            )
        
        # General recommendations
        if len(vulnerabilities) > 20:
            recommendations.append(
                "📊 CODE QUALITY: High number of vulnerabilities suggests need for security training "
                "and secure coding practices implementation."
            )
        
        return recommendations
    
    def _analyze_compliance(self, vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        """Analyze compliance impact (enterprise feature)"""
        
        if not self.enterprise_enabled:
            return {}
        
        compliance_frameworks = self.config.get('enterprise.compliance_frameworks', [
            'OWASP_TOP_10', 'CWE_TOP_25', 'PCI_DSS', 'GDPR', 'HIPAA', 'SOX'
        ])
        
        compliance_analysis = {}
        
        for framework in compliance_frameworks:
            framework_violations = []
            
            for vuln in vulnerabilities:
                # Map vulnerabilities to compliance frameworks
                if hasattr(vuln, 'compliance_mappings'):
                    if framework in vuln.compliance_mappings:
                        framework_violations.append(vuln)
            
            compliance_analysis[framework] = {
                'total_violations': len(framework_violations),
                'by_severity': {
                    level.name.lower(): len([v for v in framework_violations if v.threat_level == level])
                    for level in ThreatLevel
                },
                'compliance_score': max(0, 100 - (len(framework_violations) * 5))  # Simple scoring
            }
        
        return compliance_analysis
    
    def _calculate_success_rate(self, scan_results: Dict[str, Any]) -> float:
        """Calculate scan success rate"""
        total_scanners = len(self.scanners)
        successful_scanners = scan_results.get('completed_scanners', 0)
        
        return (successful_scanners / total_scanners) * 100 if total_scanners > 0 else 0
    
    def _validate_license(self) -> bool:
        """Validate software license (placeholder)"""
        # In production, implement actual license validation
        return True
    
    def _validate_enterprise_license(self) -> bool:
        """Validate enterprise license (placeholder)"""
        # In production, implement enterprise license validation
        return self.enterprise_enabled
    
    def _create_empty_results(self, scan_start: float) -> Dict[str, Any]:
        """Create empty results when no files found"""
        return {
            'scan_metadata': {
                'scan_id': self.current_scan_id,
                'scanner_id': self.scanner_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'duration': time.time() - scan_start,
                'scanner_version': self.version
            },
            'summary': {
                'total_vulnerabilities': 0,
                'files_scanned': 0,
                'scanners_executed': [],
                'scan_errors': []
            },
            'vulnerabilities': [],
            'security_metrics': {
                'by_threat_level': {level.name.lower(): 0 for level in ThreatLevel},
                'by_category': {cat.value: 0 for cat in VulnerabilityCategory}
            },
            'recommendations': ["No scannable files found in the specified directory"]
        }
    
    def _scan_context(self):
        """Context manager for scan operations"""
        class ScanContext:
            def __init__(self, scanner):
                self.scanner = scanner
            
            def __enter__(self):
                if self.scanner.is_scanning:
                    raise ScanError("Another scan is already in progress")
                self.scanner.is_scanning = True
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.scanner.is_scanning = False
        
        return ScanContext(self)
    
    def stop_scan(self):
        """Stop current scan gracefully"""
        logger.info("Stopping scan gracefully...")
        self._shutdown_event.set()
        
        with self._scan_lock:
            self.is_scanning = False
    
    def get_scan_status(self) -> Dict[str, Any]:
        """Get current scanner status"""
        return {
            'scanner_id': self.scanner_id,
            'is_scanning': self.is_scanning,
            'current_scan_id': self.current_scan_id,
            'uptime': time.time() - self.start_time,
            'version': self.version,
            'enterprise_enabled': self.enterprise_enabled,
            'license_valid': self.license_valid,
            'available_scanners': list(self.scanners.keys()),
            'configuration_status': {
                'max_workers': self.max_workers,
                'scan_timeout': self.scan_timeout,
                'file_size_limit_mb': self.file_size_limit / (1024 * 1024)
            }
        }
    
    def get_scanner_info(self) -> Dict[str, Any]:
        """Get detailed scanner information"""
        return {
            'scanner_metadata': {
                'id': self.scanner_id,
                'version': self.version,
                'framework_version': '1.0.0',
                'author': 'RiteshGenAI',
                'repository': 'https://github.com/RiteshGenAI/pygenai-security'
            },
            'capabilities': {
                'traditional_python_security': True,
                'genai_security': True,
                'enterprise_features': self.enterprise_enabled,
                'real_time_monitoring': True,
                'compliance_reporting': self.enterprise_enabled,
                'vs_code_integration': True,
                'testsprite_mcp': True
            },
            'supported_file_types': ['.py', '.pyw', '.pyi'],
            'supported_frameworks': [
                'Flask', 'Django', 'FastAPI', 'OpenAI', 'Anthropic', 
                'HuggingFace', 'LangChain', 'LlamaIndex'
            ]
        }


class ScanProgressTracker:
    """Thread-safe scan progress tracking"""
    
    def __init__(self, total_files: int, callback: Optional[Callable] = None):
        self.total_files = total_files
        self.processed_files = 0
        self.current_scanner = ""
        self.start_time = time.time()
        self.callback = callback
        self._lock = threading.Lock()
    
    def update_current_scanner(self, scanner_name: str):
        """Update current scanner"""
        with self._lock:
            self.current_scanner = scanner_name
            self._notify_callback()
    
    def update_processed_files(self, count: int):
        """Update processed files count"""
        with self._lock:
            self.processed_files = count
            self._notify_callback()
    
    def _notify_callback(self):
        """Notify progress callback"""
        if self.callback:
            try:
                progress_data = {
                    'total_files': self.total_files,
                    'processed_files': self.processed_files,
                    'current_scanner': self.current_scanner,
                    'elapsed_time': time.time() - self.start_time,
                    'progress_percentage': (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0
                }
                self.callback(progress_data)
            except Exception as e:
                logger.debug(f"Progress callback failed: {e}")
