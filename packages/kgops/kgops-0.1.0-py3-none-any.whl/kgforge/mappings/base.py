"""
Base class for schema mappings.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseMapping(ABC):
    """
    Abstract base class for schema mappings and ontologies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    def map_properties(self, source_props: Dict[str, Any]) -> Dict[str, Any]:
        """Map source properties to target schema."""
        pass
    
    @abstractmethod
    def map_labels(self, source_labels: List[str]) -> List[str]:
        """Map source labels to target ontology."""
        pass
    
    @abstractmethod
    def validate_mapping(self, mapped_data: Dict[str, Any]) -> bool:
        """Validate mapped data against target schema."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the target schema definition."""
        pass
