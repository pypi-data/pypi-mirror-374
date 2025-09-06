"""
Main KGOps class - the primary interface for knowledge graph operations.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Iterator
from pathlib import Path
import logging
from datetime import datetime

from kgops.core.context import Context, GraphConfig, TenantConfig
from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.exceptions import KGOpsError, ValidationError, StorageError
from kgops.storage.base import BaseStorage
from kgops.storage.memory import MemoryStorage
from kgops.connectors.base import BaseConnector
from kgops.transforms.base import BaseTransform
from kgops.utils.logging import get_logger


class KGOps:
    """
    Main interface for knowledge graph operations in kgops.
    
    Provides unified access to graph building, querying, and export functionality
    with support for multiple backends and multi-tenancy.
    """
    
    def __init__(self, 
                 backend: str = "networkx",
                 tenant: Optional[str] = None,
                 graph: Optional[str] = None,
                 config: Optional[Union[str, Path, Dict[str, Any], Context]] = None,
                 **kwargs):
        """
        Initialize KGOps instance.
        
        Args:
            backend: Storage backend type (default: "networkx")
            tenant: Tenant identifier for multi-tenancy
            graph: Graph name/identifier
            config: Configuration file path, dict, or Context instance
            **kwargs: Additional configuration options
        """
        self.logger = get_logger(__name__)
        
        # Initialize context
        if isinstance(config, Context):
            self.context = config
        elif isinstance(config, (str, Path)):
            self.context = Context.from_file(config)
        elif isinstance(config, dict):
            self.context = Context(**config)
        else:
            self.context = Context()
        
        # Override context with parameters
        if backend:
            self.context.graph.backend = backend
        
        if tenant and graph:
            self.context.set_tenant(tenant, graph)
        
        # Apply additional kwargs to context
        for key, value in kwargs.items():
            self.context.update_graph_config(**{key: value})
        
        # Initialize storage
        self._storage: Optional[BaseStorage] = None
        self._current_dataset: Optional[Dataset] = None
        
        # Initialize components
        self._connectors: Dict[str, BaseConnector] = {}
        self._transforms: Dict[str, BaseTransform] = {}
        
        self.logger.info(f"KGOps initialized with backend: {self.context.graph.backend}")
    
    @property
    def storage(self) -> BaseStorage:
        """Get or initialize storage backend."""
        if self._storage is None:
            self._storage = self._create_storage()
        return self._storage
    
    def _create_storage(self) -> BaseStorage:
        """Create storage backend based on configuration."""
        backend_type = self.context.graph.backend.lower()
        
        if backend_type == "networkx":
            return MemoryStorage(self.context)
        else:
            raise ValidationError(f"Unsupported backend type: {backend_type}")
    
    def create_graph(self, name: str, description: Optional[str] = None, 
                     version: str = "1.0.0", **metadata) -> Dataset:
        """Create a new knowledge graph dataset."""
        try:
            dataset = Dataset(
                name=name,
                description=description,
                version=version,
                metadata=metadata
            )
            
            self._current_dataset = dataset
            self.logger.info(f"Created new graph: {name}")
            
            return dataset
        except Exception as e:
            raise KGOpsError(f"Failed to create graph: {e}")
    
    def load_graph(self, source: Union[str, Path, Dict[str, Any]], 
                   format: str = "auto") -> Dataset:
        """Load a knowledge graph from various sources."""
        try:
            if isinstance(source, (str, Path)):
                path = Path(source)
                
                if format == "auto":
                    format = path.suffix.lower().lstrip('.')
                
                if format == "json":
                    dataset = Dataset.from_json(path)
                else:
                    raise ValidationError(f"Unsupported format: {format}")
            
            elif isinstance(source, dict):
                dataset = Dataset.from_dict(source)
            else:
                raise ValidationError("Source must be file path or dictionary")
            
            self._current_dataset = dataset
            self.logger.info(f"Loaded graph: {dataset.name}")
            
            return dataset
        except Exception as e:
            raise KGOpsError(f"Failed to load graph: {e}")
    
    def save_graph(self, path: Union[str, Path], format: str = "auto") -> None:
        """Save current graph to file."""
        if self._current_dataset is None:
            raise ValidationError("No active graph to save")
        
        try:
            path = Path(path)
            
            if format == "auto":
                format = path.suffix.lower().lstrip('.')
            
            if format == "json":
                self._current_dataset.to_json(path)
            else:
                raise ValidationError(f"Unsupported format: {format}")
            
            self.logger.info(f"Saved graph to: {path}")
        except Exception as e:
            raise KGOpsError(f"Failed to save graph: {e}")
    
    def add_resource(self, resource: Union[Resource, Dict[str, Any]], 
                     **properties) -> Resource:
        """Add a resource to the current graph."""
        if self._current_dataset is None:
            raise ValidationError("No active graph. Create or load a graph first.")
        
        try:
            if isinstance(resource, dict):
                # Create resource from dictionary
                labels = resource.pop("labels", [])
                resource_id = resource.pop("id", None)
                resource_props = {**resource, **properties}
                
                new_resource = Resource(
                    id=resource_id if resource_id else None,
                    labels=set(labels) if labels else set(),
                    properties=resource_props
                )
            elif isinstance(resource, Resource):
                new_resource = resource
                # Apply additional properties
                for key, value in properties.items():
                    new_resource.set_property(key, value)
            else:
                raise ValidationError("Resource must be Resource instance or dictionary")
            
            self._current_dataset.add_resource(new_resource)
            self.logger.debug(f"Added resource: {new_resource.id}")
            
            return new_resource
        except Exception as e:
            raise KGOpsError(f"Failed to add resource: {e}")
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        if self._current_dataset is None:
            return None
        
        return self._current_dataset.get_resource(resource_id)
    
    def add_edge(self, source: Union[str, Resource], target: Union[str, Resource],
                 edge_type: str, **properties) -> Edge:
        """Add an edge between two resources."""
        if self._current_dataset is None:
            raise ValidationError("No active graph. Create or load a graph first.")
        
        try:
            source_id = source.id if isinstance(source, Resource) else source
            target_id = target.id if isinstance(target, Resource) else target
            
            edge = self._current_dataset.add_edge(
                source_id=source_id,
                target_id=target_id,
                edge_type=edge_type,
                properties=properties
            )
            
            self.logger.debug(f"Added edge: {source_id} -[{edge_type}]-> {target_id}")
            
            return edge
        except Exception as e:
            raise KGOpsError(f"Failed to add edge: {e}")
    
    def query(self, query_type: str = "neighbors", **params) -> Any:
        """Execute various types of queries on the graph."""
        if self._current_dataset is None:
            raise ValidationError("No active graph to query")
        
        try:
            if query_type == "neighbors":
                resource_id = params.get("resource_id")
                direction = params.get("direction", "both")
                depth = params.get("depth", 1)
                
                if not resource_id:
                    raise ValidationError("resource_id required for neighbors query")
                
                return self._get_neighbors_recursive(resource_id, direction, depth)
            
            elif query_type == "label":
                label = params.get("label")
                if not label:
                    raise ValidationError("label required for label query")
                
                return self._current_dataset.get_resources_by_label(label)
            
            elif query_type == "property":
                key = params.get("key")
                value = params.get("value")
                
                if not key:
                    raise ValidationError("key required for property query")
                
                return self._current_dataset.get_resources_by_property(key, value)
            
            else:
                raise ValidationError(f"Unsupported query type: {query_type}")
        
        except Exception as e:
            raise KGOpsError(f"Query failed: {e}")
    
    def _get_neighbors_recursive(self, resource_id: str, direction: str, depth: int) -> List[Resource]:
        """Get neighbors recursively up to specified depth."""
        visited = set()
        result = []
        
        def _traverse(current_id: str, current_depth: int):
            if current_depth <= 0 or current_id in visited:
                return
            
            visited.add(current_id)
            neighbors = self._current_dataset.get_neighbors(current_id, direction)
            
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    neighbor_resource = self._current_dataset.get_resource(neighbor_id)
                    if neighbor_resource:
                        result.append(neighbor_resource)
                    _traverse(neighbor_id, current_depth - 1)
        
        _traverse(resource_id, depth)
        return result
    
    def filter_resources(self, filter_func: Callable[[Resource], bool]) -> List[Resource]:
        """Filter resources using a custom function."""
        if self._current_dataset is None:
            return []
        
        return self._current_dataset.filter_resources(filter_func)
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the current graph."""
        if self._current_dataset is None:
            return {"error": "No active graph"}
        
        return self._current_dataset.stats()
    
    def export(self, format: str = "networkx", **kwargs) -> Any:
        """Export graph to various formats."""
        if self._current_dataset is None:
            raise ValidationError("No active graph to export")
        
        try:
            if format.lower() == "networkx":
                return self._export_networkx(**kwargs)
            elif format.lower() == "json":
                return self._current_dataset.to_dict()
            elif format.lower() == "edges":
                return self._export_edge_list(**kwargs)
            else:
                raise ValidationError(f"Unsupported export format: {format}")
        except Exception as e:
            raise KGOpsError(f"Export failed: {e}")
    
    def _export_networkx(self, **kwargs) -> Any:
        """Export to NetworkX graph."""
        try:
            import networkx as nx
            
            # Create directed or undirected graph
            directed = kwargs.get("directed", True)
            G = nx.DiGraph() if directed else nx.Graph()
            
            # Add nodes
            for resource in self._current_dataset.resources.values():
                node_attrs = {
                    "labels": list(resource.labels),
                    **resource.properties
                }
                G.add_node(resource.id, **node_attrs)
            
            # Add edges
            for edge in self._current_dataset.edges:
                edge_attrs = {
                    "type": edge.type,
                    **edge.properties
                }
                G.add_edge(edge.source, edge.target, **edge_attrs)
            
            return G
        except ImportError:
            raise KGOpsError("NetworkX not available for export")
    
    def _export_edge_list(self, **kwargs) -> List[Dict[str, Any]]:
        """Export as edge list."""
        edges = []
        
        for edge in self._current_dataset.edges:
            edges.append({
                "source": edge.source,
                "target": edge.target,
                "type": edge.type,
                "properties": edge.properties
            })
        
        return edges
    
    def clear(self) -> None:
        """Clear current graph."""
        self._current_dataset = None
        self.logger.info("Cleared current graph")
    
    @property
    def current_graph(self) -> Optional[Dataset]:
        """Get current active graph dataset."""
        return self._current_dataset
    
    def __str__(self) -> str:
        graph_info = f"graph={self._current_dataset.name}" if self._current_dataset else "no graph"
        return f"KGOps(backend={self.context.graph.backend}, {graph_info})"
    
    def __repr__(self) -> str:
        return self.__str__()
