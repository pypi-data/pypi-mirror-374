"""
Base connector class for data ingestion.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Iterator, Union
from pathlib import Path

from kgops.core.resource import Resource
from kgops.core.dataset import Dataset
from kgops.core.exceptions import ConnectorError


class BaseConnector(ABC):
    """
    Abstract base class for data connectors.
    
    Connectors are responsible for ingesting data from various sources
    and converting them into Resource objects.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    def connect(self, source: Union[str, Path, Dict[str, Any]], **kwargs) -> None:
        """Connect to data source."""
        pass
    
    @abstractmethod
    def read(self, **kwargs) -> Iterator[Dict[str, Any]]:
        """Read data from source and yield records."""
        pass
    
    @abstractmethod
    def to_resources(self, records: Iterator[Dict[str, Any]], **kwargs) -> Iterator[Resource]:
        """Convert records to Resource objects."""
        pass
    
    def ingest(self, source: Union[str, Path, Dict[str, Any]], **kwargs) -> Iterator[Resource]:
        """
        Full ingestion pipeline: connect, read, and convert to resources.
        """
        try:
            self.connect(source, **kwargs)
            records = self.read(**kwargs)
            return self.to_resources(records, **kwargs)
        except Exception as e:
            raise ConnectorError(f"Ingestion failed: {e}")
    
    @abstractmethod
    def close(self) -> None:
        """Close connection and cleanup resources."""
        pass
