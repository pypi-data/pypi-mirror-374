"""
Schema mapping implementation.
"""

from typing import Any, Dict, List, Optional, Union
import json
from pathlib import Path

from kgops.mappings.base import BaseMapping
from kgops.core.exceptions import ValidationError
from kgops.utils.validation import validate_property_value


class SchemaMapper(BaseMapping):
    """
    Maps data according to JSON schema definitions.
    """
    
    def __init__(self, schema_path: Optional[Union[str, Path]] = None, 
                 schema_dict: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        
        if schema_path:
            self.schema = self._load_schema(schema_path)
        elif schema_dict:
            self.schema = schema_dict
        else:
            # Default basic schema
            self.schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
        
        # Extract mapping rules from schema
        self.property_mappings = self.schema.get("mappings", {}).get("properties", {})
        self.label_mappings = self.schema.get("mappings", {}).get("labels", {})
    
    def _load_schema(self, schema_path: Union[str, Path]) -> Dict[str, Any]:
        """Load schema from file."""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValidationError(f"Failed to load schema: {e}")
    
    def map_properties(self, source_props: Dict[str, Any]) -> Dict[str, Any]:
        """Map source properties to target schema."""
        mapped_props = {}
        
        for source_key, value in source_props.items():
            # Apply property mapping
            target_key = self.property_mappings.get(source_key, source_key)
            
            # Apply value transformation if specified
            transformed_value = self._transform_value(target_key, value)
            
            mapped_props[target_key] = transformed_value
        
        return mapped_props
    
    def map_labels(self, source_labels: List[str]) -> List[str]:
        """Map source labels to target ontology."""
        mapped_labels = []
        
        for label in source_labels:
            mapped_label = self.label_mappings.get(label, label)
            mapped_labels.append(mapped_label)
        
        return mapped_labels
    
    def _transform_value(self, property_name: str, value: Any) -> Any:
        """Transform value according to schema rules."""
        prop_schema = self.schema.get("properties", {}).get(property_name, {})
        
        # Type conversion
        target_type = prop_schema.get("type")
        if target_type:
            try:
                if target_type == "string":
                    value = str(value)
                elif target_type == "integer":
                    value = int(float(str(value)))
                elif target_type == "number":
                    value = float(str(value))
                elif target_type == "boolean":
                    if isinstance(value, str):
                        value = value.lower() in ["true", "1", "yes", "on"]
                    else:
                        value = bool(value)
            except (ValueError, TypeError):
                # Keep original value if conversion fails
                pass
        
        # Apply constraints
        if "minLength" in prop_schema and isinstance(value, str):
            if len(value) < prop_schema["minLength"]:
                raise ValidationError(f"Property {property_name} too short")
        
        if "maxLength" in prop_schema and isinstance(value, str):
            if len(value) > prop_schema["maxLength"]:
                value = value[:prop_schema["maxLength"]]
        
        return value
    
    def validate_mapping(self, mapped_data: Dict[str, Any]) -> bool:
        """Validate mapped data against target schema."""
        try:
            # Check required properties
            required = self.schema.get("required", [])
            for req_prop in required:
                if req_prop not in mapped_data:
                    raise ValidationError(f"Required property missing: {req_prop}")
            
            # Validate property types and constraints
            properties_schema = self.schema.get("properties", {})
            for prop_name, value in mapped_data.items():
                if prop_name in properties_schema:
                    prop_schema = properties_schema[prop_name]
                    if not self._validate_property(value, prop_schema):
                        raise ValidationError(f"Property {prop_name} validation failed")
            
            return True
        
        except ValidationError:
            return False
    
    def _validate_property(self, value: Any, prop_schema: Dict[str, Any]) -> bool:
        """Validate a single property against its schema."""
        prop_type = prop_schema.get("type")
        
        # Type validation
        if prop_type == "string" and not isinstance(value, str):
            return False
        elif prop_type == "integer" and not isinstance(value, int):
            return False
        elif prop_type == "number" and not isinstance(value, (int, float)):
            return False
        elif prop_type == "boolean" and not isinstance(value, bool):
            return False
        elif prop_type == "array" and not isinstance(value, list):
            return False
        elif prop_type == "object" and not isinstance(value, dict):
            return False
        
        # Additional validations
        if prop_type == "string" and isinstance(value, str):
            if "minLength" in prop_schema and len(value) < prop_schema["minLength"]:
                return False
            if "maxLength" in prop_schema and len(value) > prop_schema["maxLength"]:
                return False
            if "pattern" in prop_schema:
                import re
                if not re.match(prop_schema["pattern"], value):
                    return False
        
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the target schema definition."""
        return self.schema.copy()
    
    def add_property_mapping(self, source_prop: str, target_prop: str) -> None:
        """Add a property mapping rule."""
        if "mappings" not in self.schema:
            self.schema["mappings"] = {"properties": {}, "labels": {}}
        
        self.schema["mappings"]["properties"][source_prop] = target_prop
        self.property_mappings[source_prop] = target_prop
    
    def add_label_mapping(self, source_label: str, target_label: str) -> None:
        """Add a label mapping rule."""
        if "mappings" not in self.schema:
            self.schema["mappings"] = {"properties": {}, "labels": {}}
        
        self.schema["mappings"]["labels"][source_label] = target_label
        self.label_mappings[source_label] = target_label
