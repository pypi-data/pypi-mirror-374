"""
Data mapping and transformation utilities.
"""

from typing import Any, Dict, List, Optional, Union, Callable
import re
from datetime import datetime

from kgops.transforms.base import BaseTransform
from kgops.core.resource import Resource
from kgops.core.exceptions import TransformError, ValidationError
from kgops.utils.helpers import normalize_string, safe_json_loads


class DataMapper(BaseTransform):
    """
    Maps and transforms data according to specified rules and schemas.
    """
    
    def __init__(self, mapping_rules: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.mapping_rules = mapping_rules or {}
    
    def transform(self, resource: Resource, **kwargs) -> Resource:
        """Transform a resource according to mapping rules."""
        if not self.mapping_rules:
            return resource
        
        try:
            # Apply property mappings
            if "property_mappings" in self.mapping_rules:
                resource = self._apply_property_mappings(resource)
            
            # Apply label mappings
            if "label_mappings" in self.mapping_rules:
                resource = self._apply_label_mappings(resource)
            
            # Apply value transformations
            if "value_transforms" in self.mapping_rules:
                resource = self._apply_value_transforms(resource)
            
            return resource
        except Exception as e:
            raise TransformError(f"Mapping failed for resource {resource.id}: {e}")
    
    def _apply_property_mappings(self, resource: Resource) -> Resource:
        """Apply property name mappings."""
        mappings = self.mapping_rules.get("property_mappings", {})
        new_properties = {}
        
        for old_key, new_key in mappings.items():
            if old_key in resource.properties:
                new_properties[new_key] = resource.properties.pop(old_key)
        
        resource.properties.update(new_properties)
        return resource
    
    def _apply_label_mappings(self, resource: Resource) -> Resource:
        """Apply label mappings."""
        mappings = self.mapping_rules.get("label_mappings", {})
        new_labels = set()
        
        for label in resource.labels:
            mapped_label = mappings.get(label, label)
            new_labels.add(mapped_label)
        
        resource.labels = new_labels
        return resource
    
    def _apply_value_transforms(self, resource: Resource) -> Resource:
        """Apply value transformation rules."""
        transforms = self.mapping_rules.get("value_transforms", {})
        
        for prop_name, transform_rule in transforms.items():
            if prop_name in resource.properties:
                try:
                    old_value = resource.properties[prop_name]
                    new_value = self._apply_transform_rule(old_value, transform_rule)
                    resource.properties[prop_name] = new_value
                except Exception as e:
                    # Log warning but continue
                    pass
        
        return resource
    
    def _apply_transform_rule(self, value: Any, rule: Dict[str, Any]) -> Any:
        """Apply a single transform rule to a value."""
        transform_type = rule.get("type", "identity")
        
        if transform_type == "normalize_string":
            return normalize_string(str(value), 
                                  lowercase=rule.get("lowercase", True),
                                  remove_special=rule.get("remove_special", False))
        
        elif transform_type == "regex_extract":
            pattern = rule.get("pattern")
            if pattern and isinstance(value, str):
                match = re.search(pattern, value)
                return match.group(1) if match and match.groups() else value
        
        elif transform_type == "type_cast":
            target_type = rule.get("target_type")
            if target_type == "int":
                return int(float(str(value)))
            elif target_type == "float":
                return float(str(value))
            elif target_type == "str":
                return str(value)
            elif target_type == "bool":
                return str(value).lower() in ["true", "1", "yes", "on"]
        
        elif transform_type == "date_parse":
            format_str = rule.get("format", "%Y-%m-%d")
            if isinstance(value, str):
                return datetime.strptime(value, format_str).isoformat()
        
        return value  # Identity transform
    
    def extract_entities(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract entities using mapping rules."""
        # Basic implementation - can be extended
        return []
    
    def extract_relations(self, text: str, entities: Optional[List[Dict[str, Any]]] = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract relations using mapping rules."""
        # Basic implementation - can be extended
        return []


def create_mapping_from_sample(sample_data: Dict[str, Any], 
                              target_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Create mapping rules by comparing sample data to target schema."""
    mapping_rules = {
        "property_mappings": {},
        "label_mappings": {},
        "value_transforms": {}
    }
    
    # Simple heuristic mapping based on key similarity
    sample_keys = set(sample_data.keys())
    target_keys = set(target_schema.get("properties", {}).keys())
    
    for sample_key in sample_keys:
        # Exact match
        if sample_key in target_keys:
            continue
        
        # Fuzzy matching
        normalized_sample = normalize_string(sample_key)
        for target_key in target_keys:
            normalized_target = normalize_string(target_key)
            
            # Simple similarity check
            if (normalized_sample in normalized_target or 
                normalized_target in normalized_sample or
                normalized_sample.replace("_", "") == normalized_target.replace("_", "")):
                mapping_rules["property_mappings"][sample_key] = target_key
                break
    
    return mapping_rules
