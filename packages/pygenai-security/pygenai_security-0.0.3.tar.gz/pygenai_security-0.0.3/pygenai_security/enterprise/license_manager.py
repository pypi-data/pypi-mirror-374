"""
Minimal License Manager for PyGenAI Security Framework
"""

class LicenseType:
    OPEN_SOURCE = "open_source"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class LicenseManager:
    def __init__(self, config=None):
        self.config = config or {}
    
    def validate_license(self):
        return True, {
            'license_type': LicenseType.OPEN_SOURCE,
            'valid': True,
            'message': 'Open source license'
        }
    
    def is_feature_enabled(self, feature):
        open_source_features = [
            'basic_scanning',
            'vs_code_integration',
            'cli_access'
        ]
        return feature in open_source_features
    
    def get_license_info(self):
        return {
            'valid': True,
            'type': LicenseType.OPEN_SOURCE,
            'features': {
                'basic_scanning': True,
                'vs_code_integration': True,
                'cli_access': True,
                'enterprise_features': False
            }
        }
