"""
Configuration Manager for PyGenAI Security Framework
Handles all configuration aspects with validation and enterprise features.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

from .exceptions import ConfigurationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScannerConfig:
    """Configuration for individual scanners"""
    enabled: bool = True
    rules: List[str] = field(default_factory=list)
    exclude_rules: List[str] = field(default_factory=list)
    severity_threshold: str = "medium"
    confidence_threshold: float = 0.7
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnterpriseConfig:
    """Enterprise-specific configuration"""
    enabled: bool = False
    license_key: str = ""
    compliance_frameworks: List[str] = field(default_factory=list)
    audit_logging: bool = True
    advanced_analytics: bool = False
    custom_reporting: bool = False
    sso_integration: bool = False


@dataclass
class IntegrationConfig:
    """External integrations configuration"""
    vscode_enabled: bool = True
    testsprite_mcp_enabled: bool = False
    testsprite_url: str = ""
    testsprite_api_key: str = ""
    webhook_url: str = ""
    slack_webhook: str = ""
    teams_webhook: str = ""


class ConfigManager:
    """
    Comprehensive configuration manager for PyGenAI Security Framework
    
    Handles loading, validation, and management of all configuration aspects
    including scanner settings, enterprise features, and integrations.
    """
    
    def __init__(self, config_data: Optional[Union[Dict[str, Any], str, Path]] = None):
        """
        Initialize configuration manager
        
        Args:
            config_data: Configuration data as dict, file path, or None for defaults
        """
        self.config: Dict[str, Any] = {}
        self.config_file_path: Optional[Path] = None
        
        # Load configuration
        if isinstance(config_data, (str, Path)):
            self.load_from_file(config_data)
        elif isinstance(config_data, dict):
            self.config = config_data.copy()
        else:
            self._load_default_config()
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration manager initialized")
    
    def _load_default_config(self):
        """Load default configuration"""
        self.config = {
            # Scanner Configuration
            'scanners': {
                'enabled': ['traditional_python', 'genai_security', 'dependency_check'],
                'traditional_python': ScannerConfig(
                    rules=['sql_injection', 'xss', 'command_injection', 'hardcoded_secrets', 'path_traversal'],
                    severity_threshold='medium',
                    confidence_threshold=0.8
                ).__dict__,
                'genai_security': ScannerConfig(
                    rules=['prompt_injection', 'data_leakage', 'model_manipulation', 'bias_detection'],
                    severity_threshold='medium',
                    confidence_threshold=0.7
                ).__dict__,
                'dependency_check': ScannerConfig(
                    rules=['known_vulnerabilities', 'license_issues', 'outdated_packages'],
                    severity_threshold='high',
                    confidence_threshold=0.9
                ).__dict__,
                'configuration_audit': ScannerConfig(
                    rules=['insecure_configs', 'exposed_secrets', 'weak_settings'],
                    severity_threshold='medium',
                    confidence_threshold=0.8
                ).__dict__
            },
            
            # Filtering and Processing
            'filtering': {
                'min_threat_level': 'medium',
                'confidence_threshold': 0.7,
                'exclude_false_positives': True,
                'deduplicate_vulnerabilities': True,
                'max_vulnerabilities_per_file': 50
            },
            
            # Performance Settings
            'performance': {
                'max_workers': 4,
                'scan_timeout': 3600,  # 1 hour
                'file_size_limit_mb': 50,
                'enable_parallel_scanning': True,
                'memory_limit_mb': 1024
            },
            
            # Enterprise Features
            'enterprise': EnterpriseConfig(
                compliance_frameworks=['OWASP_TOP_10', 'CWE_TOP_25', 'PCI_DSS']
            ).__dict__,
            
            # Integrations
            'integrations': IntegrationConfig().__dict__,
            
            # Analytics and Telemetry
            'analytics': {
                'enabled': True,
                'privacy_mode': True,
                'collect_usage_stats': True,
                'collect_performance_metrics': True,
                'anonymous_tracking': True,
                'telemetry_endpoint': 'https://analytics.pygenai-security.com'
            },
            
            # Logging Configuration
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'log_file': 'pygenai_security.log',
                'max_log_size_mb': 100,
                'log_rotation': True,
                'security_events_log': 'security_events.log',
                'audit_log': 'audit.log'
            },
            
            # Reporting Configuration
            'reporting': {
                'formats': ['json', 'html', 'csv'],
                'include_code_snippets': True,
                'include_remediation_examples': True,
                'generate_executive_summary': True,
                'include_compliance_mapping': True,
                'custom_templates': {}
            },
            
            # VS Code Integration
            'vscode': {
                'enabled': True,
                'real_time_scanning': True,
                'diagnostic_delay_ms': 1000,
                'max_diagnostics': 100,
                'show_inline_suggestions': True,
                'enable_code_actions': True
            },
            
            # TestSprite MCP Integration
            'testsprite': {
                'enabled': False,
                'mcp_server_url': 'localhost:3000',
                'api_key': '',
                'auto_generate_tests': True,
                'test_framework': 'pytest',
                'include_security_tests': True
            }
        }
    
    def load_from_file(self, file_path: Union[str, Path]):
        """Load configuration from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    self.config = yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    self.config = json.load(f)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {file_path.suffix}")
            
            self.config_file_path = file_path
            logger.info(f"Configuration loaded from {file_path}")
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Invalid configuration file format: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {e}")
    
    def save_to_file(self, file_path: Optional[Union[str, Path]] = None):
        """Save configuration to file"""
        if file_path is None:
            if self.config_file_path is None:
                raise ConfigurationError("No file path specified and no default file path available")
            file_path = self.config_file_path
        else:
            file_path = Path(file_path)
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                elif file_path.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {file_path.suffix}")
            
            self.config_file_path = file_path
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def has(self, key: str) -> bool:
        """Check if configuration key exists"""
        return self.get(key) is not None
    
    def get_scanner_config(self, scanner_name: str) -> Dict[str, Any]:
        """Get configuration for specific scanner"""
        scanner_config = self.get(f'scanners.{scanner_name}', {})
        
        # Merge with default scanner config if needed
        if not scanner_config:
            default_config = ScannerConfig().__dict__
            self.set(f'scanners.{scanner_name}', default_config)
            return default_config
        
        return scanner_config
    
    def get_enterprise_config(self) -> Dict[str, Any]:
        """Get enterprise configuration"""
        return self.get('enterprise', EnterpriseConfig().__dict__)
    
    def get_integration_config(self) -> Dict[str, Any]:
        """Get integration configuration"""
        return self.get('integrations', IntegrationConfig().__dict__)
    
    def is_enterprise_enabled(self) -> bool:
        """Check if enterprise features are enabled"""
        return self.get('enterprise.enabled', False)
    
    def is_scanner_enabled(self, scanner_name: str) -> bool:
        """Check if specific scanner is enabled"""
        enabled_scanners = self.get('scanners.enabled', [])
        scanner_config = self.get(f'scanners.{scanner_name}', {})
        
        return scanner_name in enabled_scanners and scanner_config.get('enabled', True)
    
    def get_enabled_scanners(self) -> List[str]:
        """Get list of enabled scanners"""
        enabled_scanners = self.get('scanners.enabled', [])
        
        # Filter by individual scanner enabled status
        return [
            scanner for scanner in enabled_scanners 
            if self.is_scanner_enabled(scanner)
        ]
    
    def enable_scanner(self, scanner_name: str):
        """Enable specific scanner"""
        enabled_scanners = self.get('scanners.enabled', [])
        if scanner_name not in enabled_scanners:
            enabled_scanners.append(scanner_name)
            self.set('scanners.enabled', enabled_scanners)
        
        self.set(f'scanners.{scanner_name}.enabled', True)
    
    def disable_scanner(self, scanner_name: str):
        """Disable specific scanner"""
        self.set(f'scanners.{scanner_name}.enabled', False)
    
    def get_compliance_frameworks(self) -> List[str]:
        """Get enabled compliance frameworks"""
        return self.get('enterprise.compliance_frameworks', [])
    
    def enable_compliance_framework(self, framework: str):
        """Enable compliance framework"""
        frameworks = self.get_compliance_frameworks()
        if framework not in frameworks:
            frameworks.append(framework)
            self.set('enterprise.compliance_frameworks', frameworks)
    
    def _validate_config(self):
        """Validate configuration for consistency and required values"""
        validation_errors = []
        
        # Validate scanner configuration
        enabled_scanners = self.get('scanners.enabled', [])
        for scanner in enabled_scanners:
            scanner_config = self.get(f'scanners.{scanner}', {})
            if not scanner_config:
                validation_errors.append(f"Missing configuration for enabled scanner: {scanner}")
        
        # Validate threat levels
        valid_threat_levels = ['info', 'low', 'medium', 'high', 'critical']
        min_threat_level = self.get('filtering.min_threat_level', 'medium')
        if min_threat_level not in valid_threat_levels:
            validation_errors.append(f"Invalid min_threat_level: {min_threat_level}")
        
        # Validate performance settings
        max_workers = self.get('performance.max_workers', 4)
        if not isinstance(max_workers, int) or max_workers < 1 or max_workers > 32:
            validation_errors.append("max_workers must be integer between 1 and 32")
        
        scan_timeout = self.get('performance.scan_timeout', 3600)
        if not isinstance(scan_timeout, int) or scan_timeout < 60:
            validation_errors.append("scan_timeout must be integer >= 60 seconds")
        
        # Validate confidence thresholds
        confidence_threshold = self.get('filtering.confidence_threshold', 0.7)
        if not isinstance(confidence_threshold, (int, float)) or not 0 <= confidence_threshold <= 1:
            validation_errors.append("confidence_threshold must be float between 0 and 1")
        
        # Validate enterprise settings
        if self.is_enterprise_enabled():
            license_key = self.get('enterprise.license_key', '')
            if not license_key:
                validation_errors.append("Enterprise mode enabled but no license_key provided")
        
        # Validate TestSprite integration
        if self.get('testsprite.enabled', False):
            api_key = self.get('testsprite.api_key', '')
            server_url = self.get('testsprite.mcp_server_url', '')
            if not api_key:
                validation_errors.append("TestSprite enabled but no api_key provided")
            if not server_url:
                validation_errors.append("TestSprite enabled but no mcp_server_url provided")
        
        # Log validation errors
        if validation_errors:
            logger.warning(f"Configuration validation issues: {validation_errors}")
            
        # In strict mode, raise exception for validation errors
        if self.get('strict_mode', False) and validation_errors:
            raise ConfigurationError(f"Configuration validation failed: {validation_errors}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for diagnostics"""
        return {
            'config_file': str(self.config_file_path) if self.config_file_path else None,
            'enabled_scanners': self.get_enabled_scanners(),
            'enterprise_enabled': self.is_enterprise_enabled(),
            'compliance_frameworks': self.get_compliance_frameworks(),
            'integrations': {
                'vscode': self.get('vscode.enabled', True),
                'testsprite': self.get('testsprite.enabled', False),
                'analytics': self.get('analytics.enabled', True)
            },
            'performance': {
                'max_workers': self.get('performance.max_workers', 4),
                'parallel_scanning': self.get('performance.enable_parallel_scanning', True),
                'file_size_limit_mb': self.get('performance.file_size_limit_mb', 50)
            },
            'filtering': {
                'min_threat_level': self.get('filtering.min_threat_level', 'medium'),
                'confidence_threshold': self.get('filtering.confidence_threshold', 0.7)
            }
        }
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._load_default_config()
        logger.info("Configuration reset to defaults")
    
    def merge_config(self, other_config: Dict[str, Any]):
        """Merge another configuration into current one"""
        def deep_merge(base_dict: dict, merge_dict: dict):
            for key, value in merge_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_merge(self.config, other_config)
        self._validate_config()
        
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration"""
        return self.config.copy()
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return f"ConfigManager(scanners={len(self.get_enabled_scanners())}, enterprise={self.is_enterprise_enabled()})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"ConfigManager(config_file='{self.config_file_path}', scanners={self.get_enabled_scanners()})"
