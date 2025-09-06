"""
Format conversion utilities for different data representations.
"""

import json
import csv
from typing import Any, Dict, List, Optional, Union, Iterator
from pathlib import Path
from io import StringIO

from kgops.transforms.base import BaseTransform
from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.exceptions import TransformError
from kgops.utils.helpers import extract_entities_simple


class FormatConverter(BaseTransform):
    """
    Converts between different data formats and kgops objects.
    """
    
    def transform(self, resource: Resource, **kwargs) -> Resource:
        """Basic transform - mainly used for format conversion."""
        return resource
    
    def extract_entities(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract entities from text."""
        return extract_entities_simple(text)
    
    def extract_relations(self, text: str, entities: Optional[List[Dict[str, Any]]] = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract relations from text."""
        # Basic implementation - can be enhanced
        return []
    
    def csv_to_resources(self, csv_path: Union[str, Path], 
                        id_field: Optional[str] = None,
                        label_field: Optional[str] = None,
                        **kwargs) -> Iterator[Resource]:
        """Convert CSV data to Resource objects."""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Clean empty values
                    properties = {k: v for k, v in row.items() if v and v.strip()}
                    
                    # Extract ID
                    resource_id = None
                    if id_field and id_field in properties:
                        resource_id = properties.pop(id_field)
                    
                    # Extract labels
                    labels = set()
                    if label_field and label_field in properties:
                        label_value = properties.pop(label_field)
                        if isinstance(label_value, str):
                            labels = {l.strip() for l in label_value.split(',') if l.strip()}
                    
                    # Create resource
                    resource = Resource(
                        id=resource_id,
                        labels=labels,
                        properties=properties
                    )
                    
                    yield resource
        
        except Exception as e:
            raise TransformError(f"Failed to convert CSV to resources: {e}")
    
    def json_to_resources(self, json_path: Union[str, Path], 
                         id_field: str = "id",
                         label_field: str = "labels",
                         **kwargs) -> Iterator[Resource]:
        """Convert JSON data to Resource objects."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                # Try common field names for record arrays
                records = data.get('records', data.get('items', data.get('data', [data])))
            else:
                records = [data]
            
            for record in records:
                if not isinstance(record, dict):
                    continue
                
                properties = record.copy()
                
                # Extract ID
                resource_id = properties.pop(id_field, None)
                
                # Extract labels
                labels = set()
                if label_field in properties:
                    label_value = properties.pop(label_field)
                    if isinstance(label_value, list):
                        labels = set(label_value)
                    elif isinstance(label_value, str):
                        labels = {label_value}
                
                resource = Resource(
                    id=resource_id,
                    labels=labels,
                    properties=properties
                )
                
                yield resource
        
        except Exception as e:
            raise TransformError(f"Failed to convert JSON to resources: {e}")
    
    def resources_to_csv(self, resources: List[Resource], 
                        csv_path: Union[str, Path],
                        include_labels: bool = True,
                        **kwargs) -> None:
        """Convert Resource objects to CSV."""
        try:
            if not resources:
                return
            
            # Collect all property keys
            all_keys = set(['id'])
            if include_labels:
                all_keys.add('labels')
            
            for resource in resources:
                all_keys.update(resource.properties.keys())
            
            fieldnames = sorted(all_keys)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for resource in resources:
                    row = {'id': resource.id}
                    
                    if include_labels:
                        row['labels'] = ','.join(sorted(resource.labels))
                    
                    row.update(resource.properties)
                    
                    # Fill missing fields with empty strings
                    for field in fieldnames:
                        if field not in row:
                            row[field] = ''
                    
                    writer.writerow(row)
        
        except Exception as e:
            raise TransformError(f"Failed to convert resources to CSV: {e}")
    
    def dataset_to_graphml(self, dataset: Dataset, 
                          graphml_path: Union[str, Path],
                          **kwargs) -> None:
        """Convert Dataset to GraphML format."""
        try:
            import networkx as nx
            
            # Create NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes
            for resource in dataset.resources.values():
                node_attrs = {
                    'labels': ','.join(sorted(resource.labels)),
                    **{k: str(v) for k, v in resource.properties.items()}
                }
                G.add_node(resource.id, **node_attrs)
            
            # Add edges
            for edge in dataset.edges:
                edge_attrs = {
                    'type': edge.type,
                    **{k: str(v) for k, v in edge.properties.items()}
                }
                G.add_edge(edge.source, edge.target, **edge_attrs)
            
            # Write GraphML
            nx.write_graphml(G, graphml_path)
        
        except ImportError:
            raise TransformError("NetworkX required for GraphML export")
        except Exception as e:
            raise TransformError(f"Failed to convert to GraphML: {e}")
    
    def dataset_to_triples(self, dataset: Dataset,
                          format: str = "ntriples",
                          **kwargs) -> List[str]:
        """Convert Dataset to RDF triples."""
        triples = []
        
        try:
            # Convert resources to triples
            for resource in dataset.resources.values():
                subject = f"<http://kgops.dev/resource/{resource.id}>"
                
                # Type triples for labels
                for label in resource.labels:
                    triples.append(f"{subject} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://kgops.dev/type/{label}> .")
                
                # Property triples
                for prop, value in resource.properties.items():
                    predicate = f"<http://kgops.dev/property/{prop}>"
                    
                    # Handle different value types
                    if isinstance(value, str):
                        object_val = f'"{value}"'
                    elif isinstance(value, (int, float)):
                        object_val = f'"{value}"^^<http://www.w3.org/2001/XMLSchema#{"integer" if isinstance(value, int) else "double"}>'
                    elif isinstance(value, bool):
                        object_val = f'"{str(value).lower()}"^^<http://www.w3.org/2001/XMLSchema#boolean>'
                    else:
                        object_val = f'"{str(value)}"'
                    
                    triples.append(f"{subject} {predicate} {object_val} .")
            
            # Convert edges to triples
            for edge in dataset.edges:
                subject = f"<http://kgops.dev/resource/{edge.source}>"
                predicate = f"<http://kgops.dev/relation/{edge.type}>"
                object_val = f"<http://kgops.dev/resource/{edge.target}>"
                
                triples.append(f"{subject} {predicate} {object_val} .")
            
            return triples
        
        except Exception as e:
            raise TransformError(f"Failed to convert to triples: {e}")
