"""
Validation utilities for kgops components.
"""

from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime

from kgops.core.resource import Resource
from kgops.core.dataset import Edge
from kgops.core.exceptions import ValidationError


def validate_resource(resource: Resource, strict: bool = True) -> bool:
    """Validate a resource instance."""
    try:
        # Check required fields
        if not resource.id:
            raise ValidationError("Resource must have an ID")
        
        if not isinstance(resource.id, str):
            raise ValidationError("Resource ID must be a string")
        
        # Validate labels
        if not isinstance(resource.labels, set):
            raise ValidationError("Resource labels must be a set")
        
        for label in resource.labels:
            if not isinstance(label, str) or not label.strip():
                raise ValidationError("All labels must be non-empty strings")
        
        # Validate properties
        if not isinstance(resource.properties, dict):
            raise ValidationError("Resource properties must be a dictionary")
        
        for key in resource.properties.keys():
            if not isinstance(key, str):
                raise ValidationError("Property keys must be strings")
        
        # Validate embeddings (if present)
        if resource.embeddings is not None:
            if not isinstance(resource.embeddings, dict):
                raise ValidationError("Embeddings must be a dictionary")
            
            for name, embedding in resource.embeddings.items():
                if not isinstance(name, str):
                    raise ValidationError("Embedding names must be strings")
                
                if not isinstance(embedding, list):
                    raise ValidationError("Embeddings must be lists")
                
                if not all(isinstance(x, (int, float)) for x in embedding):
                    raise ValidationError("Embedding values must be numbers")
        
        # Validate timestamps
        if not isinstance(resource.created_at, datetime):
            raise ValidationError("created_at must be a datetime")
        
        if not isinstance(resource.updated_at, datetime):
            raise ValidationError("updated_at must be a datetime")
        
        return True
        
    except ValidationError:
        if strict:
            raise
        return False


def validate_edge(edge: Edge, strict: bool = True) -> bool:
    """Validate an edge instance."""
    try:
        # Check required fields
        if not edge.source:
            raise ValidationError("Edge must have a source")
        
        if not edge.target:
            raise ValidationError("Edge must have a target")
        
        if not edge.type:
            raise ValidationError("Edge must have a type")
        
        # Validate field types
        if not isinstance(edge.source, str):
            raise ValidationError("Edge source must be a string")
        
        if not isinstance(edge.target, str):
            raise ValidationError("Edge target must be a string")
        
        if not isinstance(edge.type, str):
            raise ValidationError("Edge type must be a string")
        
        # Validate properties
        if not isinstance(edge.properties, dict):
            raise ValidationError("Edge properties must be a dictionary")
        
        for key in edge.properties.keys():
            if not isinstance(key, str):
                raise ValidationError("Edge property keys must be strings")
        
        # Validate timestamp
        if not isinstance(edge.created_at, datetime):
            raise ValidationError("Edge created_at must be a datetime")
        
        return True
        
    except ValidationError:
        if strict:
            raise
        return False


def validate_identifier(identifier: str, pattern: Optional[str] = None) -> bool:
    """Validate an identifier string."""
    if not isinstance(identifier, str):
        return False
    
    if not identifier.strip():
        return False
    
    if pattern:
        return bool(re.match(pattern, identifier))
    
    # Default pattern: alphanumeric, hyphens, underscores
    default_pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(default_pattern, identifier))


def validate_property_value(value: Any) -> bool:
    """Validate that a property value is serializable."""
    try:
        import json
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def validate_embedding_vector(embedding: List[float], expected_dim: Optional[int] = None) -> bool:
    """Validate an embedding vector."""
    if not isinstance(embedding, list):
        return False
    
    if not embedding:  # Empty list
        return False
    
    if not all(isinstance(x, (int, float)) for x in embedding):
        return False
    
    if expected_dim is not None and len(embedding) != expected_dim:
        return False
    
    # Check for NaN or infinite values
    import math
    for val in embedding:
        if math.isnan(val) or math.isinf(val):
            return False
    
    return True


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input."""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip()
    
    return text


def validate_configuration(config: Dict[str, Any]) -> List[str]:
    """Validate configuration dictionary and return list of errors."""
    errors = []
    
    # Check required fields
    required_fields = ["graph", "version"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate graph configuration
    if "graph" in config:
        graph_config = config["graph"]
        if not isinstance(graph_config, dict):
            errors.append("Graph configuration must be a dictionary")
        else:
            if "backend" not in graph_config:
                errors.append("Graph backend not specified")
            elif graph_config["backend"] not in ["networkx"]:  # Add more backends later
                errors.append(f"Unsupported backend: {graph_config['backend']}")
    
    # Validate tenant configuration (if present)
    if "tenant" in config:
        tenant_config = config["tenant"]
        if not isinstance(tenant_config, dict):
            errors.append("Tenant configuration must be a dictionary")
        else:
            required_tenant_fields = ["tenant_id", "name"]
            for field in required_tenant_fields:
                if field not in tenant_config:
                    errors.append(f"Missing tenant field: {field}")
    
    return errors
