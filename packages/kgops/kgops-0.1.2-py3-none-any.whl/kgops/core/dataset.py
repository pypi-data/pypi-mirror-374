"""
Dataset management for collections of resources and relationships.
[
Edge,
Dataset,

]
"""

from typing import List, Dict, Optional, Any, Union, Tuple, Iterator
from pathlib import Path
import json
import yaml
import csv
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, ConfigDict
from kgops.core.resource import Resource
from kgops.core.exceptions import DatasetError, ValidationError


class Edge(BaseModel):
    """
    Represents a relationship between two resources in a dataset.
    [source, target, type, properties, created_at]
    """
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    source : str= Field(description="source resource ID")
    target : str= Field(description="target resource ID")
    type : str= Field(description="type of relationship")
    properties : Dict[str, Any]= Field(default_factory=dict, description="additional edge properties")
    created_at : datetime= Field(default_factory=lambda: datetime.now(timezone.utc), description="timestamp of creation")
    updated_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="timestamp of last update")

    def to_dict(self) -> Dict[str,Any]:
        """
        converts an edge into a dictionary representation
        """
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "properties": self.properties.copy(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """
        creates an edge from a dictionary representation
        """
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        return cls(**data)
    

class Dataset(BaseModel):
    """
    Container for resources and edges representing a knowledge graph dataset.
    [name, description, version, resources, edges, metadata, created_at, updated_at]
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    name : str = Field(description="Name of the dataset")
    description: Optional[str]= Field(default=None, description="Description of the dataset")
    version : str = Field(default="1.0.0", description="Version of the dataset")
    resources : Dict[str, Resource]= Field(default_factory=dict, description="Resources in the dataset by ID")
    edges : List[Edge]= Field(default_factory=list, description="Edges/Relationships in the dataset")
    metadata : Dict[str, Any]= Field(default_factory=dict, description="Metadata for the dataset")
    created_at : datetime= Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of creation")
    updated_at : datetime= Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of last update")

    def add_resource(self, resource: Resource) -> None:
        """
        Add a resource to the dataset.
        """
        if not isinstance(resource, Resource):
            raise ValidationError("resource must be an instance of Resource.")
        
        self.resources[resource.id] = resource
        self.updated_at = datetime.now(timezone.utc)

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Get a resource by its ID.
        """
        return self.resources.get(resource_id)
    
    def remove_resource(self, resource_id :str) -> None:
        """
        Remove a resource and all the associated edges from the dataset.
        """
        if resource_id not in self.resources:
            return 
        
        # remove the resource
        del self.resources[resource_id]

        # remove associated edges
        self.edges = [
            edge for edge in self.edges if edge.source != resource_id and edge.target != resource_id
        ]
        
        self.updated_at = datetime.now(timezone.utc)

    def add_edge(self, source_id:str, target_id:str, edge_type:str, properties:Optional[Dict[str,Any]]=None) -> Edge:
        """
        Add an edge between two resources in the dataset.
        """
            # validate that the resource exists
        if source_id not in self.resources:
            raise ValidationError(f"Source resource {source_id} does not exist in the dataset.")
        if target_id not in self.resources:
            raise ValidationError(f"Target resource {target_id} does not exist in the dataset.")

        edge = Edge(
                source=source_id,
                target=target_id,
                type=edge_type,
                properties=properties or {}
            )
        self.edges.append(edge)
        self.updated_at = datetime.now(timezone.utc)

        return edge
    
    def get_edges(self, source_id: Optional[str]=None,target_id : Optional[str] = None, edge_type: Optional[str]=None) -> List[Edge]:
        """
        Get the edges matching the criteria
        """
        filtered_edges = self.edges

        if source_id is not None:
            filtered_edges = [edge for edge in filtered_edges if edge.source == source_id]

        if target_id is not None:
            filtered_edges = [edge for edge in filtered_edges if edge.target == target_id]
        
        if edge_type is not None :
            filtered_edges = [edge for edge in filtered_edges if edge.type == edge_type]

        return filtered_edges
    
    def get_neighbors(self, resource_id : str, direction: str = "both") -> List[str]:
        """
        Get neighbouring resource IDs
        """
        neighbours = set()
        for edge in self.edges:
            if direction in ["out", "both"] and edge.source == resource_id:
                neighbours.add(edge.target)
            elif direction in ["in", "both"] and edge.target == resource_id:
                neighbours.add(edge.source)
        return list(neighbours)
    
    def get_resources_by_label(self, label:str)-> List[Resource]:
        """
        Get resources by their label.
        """
        return [resource for resource in self.resources.values() if resource.has_label(label)]
    
    def get_resources_by_property(self, key:str, value:Any = None) -> List[Resource]:
        """
        Get resources by a specific property key-value pair.
        """
        if value is None:
            return [resource for resource in self.resources.values()
                    if resource.has_property(key)]
        else:    
            return [resource for resource in self.resources.values() if resource.get_property(key) == value]
        
    def filter_resources(self, filter_func) -> List[Resource]:
        """Filter resources based on a custom filter function."""
        return [resource for resource in self.resources.values() if filter_func(resource)]
    
    def stats(self) -> Dict[str, Any]:
        """
        Get dataset statistics.
        """

        label_counts= {}
        edge_type_counts = {}

        for resource in self.resources.values():
            for label in resource.labels:
                label_counts[label] = label_counts.get(label, 0) + 1

        for edge in self.edges:
            edge_type_counts[edge.type] = edge_type_counts.get(edge.type, 0) + 1

        return {
            "resources": len(self.resources),
            "edges": len(self.edges),
            "labels": label_counts,
            "edge_types": edge_type_counts,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        converts a dataset into a dictionary representation
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "resources": {rid: resource.to_dict() for rid, resource in self.resources.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata.copy(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data:Dict[str, Any]) -> "Dataset":
        """
        creates a dataset from a dictionary representation
        """
        try:
            if "created_at" in data and isinstance(data["created_at"], str):
                    data["created_at"] = datetime.fromisoformat(data["created_at"])
                
            if "updated_at" in data and isinstance(data["updated_at"], str):
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                
            resources = {}
            
            # parse resources
            if "resources" in data:
                for rid, resource_data in data["resources"].items():
                    resources[rid] = Resource.from_dict(resource_data)
                data["resources"] = resources
            # parse edges
            if "edges" in data:
                edges = []
                for edge_data in data["edges"]:
                    edges.append(Edge.from_dict(edge_data))
                data["edges"] = edges
            return cls(**data)
        except Exception as e:
            raise DatasetError(f"Failed to create Dataset from dict: {e}")
        
    def to_json(self, path: Optional[Union[str, Path]]=None) -> Optional[str]:
        """
        save dataset to JSON file or return JSON string
        """
        json_data = json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

        if path is not None:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            return None
        
        return json_data
    
    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "Dataset":
        """Load dataset from JSON file."""
        try:
            path = Path(path)
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return cls.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise DatasetError(f"Failed to load dataset from JSON: {e}")
    
    def __len__(self) -> int:
        """Return number of resources in dataset."""
        return len(self.resources)
    
    def __iter__(self) -> Iterator[Resource]:
        """Iterate over resources in dataset."""
        return iter(self.resources.values())
    
    def __str__(self) -> str:
        return f"Dataset(name={self.name}, resources={len(self.resources)}, edges={len(self.edges)})"
