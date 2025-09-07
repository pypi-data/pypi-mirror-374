"""
Custom exceptions for PyGenAI Security Framework
"""


class PyGenAISecurityError(Exception):
    """Base exception for PyGenAI Security Framework"""
    pass


class ScanError(PyGenAISecurityError):
    """Exception raised during scanning operations"""
    pass


class ConfigurationError(PyGenAISecurityError):
    """Exception raised for configuration-related errors"""
    pass


class LicenseError(PyGenAISecurityError):
    """Exception raised for licensing issues"""
    pass


class IntegrationError(PyGenAISecurityError):
    """Exception raised for integration failures"""
    pass


class ValidationError(PyGenAISecurityError):
    """Exception raised for validation failures"""
    pass
