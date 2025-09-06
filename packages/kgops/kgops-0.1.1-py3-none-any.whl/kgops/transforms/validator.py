"""
Validation transforms for ensuring data quality.
"""

from typing import Any, Dict, List, Optional, Union, Set
import re
from datetime import datetime

from kgops.transforms.base import BaseTransform
from kgops.core.resource import Resource
from kgops.core.exceptions import TransformError, ValidationError
from kgops.utils.helpers import validate_email, validate_url


class DataValidator(BaseTransform):
    """
    Validates and cleans resource data according to schema rules.
    """
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None, strict: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema or {}
        self.strict = strict  # If True, raise errors; if False, log warnings
        self.validation_errors = []
    
    def transform(self, resource: Resource, **kwargs) -> Resource:
        """Validate and potentially fix a resource."""
        self.validation_errors = []
        
        try:
            # Validate labels
            resource = self._validate_labels(resource)
            
            # Validate properties
            resource = self._validate_properties(resource)
            
            # Apply data cleaning
            resource = self._clean_data(resource)
            
            # Validate against schema if provided
            if self.schema:
                resource = self._validate_against_schema(resource)
            
            return resource
        except Exception as e:
            if self.strict:
                raise TransformError(f"Validation failed for resource {resource.id}: {e}")
            else:
                # Log error but return resource
                self.validation_errors.append(str(e))
                return resource
    
    def _validate_labels(self, resource: Resource) -> Resource:
        """Validate resource labels."""
        valid_labels = set()
        
        for label in resource.labels:
            if not isinstance(label, str) or not label.strip():
                error_msg = f"Invalid label: {label}"
                self._handle_validation_error(error_msg)
                continue
            
            # Clean label
            clean_label = label.strip()
            if clean_label:
                valid_labels.add(clean_label)
        
        resource.labels = valid_labels
        return resource
    
    def _validate_properties(self, resource: Resource) -> Resource:
        """Validate resource properties."""
        valid_properties = {}
        
        for key, value in resource.properties.items():
            if not isinstance(key, str) or not key.strip():
                error_msg = f"Invalid property key: {key}"
                self._handle_validation_error(error_msg)
                continue
            
            # Validate specific property types
            clean_key = key.strip()
            clean_value = self._validate_property_value(clean_key, value)
            
            if clean_value is not None:
                valid_properties[clean_key] = clean_value
        
        resource.properties = valid_properties
        return resource
    
    def _validate_property_value(self, key: str, value: Any) -> Any:
        """Validate a single property value."""
        if value is None:
            return None
        
        # Email validation
        if "email" in key.lower() and isinstance(value, str):
            if not validate_email(value):
                error_msg = f"Invalid email format: {value}"
                self._handle_validation_error(error_msg)
                return None if self.strict else value
        
        # URL validation
        if "url" in key.lower() and isinstance(value, str):
            if not validate_url(value):
                error_msg = f"Invalid URL format: {value}"
                self._handle_validation_error(error_msg)
                return None if self.strict else value
        
        # Date validation
        if "date" in key.lower() and isinstance(value, str):
            try:
                # Try to parse as ISO date
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                error_msg = f"Invalid date format: {value}"
                self._handle_validation_error(error_msg)
                return None if self.strict else value
        
        return value
    
    def _clean_data(self, resource: Resource) -> Resource:
        """Apply data cleaning operations."""
        cleaned_properties = {}
        
        for key, value in resource.properties.items():
            cleaned_value = self._clean_value(value)
            if cleaned_value is not None:
                cleaned_properties[key] = cleaned_value
        
        resource.properties = cleaned_properties
        return resource
    
    def _clean_value(self, value: Any) -> Any:
        """Clean a single value."""
        if isinstance(value, str):
            # Strip whitespace
            value = value.strip()
            
            # Remove empty strings
            if not value:
                return None
            
            # Normalize common variations
            if value.lower() in ["null", "none", "n/a", "na", ""]:
                return None
        
        return value
    
    def _validate_against_schema(self, resource: Resource) -> Resource:
        """Validate resource against provided schema."""
        if "labels" in self.schema:
            required_labels = set(self.schema["labels"].get("required", []))
            allowed_labels = set(self.schema["labels"].get("allowed", []))
            
            # Check required labels
            missing_labels = required_labels - resource.labels
            if missing_labels:
                error_msg = f"Missing required labels: {missing_labels}"
                self._handle_validation_error(error_msg)
            
            # Check allowed labels
            if allowed_labels:
                invalid_labels = resource.labels - allowed_labels
                if invalid_labels:
                    error_msg = f"Invalid labels: {invalid_labels}"
                    self._handle_validation_error(error_msg)
        
        if "properties" in self.schema:
            schema_props = self.schema["properties"]
            
            # Check required properties
            required_props = {k for k, v in schema_props.items() 
                            if isinstance(v, dict) and v.get("required", False)}
            missing_props = required_props - set(resource.properties.keys())
            if missing_props:
                error_msg = f"Missing required properties: {missing_props}"
                self._handle_validation_error(error_msg)
            
            # Validate property types
            for prop_name, prop_value in resource.properties.items():
                if prop_name in schema_props:
                    prop_schema = schema_props[prop_name]
                    if not self._validate_type(prop_value, prop_schema):
                        error_msg = f"Property {prop_name} has invalid type"
                        self._handle_validation_error(error_msg)
        
        return resource
    
    def _validate_type(self, value: Any, type_schema: Dict[str, Any]) -> bool:
        """Validate value against type schema."""
        expected_type = type_schema.get("type")
        
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        
        return True  # No type specified
    
    def _handle_validation_error(self, error_msg: str) -> None:
        """Handle validation error based on strict mode."""
        self.validation_errors.append(error_msg)
        if self.strict:
            raise ValidationError(error_msg)
    
    def extract_entities(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract entities with validation."""
        # Basic implementation
        return []
    
    def extract_relations(self, text: str, entities: Optional[List[Dict[str, Any]]] = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract relations with validation."""
        # Basic implementation
        return []
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report."""
        return {
            "errors": self.validation_errors,
            "error_count": len(self.validation_errors)
        }
