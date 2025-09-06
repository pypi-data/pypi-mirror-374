"""
Resource Management for kgops operations
[
Resource[validate_labels, validate_properties, add_label, remove_label, set_property, get_property, remove_property]
]
"""

from typing import Any, Dict, List, Optional, Union, Set
from uuid import uuid4
from datetime import datetime, timezone
import json
from pydantic import BaseModel, Field, field_validator, ConfigDict

from kgops.core.exceptions import ResourceError, ValidationError


class Resource(BaseModel):
    """
    Represents a node/Entity in a Knowledge Graph.
    [id,labels, properties, embeddings, created_at, updated_at]
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            set: list,
        }
    )
    
    id : str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the resource")
    labels : Set[str] = Field(default_factory=set, description="Labels or types associated with the resource")
    properties : Dict[str, Any] = Field(default_factory=dict, description="Properties or attributes of the resource")
    embeddings : Optional[Dict[str, List[float]]] = Field(default=None, description="Embeddings for the resource (if any)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last updated timestamp")

    @field_validator('labels')
    def validate_labels(cls, v):
        if isinstance(v, (set, list)):
            v= set(v)
        if not isinstance(v, set):
            raise ValidationError("Labels must be a set or list of strings.")
        
        for label in v:
            if not isinstance(label, str) or not label.strip():
                raise ValidationError("Each label must be a non-empty string")
        
        return v


    @field_validator('properties')
    def validate_properties(cls, v):
        """
        validate properties dictionary
        properties must be a dict
        keys must be a str 
        """

        if not isinstance(v,dict):
            raise ValidationError('properties must be a dictionary')
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValidationError('property keys must be strings')
        
        return v
    
    def add_label(self, label:str) -> None:
        """
        Add a label to the resource
        """

        if not isinstance(label, str) or not label.strip():
            raise ValidationError("Label must be a non-empty string.")
        
        self.labels.add(label.strip())
        self.updated_at = datetime.now(timezone.utc)


    def remove_label(self, label:str) -> None:
        """
        Remove lable from the resource
        """

        self.labels.discard(label)
        self.updated_at = datetime.now(timezone.utc)

    def set_property(self, key:str, value:Any) -> None:
        """
        Set a property for the resource
        """

        if not isinstance(key, str):
            raise ValidationError("Property key must be a string.")
        
        self.properties[key] = value
        self.updated_at = datetime.now(timezone.utc)

    
    def get_property(self, key:str) -> Any:
        """
        get a property value
        """
        return self.properties.get(key)
    
    def remove_property(self, key:str) -> None:
        """
        remove a property from the resource.
        """
        self.properties.pop(key)
        self.updated_at = datetime.now(timezone.utc)    

    def set_embedding(self, name:str , embedding: List[float])-> None:
        """
        Set an embedding for the resource
        """

        if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
            raise ValidationError("Embedding must be a list of numbers")
        
        if self.embeddings is None:
            self.embeddings = {}
        
        self.embeddings[name] = embedding
        self.updated_at = datetime.now(timezone.utc)

    
    def get_embedding(self, name:str) -> Optional[List[float]]:
        """
        Get the embedding vector
        """
        if self.embeddings is None:
            return None
        return self.embeddings.get(name)

    def has_label(self, label: str) -> bool:
        """
        Check if the resource has a specific label
        """
        return label in self.labels
    
    def has_property(self, key:str)->bool:
        """
        Check if the resource has a specific property
        """
        return key in self.properties
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Resource to a dictionary representation
        """
        return {
            "id": self.id,
            "labels": list(self.labels),
            "properties": self.properties.copy(),
            "embeddings": self.embeddings.copy() if self.embeddings else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resource":
        """
        Create a Resource instance from a dictionary representation
        """
        try:
            # Handle datetime parsing
            if "created_at" in data and isinstance(data["created_at"], str):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            
            if "updated_at" in data and isinstance(data["updated_at"], str):
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            return cls(
                **data
            )
        except Exception as e:
            raise ResourceError(f"Failed to create Resource from dict: {e}")
        
    def to_json(self) -> str:
        """Convert resource to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str:str) -> "Resource":
        """Create Resource instance from JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ResourceError(f"Failed to decode JSON: {e}")
        except Exception as e:
            raise ResourceError(f"Failed to create Resource from JSON: {e}")
            
    def __str__(self) -> str:
        labels_str = ", ".join(sorted(self.labels)) if self.labels else "No labels"
        return f"Resource(id={self.id}, labels=[{labels_str}], properties={len(self.properties)})"
    
    def __repr__(self) -> str:
        return self.__str__()
