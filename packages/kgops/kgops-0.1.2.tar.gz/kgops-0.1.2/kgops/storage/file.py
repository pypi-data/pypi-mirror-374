"""
File-based storage backend for kgops.
"""

from typing import Any, Dict, List, Optional, Union, Iterator
from pathlib import Path
import json
import pickle
from datetime import datetime, timezone

from kgops.storage.base import BaseStorage
from kgops.core.context import Context
from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.exceptions import StorageError, ValidationError
from kgops.utils.logging import get_logger
from kgops.utils.serialization import serialize_dataset, deserialize_dataset


class FileStorage(BaseStorage):
    """
    File-based storage backend that persists graphs to local files.
    
    Suitable for small to medium datasets and development use.
    """
    
    def __init__(self, context: Context, storage_path: Optional[Union[str, Path]] = None):
        super().__init__(context)
        self.logger = get_logger(__name__)
        
        # Set storage directory
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.cwd() / "kgops_data"
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Index file for graph metadata
        self.index_path = self.storage_path / "_index.json"
        self._index = self._load_index()
        
        self.logger.info(f"FileStorage initialized at: {self.storage_path}")
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the graph index."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load index, creating new one: {e}")

        return {"graphs": {}, "created": datetime.now(timezone.utc).isoformat()}

    def _save_index(self) -> None:
        """Save the graph index."""
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self._index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise StorageError(f"Failed to save index: {e}")
    
    def _get_graph_path(self, name: str) -> Path:
        """Get file path for a graph."""
        safe_name = "".join(c for c in name if c.isalnum() or c in "._-")
        return self.storage_path / f"{safe_name}.json"
    
    def create_graph(self, name: str, **metadata) -> Dataset:
        """Create a new graph."""
        if name in self._index["graphs"]:
            raise ValidationError(f"Graph '{name}' already exists")
        
        try:
            dataset = Dataset(name=name, metadata=metadata)
            
            # Save to file
            graph_path = self._get_graph_path(name)
            dataset.to_json(graph_path)
            
            # Update index
            self._index["graphs"][name] = {
                "path": str(graph_path),
                "created": dataset.created_at.isoformat(),
                "updated": dataset.updated_at.isoformat(),
                "metadata": metadata
            }
            self._save_index()
            
            self.logger.info(f"Created graph: {name}")
            return dataset
        
        except Exception as e:
            raise StorageError(f"Failed to create graph: {e}")
    
    def load_graph(self, name: str) -> Optional[Dataset]:
        """Load an existing graph."""
        if name not in self._index["graphs"]:
            return None
        
        try:
            graph_info = self._index["graphs"][name]
            graph_path = Path(graph_info["path"])
            
            if not graph_path.exists():
                self.logger.warning(f"Graph file missing for {name}, removing from index")
                del self._index["graphs"][name]
                self._save_index()
                return None
            
            dataset = Dataset.from_json(graph_path)
            self.logger.debug(f"Loaded graph: {name}")
            
            return dataset
        
        except Exception as e:
            raise StorageError(f"Failed to load graph {name}: {e}")
    
    def save_graph(self, dataset: Dataset) -> None:
        """Save a graph dataset."""
        try:
            graph_path = self._get_graph_path(dataset.name)
            dataset.to_json(graph_path)
            
            # Update index
            self._index["graphs"][dataset.name] = {
                "path": str(graph_path),
                "created": dataset.created_at.isoformat(),
                "updated": dataset.updated_at.isoformat(),
                "metadata": dataset.metadata
            }
            self._save_index()
            
            self.logger.debug(f"Saved graph: {dataset.name}")
        
        except Exception as e:
            raise StorageError(f"Failed to save graph {dataset.name}: {e}")
    
    def delete_graph(self, name: str) -> None:
        """Delete a graph."""
        if name not in self._index["graphs"]:
            raise ValidationError(f"Graph '{name}' not found")
        
        try:
            graph_info = self._index["graphs"][name]
            graph_path = Path(graph_info["path"])
            
            # Delete file if it exists
            if graph_path.exists():
                graph_path.unlink()
            
            # Remove from index
            del self._index["graphs"][name]
            self._save_index()
            
            self.logger.info(f"Deleted graph: {name}")
        
        except Exception as e:
            raise StorageError(f"Failed to delete graph {name}: {e}")
    
    def list_graphs(self) -> List[str]:
        """List available graphs."""
        return list(self._index["graphs"].keys())
    
    def add_resource(self, graph_name: str, resource: Resource) -> None:
        """Add a resource to a graph."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            raise ValidationError(f"Graph '{graph_name}' not found")
        
        dataset.add_resource(resource)
        self.save_graph(dataset)
    
    def get_resource(self, graph_name: str, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            return None
        
        return dataset.get_resource(resource_id)
    
    def update_resource(self, graph_name: str, resource: Resource) -> None:
        """Update an existing resource."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            raise ValidationError(f"Graph '{graph_name}' not found")
        
        if resource.id not in dataset.resources:
            raise ValidationError(f"Resource {resource.id} not found in graph {graph_name}")
        
        dataset.resources[resource.id] = resource
        resource.updated_at = datetime.now(timezone.utc)
        
        self.save_graph(dataset)
    
    def delete_resource(self, graph_name: str, resource_id: str) -> None:
        """Delete a resource."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            raise ValidationError(f"Graph '{graph_name}' not found")
        
        dataset.remove_resource(resource_id)
        self.save_graph(dataset)
    
    def add_edge(self, graph_name: str, edge: Edge) -> None:
        """Add an edge to a graph."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            raise ValidationError(f"Graph '{graph_name}' not found")
        
        # Validate that source and target exist
        if edge.source not in dataset.resources:
            raise ValidationError(f"Source resource {edge.source} not found")
        if edge.target not in dataset.resources:
            raise ValidationError(f"Target resource {edge.target} not found")
        
        dataset.edges.append(edge)
        self.save_graph(dataset)
    
    def get_edges(self, graph_name: str, source: Optional[str] = None,
                  target: Optional[str] = None, edge_type: Optional[str] = None) -> List[Edge]:
        """Get edges matching criteria."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            return []
        
        return dataset.get_edges(source, target, edge_type)
    
    def delete_edge(self, graph_name: str, source: str, target: str, edge_type: str) -> None:
        """Delete an edge."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            raise ValidationError(f"Graph '{graph_name}' not found")
        
        original_count = len(dataset.edges)
        dataset.edges = [
            edge for edge in dataset.edges
            if not (edge.source == source and edge.target == target and edge.type == edge_type)
        ]
        
        if len(dataset.edges) == original_count:
            raise ValidationError(f"Edge not found: {source} -[{edge_type}]-> {target}")
        
        self.save_graph(dataset)
    
    def query(self, graph_name: str, query: str, **params) -> Any:
        """Execute a query against the graph."""
        dataset = self.load_graph(graph_name)
        if dataset is None:
            raise ValidationError(f"Graph '{graph_name}' not found")
        
        # Use in-memory NetworkX for queries
        try:
            import networkx as nx
            
            # Build NetworkX graph
            G = nx.DiGraph()
            
            for resource in dataset.resources.values():
                G.add_node(resource.id, **resource.properties)
            
            for edge in dataset.edges:
                G.add_edge(edge.source, edge.target, type=edge.type, **edge.properties)
            
            # Execute query
            if query == "neighbors":
                node_id = params.get("node_id")
                direction = params.get("direction", "both")
                
                if direction == "out":
                    return list(G.successors(node_id))
                elif direction == "in":
                    return list(G.predecessors(node_id))
                else:
                    return list(G.neighbors(node_id))
            
            else:
                raise ValidationError(f"Unsupported query: {query}")
        
        except ImportError:
            raise StorageError("NetworkX required for graph queries")
        except Exception as e:
            raise StorageError(f"Query execution failed: {e}")
    
    def get_graph_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a graph."""
        return self._index["graphs"].get(name)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total_size = 0
        for graph_name, graph_info in self._index["graphs"].items():
            graph_path = Path(graph_info["path"])
            if graph_path.exists():
                total_size += graph_path.stat().st_size
        
        return {
            "storage_path": str(self.storage_path),
            "graph_count": len(self._index["graphs"]),
            "total_size_bytes": total_size,
            "index_updated": self._index.get("updated", "unknown")
        }
    
    def close(self) -> None:
        """Close storage (save index)."""
        try:
            self._save_index()
            self.logger.info("FileStorage closed")
        except Exception as e:
            self.logger.error(f"Error closing FileStorage: {e}")
