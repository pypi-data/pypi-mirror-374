"""
Base class for storage backends.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator
from kgops.core.context import Context
from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge


class BaseStorage(ABC):
    """
    Abstract base class for all storage backends.
    """
    
    def __init__(self, context: Context):
        self.context = context
    
    @abstractmethod
    def create_graph(self, name: str, **metadata) -> Dataset:
        """Create a new graph."""
        pass
    
    @abstractmethod
    def load_graph(self, name: str) -> Optional[Dataset]:
        """Load an existing graph."""
        pass
    
    @abstractmethod
    def save_graph(self, dataset: Dataset) -> None:
        """Save a graph dataset."""
        pass
    
    @abstractmethod
    def delete_graph(self, name: str) -> None:
        """Delete a graph."""
        pass
    
    @abstractmethod
    def list_graphs(self) -> List[str]:
        """List available graphs."""
        pass
    
    @abstractmethod
    def add_resource(self, graph_name: str, resource: Resource) -> None:
        """Add a resource to a graph."""
        pass
    
    @abstractmethod
    def get_resource(self, graph_name: str, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        pass
    
    @abstractmethod
    def update_resource(self, graph_name: str, resource: Resource) -> None:
        """Update an existing resource."""
        pass
    
    @abstractmethod
    def delete_resource(self, graph_name: str, resource_id: str) -> None:
        """Delete a resource."""
        pass
    
    @abstractmethod
    def add_edge(self, graph_name: str, edge: Edge) -> None:
        """Add an edge to a graph."""
        pass
    
    @abstractmethod
    def get_edges(self, graph_name: str, source: Optional[str] = None,
                  target: Optional[str] = None, edge_type: Optional[str] = None) -> List[Edge]:
        """Get edges matching criteria."""
        pass
    
    @abstractmethod
    def delete_edge(self, graph_name: str, source: str, target: str, edge_type: str) -> None:
        """Delete an edge."""
        pass
    
    @abstractmethod
    def query(self, graph_name: str, query: str, **params) -> Any:
        """Execute a query against the graph."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close storage connection."""
        pass
