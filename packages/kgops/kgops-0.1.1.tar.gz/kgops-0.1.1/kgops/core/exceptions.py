"""
Core Exceptions for the kgops framework
[
KGOpsError,
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

class KGOpsError(Exception):
    """
    Base class for all exceptions raised by the kgops framework.
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

class ValidationError(KGOpsError):
    """
    Exception raised for validation fails in the kgops framework.
    """
    pass

class StorageError(KGOpsError):
    """
    Exception raised for storage-related errors or when storage operations fail in the kgops framework.
    """
    pass

class ConnectorError(KGOpsError):
    """Raised when connector operations fail."""
    pass

class TransformError(KGOpsError):
    """Raised when transformation operations fail."""
    pass

class ConfigurationError(KGOpsError):
    """Raised when configuration is invalid."""
    pass

class ResourceError(KGOpsError):
    """Raised when resource operations fail."""
    pass

class DatasetError(KGOpsError):
    """Raised when dataset operations fail."""
    pass

class QueryError(KGOpsError):
    """Raised when query operations fail."""
    pass

class ExportError(KGOpsError):
    """Raised when export operations fail."""
    pass
