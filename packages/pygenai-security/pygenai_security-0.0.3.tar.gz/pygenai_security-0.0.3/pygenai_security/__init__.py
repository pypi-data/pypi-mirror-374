"""
Fixed __init__.py for PyGenAI Security Framework
Handles missing modules gracefully and provides proper imports
"""

# PyGenAI Security Framework
# Version: 0.0.2
# Author: RiteshGenAI

__version__ = "0.0.2"
__author__ = "RiteshGenAI"
__license__ = "MIT"

# Core imports that should always be available
try:
    from .core.vulnerability import (
        Vulnerability, 
        ThreatLevel, 
        VulnerabilityCategory,
        VulnerabilityCollection
    )
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False

try:
    from .core.config_manager import ConfigManager
    _CONFIG_AVAILABLE = True
except ImportError:
    _CONFIG_AVAILABLE = False

try:
    from .core.security_scanner import PyGenAIScanner, ScanMode
    _SCANNER_AVAILABLE = True
except ImportError:
    _SCANNER_AVAILABLE = False

# Optional imports - don't fail if missing
try:
    from .scanners.traditional_scanner import TraditionalPythonScanner
    _TRADITIONAL_SCANNER_AVAILABLE = True
except ImportError:
    _TRADITIONAL_SCANNER_AVAILABLE = False

try:
    from .scanners.genai_scanner import GenAISecurityScanner
    _GENAI_SCANNER_AVAILABLE = True
except ImportError:
    _GENAI_SCANNER_AVAILABLE = False

try:
    from .scanners.dependency_scanner import DependencyScanner
    _DEPENDENCY_SCANNER_AVAILABLE = True
except ImportError:
    _DEPENDENCY_SCANNER_AVAILABLE = False

try:
    from .scanners.configuration_scanner import ConfigurationScanner
    _CONFIGURATION_SCANNER_AVAILABLE = True
except ImportError:
    _CONFIGURATION_SCANNER_AVAILABLE = False

# Enterprise features (optional)
try:
    from .enterprise.license_manager import LicenseManager
    _ENTERPRISE_AVAILABLE = True
except ImportError:
    _ENTERPRISE_AVAILABLE = False
    # Provide minimal LicenseManager fallback
    class LicenseManager:
        def __init__(self, *args, **kwargs):
            pass
        
        def validate_license(self):
            return True, {'license_type': 'open_source'}
        
        def is_feature_enabled(self, feature):
            # Open source features
            open_source_features = {
                'vs_code_integration': True,
                'basic_scanning': True
            }
            return open_source_features.get(feature, False)

# Utils (optional)
try:
    from .utils.logger import get_logger, setup_logging
    _LOGGING_AVAILABLE = True
except ImportError:
    _LOGGING_AVAILABLE = False
    # Provide basic logging fallback
    import logging
    def get_logger(name):
        return logging.getLogger(name)
    
    def setup_logging(level='INFO'):
        logging.basicConfig(level=getattr(logging, level.upper()))

try:
    from .utils.report_generator import ReportGenerator
    _REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    _REPORT_GENERATOR_AVAILABLE = False

# Public API
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',
    
    # Core classes (if available)
    'PyGenAIScanner',
    'Vulnerability',
    'ThreatLevel', 
    'VulnerabilityCategory',
    'VulnerabilityCollection',
    'ConfigManager',
    'ScanMode',
    
    # Scanners (if available)
    'TraditionalPythonScanner',
    'GenAISecurityScanner', 
    'DependencyScanner',
    'ConfigurationScanner',
    
    # Enterprise (with fallback)
    'LicenseManager',
    
    # Utils (with fallback)
    'get_logger',
    'setup_logging',
    'ReportGenerator',
]

# Only add to __all__ if actually available
if not _SCANNER_AVAILABLE:
    __all__.remove('PyGenAIScanner')
    __all__.remove('ScanMode')

if not _CORE_AVAILABLE:
    for item in ['Vulnerability', 'ThreatLevel', 'VulnerabilityCategory', 'VulnerabilityCollection']:
        if item in __all__:
            __all__.remove(item)

if not _CONFIG_AVAILABLE:
    __all__.remove('ConfigManager')

# Scanner availability flags
SCANNER_AVAILABILITY = {
    'traditional_python': _TRADITIONAL_SCANNER_AVAILABLE,
    'genai_security': _GENAI_SCANNER_AVAILABLE,  
    'dependency_check': _DEPENDENCY_SCANNER_AVAILABLE,
    'configuration_audit': _CONFIGURATION_SCANNER_AVAILABLE,
}

FEATURE_AVAILABILITY = {
    'core': _CORE_AVAILABLE,
    'config_manager': _CONFIG_AVAILABLE,
    'security_scanner': _SCANNER_AVAILABLE,
    'enterprise': _ENTERPRISE_AVAILABLE,
    'logging': _LOGGING_AVAILABLE,
    'report_generator': _REPORT_GENERATOR_AVAILABLE,
}

def get_version():
    """Get PyGenAI Security Framework version"""
    return __version__

def get_available_scanners():
    """Get list of available scanners"""
    return [scanner for scanner, available in SCANNER_AVAILABILITY.items() if available]

def get_feature_status():
    """Get status of all features"""
    return FEATURE_AVAILABILITY.copy()

def check_installation():
    """Check PyGenAI installation status and provide diagnostics"""
    print("🛡️ PyGenAI Security Framework Installation Status")
    print("=" * 50)
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print()
    
    print("📦 Core Components:")
    for feature, available in FEATURE_AVAILABILITY.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {feature}: {status}")
    
    print()
    print("🔍 Available Scanners:")
    available_scanners = get_available_scanners()
    if available_scanners:
        for scanner in available_scanners:
            print(f"  ✅ {scanner}")
    else:
        print("  ❌ No scanners available")
    
    print()
    if not _SCANNER_AVAILABLE:
        print("⚠️  WARNING: Core scanner not available. Please reinstall:")
        print("   pip uninstall pygenai-security")
        print("   pip install pygenai-security")
    elif not available_scanners:
        print("⚠️  WARNING: No scanners available. Limited functionality.")
    else:
        print("✅ Installation appears to be working correctly!")
    
    return _SCANNER_AVAILABLE and len(available_scanners) > 0

# Initialize logging if available
if _LOGGING_AVAILABLE:
    try:
        setup_logging('INFO')
    except Exception:
        pass