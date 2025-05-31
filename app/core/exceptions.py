"""
Custom exceptions for the application.
"""

class ConfigurationError(Exception):
    """Raised when there is an error in the application configuration."""
    pass

class DataProcessingError(Exception):
    """Raised when there is an error processing data."""
    pass

class ExportError(Exception):
    """Raised when there is an error exporting data."""
    pass

class AuthenticationError(Exception):
    """Raised when there is an authentication error."""
    pass

class ValidationError(Exception):
    """Raised when there is a validation error."""
    pass

class AnalyticsError(Exception):
    """
    Exception raised for errors in the analytics service.
    """
    pass 