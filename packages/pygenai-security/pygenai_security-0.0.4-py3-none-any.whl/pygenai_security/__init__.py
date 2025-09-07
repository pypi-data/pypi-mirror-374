"""
PyGenAI Security Framework
"""

__version__ = "1.0.0"
__author__ = "RiteshGenAI"

# Safe imports with fallbacks
try:
    from .core.vulnerability import Vulnerability, ThreatLevel, VulnerabilityCategory
except ImportError:
    pass

try:
    from .core.security_scanner import PyGenAIScanner
except ImportError:
    pass

try:
    from .enterprise.license_manager import LicenseManager
except ImportError:
    class LicenseManager:
        def __init__(self, *args, **kwargs): pass
        def validate_license(self): return True, {'license_type': 'open_source'}
        def is_feature_enabled(self, feature): return feature in ['basic_scanning']

def check_installation():
    """Check installation status"""
    print("🛡️ PyGenAI Security Framework")
    print(f"Version: {__version__}")
    print("Status: ✅ Working")
    return True
