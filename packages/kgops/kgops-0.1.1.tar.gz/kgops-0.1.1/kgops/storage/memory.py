"""
In-memory storage backend using NetworkX.
"""

from typing import Any, Dict, List, Optional, Union, Iterator
import networkx as nx
from datetime import datetime, timezone

from kgops.storage.base import BaseStorage
from kgops.core.context import Context
from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.exceptions import StorageError, ValidationError
from kgops.utils.logging import get_logger


class MemoryStorage(BaseStorage):
    """
    In-memory storage backend using NetworkX graphs.
    
    Suitable for development, testing, and small to medium datasets
    that fit in memory.
    """
    
    def __init__(self, context: Context):
        super().__init__(context)
        self.logger = get_logger(__name__)
        self._graphs: Dict[str, Dataset] = {}
        
        # NetworkX graph cache for efficient querying
        self._nx_cache: Dict[str, nx.DiGraph] = {}
        
        self.logger.info("MemoryStorage initialized")
    
    def create_graph(self, name: str, **metadata) -> Dataset:
        """Create a new graph dataset."""
        if name in self._graphs:
            raise ValidationError(f"Graph '{name}' already exists")
        
        dataset = Dataset(
            name=name,
            metadata=metadata
        )
        
        self._graphs[name] = dataset
        self.logger.info(f"Created graph: {name}")
        
        return dataset
    
    def load_graph(self, name: str) -> Optional[Dataset]:
        """Load an existing graph."""
        return self._graphs.get(name)
    
    def save_graph(self, dataset: Dataset) -> None:
        """Save a graph dataset (in-memory, so just update reference)."""
        self._graphs[dataset.name] = dataset
        # Invalidate NetworkX cache
        if dataset.name in self._nx_cache:
            del self._nx_cache[dataset.name]
        
        self.logger.debug(f"Saved graph: {dataset.name}")
    
    def delete_graph(self, name: str) -> None:
        """Delete a graph."""
        if name in self._graphs:
            del self._graphs[name]
        
        if name in self._nx_cache:
            del self._nx_cache[name]
        
        self.logger.info(f"Deleted graph: {name}")
    
    def list_graphs(self) -> List[str]:
        """List available graphs."""
        return list(self._graphs.keys())
    
    def add_resource(self, graph_name: str, resource: Resource) -> None:
        """Add a resource to a graph."""
        graph = self._get_graph(graph_name)
        graph.add_resource(resource)
        
        # Invalidate cache
        self._invalidate_cache(graph_name)
    
    def get_resource(self, graph_name: str, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        graph = self._get_graph(graph_name)
        return graph.get_resource(resource_id)
    
    def update_resource(self, graph_name: str, resource: Resource) -> None:
        """Update an existing resource."""
        graph = self._get_graph(graph_name)
        
        if resource.id not in graph.resources:
            raise ValidationError(f"Resource {resource.id} not found in graph {graph_name}")
        
        graph.resources[resource.id] = resource
        resource.updated_at = datetime.now(timezone.utc)
        
        # Invalidate cache
        self._invalidate_cache(graph_name)
    
    def delete_resource(self, graph_name: str, resource_id: str) -> None:
        """Delete a resource."""
        graph = self._get_graph(graph_name)
        graph.remove_resource(resource_id)
        
        # Invalidate cache
        self._invalidate_cache(graph_name)
    
    def add_edge(self, graph_name: str, edge: Edge) -> None:
        """Add an edge to a graph."""
        graph = self._get_graph(graph_name)
        
        # Validate that source and target resources exist
        if edge.source not in graph.resources:
            raise ValidationError(f"Source resource {edge.source} not found")
        if edge.target not in graph.resources:
            raise ValidationError(f"Target resource {edge.target} not found")
        
        graph.edges.append(edge)
        
        # Invalidate cache
        self._invalidate_cache(graph_name)
    
    def get_edges(self, graph_name: str, source: Optional[str] = None,
                  target: Optional[str] = None, edge_type: Optional[str] = None) -> List[Edge]:
        """Get edges matching criteria."""
        graph = self._get_graph(graph_name)
        return graph.get_edges(source, target, edge_type)
    
    def delete_edge(self, graph_name: str, source: str, target: str, edge_type: str) -> None:
        """Delete an edge."""
        graph = self._get_graph(graph_name)
        
        # Find and remove matching edges
        original_count = len(graph.edges)
        graph.edges = [
            edge for edge in graph.edges
            if not (edge.source == source and edge.target == target and edge.type == edge_type)
        ]
        
        removed_count = original_count - len(graph.edges)
        if removed_count == 0:
            raise ValidationError(f"Edge not found: {source} -[{edge_type}]-> {target}")
        
        # Invalidate cache
        self._invalidate_cache(graph_name)
        
        self.logger.debug(f"Deleted {removed_count} edge(s)")
    
    def query(self, graph_name: str, query: str, **params) -> Any:
        """Execute a query against the graph."""
        graph = self._get_graph(graph_name)
        nx_graph = self._get_networkx_graph(graph_name)
        
        try:
            if query == "neighbors":
                node_id = params.get("node_id")
                direction = params.get("direction", "both")
                
                if not node_id:
                    raise ValidationError("node_id required for neighbors query")
                
                if direction == "out":
                    return list(nx_graph.successors(node_id))
                elif direction == "in":
                    return list(nx_graph.predecessors(node_id))
                else:  # both
                    return list(nx_graph.neighbors(node_id))
            
            elif query == "shortest_path":
                source = params.get("source")
                target = params.get("target")
                
                if not source or not target:
                    raise ValidationError("source and target required for shortest_path query")
                
                try:
                    return nx.shortest_path(nx_graph, source, target)
                except nx.NetworkXNoPath:
                    return []
            
            elif query == "connected_components":
                # For directed graphs, use weakly connected components
                if nx_graph.is_directed():
                    return list(nx.weakly_connected_components(nx_graph))
                else:
                    return list(nx.connected_components(nx_graph))
            
            elif query == "degree":
                node_id = params.get("node_id")
                if node_id:
                    return nx_graph.degree(node_id)
                else:
                    return dict(nx_graph.degree())
            
            else:
                raise ValidationError(f"Unsupported query type: {query}")
        
        except Exception as e:
            raise StorageError(f"Query execution failed: {e}")
    
    def _get_graph(self, graph_name: str) -> Dataset:
        """Get graph dataset or raise error."""
        if graph_name not in self._graphs:
            raise ValidationError(f"Graph '{graph_name}' not found")
        return self._graphs[graph_name]
    
    def _get_networkx_graph(self, graph_name: str) -> nx.DiGraph:
        """Get or create cached NetworkX graph."""
        if graph_name not in self._nx_cache:
            self._build_networkx_cache(graph_name)
        
        return self._nx_cache[graph_name]
    
    def _build_networkx_cache(self, graph_name: str) -> None:
        """Build NetworkX representation for efficient querying."""
        graph = self._get_graph(graph_name)
        nx_graph = nx.DiGraph()
        
        # Add nodes with attributes
        for resource in graph.resources.values():
            node_attrs = {
                "labels": list(resource.labels),
                "created_at": resource.created_at,
                "updated_at": resource.updated_at,
                **resource.properties
            }
            nx_graph.add_node(resource.id, **node_attrs)
        
        # Add edges with attributes
        for edge in graph.edges:
            edge_attrs = {
                "type": edge.type,
                "created_at": edge.created_at,
                **edge.properties
            }
            nx_graph.add_edge(edge.source, edge.target, **edge_attrs)
        
        self._nx_cache[graph_name] = nx_graph
        self.logger.debug(f"Built NetworkX cache for graph: {graph_name}")
    
    def _invalidate_cache(self, graph_name: str) -> None:
        """Invalidate NetworkX cache for a graph."""
        if graph_name in self._nx_cache:
            del self._nx_cache[graph_name]
    
    def get_networkx_graph(self, graph_name: str) -> nx.DiGraph:
        """Public method to get NetworkX representation."""
        return self._get_networkx_graph(graph_name)
    
    def close(self) -> None:
        """Close storage (cleanup in-memory data)."""
        self._graphs.clear()
        self._nx_cache.clear()
        self.logger.info("MemoryStorage closed")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass  # Ignore errors during cleanup
