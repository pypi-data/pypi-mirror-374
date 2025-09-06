"""
Base transform class for data processing and extraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator

from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.exceptions import TransformError


class BaseTransform(ABC):
    """
    Abstract base class for data transforms.
    
    Transforms are responsible for processing resources and extracting
    structured information like entities and relationships.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    def transform(self, resource: Resource, **kwargs) -> Resource:
        """Transform a single resource."""
        pass
    
    def transform_batch(self, resources: List[Resource], **kwargs) -> List[Resource]:
        """Transform a batch of resources."""
        try:
            return [self.transform(resource, **kwargs) for resource in resources]
        except Exception as e:
            raise TransformError(f"Batch transform failed: {e}")
    
    def transform_dataset(self, dataset: Dataset, **kwargs) -> Dataset:
        """Transform all resources in a dataset."""
        try:
            transformed_resources = {}
            
            for resource_id, resource in dataset.resources.items():
                transformed_resource = self.transform(resource, **kwargs)
                transformed_resources[resource_id] = transformed_resource
            
            # Create new dataset with transformed resources
            new_dataset = Dataset(
                name=dataset.name,
                description=dataset.description,
                version=dataset.version,
                resources=transformed_resources,
                edges=dataset.edges.copy(),  # Keep existing edges
                metadata=dataset.metadata.copy()
            )
            
            return new_dataset
        except Exception as e:
            raise TransformError(f"Dataset transform failed: {e}")
    
    @abstractmethod
    def extract_entities(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract entities from text."""
        pass
    
    @abstractmethod
    def extract_relations(self, text: str, entities: Optional[List[Dict[str, Any]]] = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract relations from text."""
        pass
