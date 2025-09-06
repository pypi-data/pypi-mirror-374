"""
Serialization utilities for kgops objects.
"""

import json
import pickle
from typing import Any, Dict, List, Union
from datetime import datetime
from pathlib import Path

from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.exceptions import KGOpsError


class KGOpsJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for kgops objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Resource):
            return obj.to_dict()
        elif isinstance(obj, Edge):
            return obj.to_dict()
        elif isinstance(obj, Dataset):
            return obj.to_dict()
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        return super().default(obj)


def serialize_resource(resource: Resource, format: str = "json") -> Union[str, bytes]:
    """Serialize a resource to various formats."""
    if format.lower() == "json":
        return json.dumps(resource.to_dict(), cls=KGOpsJSONEncoder, ensure_ascii=False, indent=2)
    elif format.lower() == "pickle":
        return pickle.dumps(resource)
    else:
        raise ValueError(f"Unsupported serialization format: {format}")


def deserialize_resource(data: Union[str, bytes], format: str = "json") -> Resource:
    """Deserialize data to a Resource object."""
    try:
        if format.lower() == "json":
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            resource_dict = json.loads(data)
            return Resource.from_dict(resource_dict)
        elif format.lower() == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported deserialization format: {format}")
    except Exception as e:
        raise KGOpsError(f"Failed to deserialize resource: {e}")


def serialize_dataset(dataset: Dataset, format: str = "json") -> Union[str, bytes]:
    """Serialize a dataset to various formats."""
    if format.lower() == "json":
        return json.dumps(dataset.to_dict(), cls=KGOpsJSONEncoder, ensure_ascii=False, indent=2)
    elif format.lower() == "pickle":
        return pickle.dumps(dataset)
    else:
        raise ValueError(f"Unsupported serialization format: {format}")


def deserialize_dataset(data: Union[str, bytes], format: str = "json") -> Dataset:
    """Deserialize data to a Dataset object."""
    try:
        if format.lower() == "json":
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            dataset_dict = json.loads(data)
            return Dataset.from_dict(dataset_dict)
        elif format.lower() == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported deserialization format: {format}")
    except Exception as e:
        raise KGOpsError(f"Failed to deserialize dataset: {e}")


def save_to_file(obj: Union[Resource, Dataset], path: Union[str, Path], format: str = "auto") -> None:
    """Save object to file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "auto":
        format = path.suffix.lower().lstrip('.')
    
    try:
        if isinstance(obj, Resource):
            data = serialize_resource(obj, format)
        elif isinstance(obj, Dataset):
            data = serialize_dataset(obj, format)
        else:
            raise ValueError(f"Unsupported object type: {type(obj)}")
        
        if format in ["json"]:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(data)
        else:  # binary formats
            with open(path, 'wb') as f:
                f.write(data)
    except Exception as e:
        raise KGOpsError(f"Failed to save to file: {e}")


def load_from_file(path: Union[str, Path], obj_type: str, format: str = "auto") -> Union[Resource, Dataset]:
    """Load object from file."""
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if format == "auto":
        format = path.suffix.lower().lstrip('.')
    
    try:
        if format in ["json"]:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
        else:  # binary formats
            with open(path, 'rb') as f:
                data = f.read()
        
        if obj_type.lower() == "resource":
            return deserialize_resource(data, format)
        elif obj_type.lower() == "dataset":
            return deserialize_dataset(data, format)
        else:
            raise ValueError(f"Unsupported object type: {obj_type}")
    
    except Exception as e:
        raise KGOpsError(f"Failed to load from file: {e}")
