"""
Core Exceptions for the kgforge framework
[
KGForgeError,
ValidationError,
StorageError,
ConnectorError,
TransformError,
ConfigurationError,
ResourceError,
DatasetError,
QueryError,
ExportError
]
"""

from typing import Any, Dict, Optional

class KGForgeError(Exception):
    """
    Base class for all exceptions raised by the kgforge framework.
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

class ValidationError(KGForgeError):
    """
    Exception raised for validation fails in the kgforge framework.
    """
    pass

class StorageError(KGForgeError):
    """
    Exception raised for storage-related errors or when storage operations fail in the kgforge framework.
    """
    pass

class ConnectorError(KGForgeError):
    """Raised when connector operations fail."""
    pass

class TransformError(KGForgeError):
    """Raised when transformation operations fail."""
    pass

class ConfigurationError(KGForgeError):
    """Raised when configuration is invalid."""
    pass

class ResourceError(KGForgeError):
    """Raised when resource operations fail."""
    pass

class DatasetError(KGForgeError):
    """Raised when dataset operations fail."""
    pass

class QueryError(KGForgeError):
    """Raised when query operations fail."""
    pass

class ExportError(KGForgeError):
    """Raised when export operations fail."""
    pass
