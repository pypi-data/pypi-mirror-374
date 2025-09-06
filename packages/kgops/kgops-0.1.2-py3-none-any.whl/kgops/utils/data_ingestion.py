"""
Data ingestion utilities for various file formats.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import json
import logging
from uuid import uuid4

import pandas as pd

from kgops.core.resource import Resource
from kgops.core.exceptions import KGOpsError, ValidationError


logger = logging.getLogger(__name__)


class DataIngestionError(KGOpsError):
    """Exception raised during data ingestion operations."""
    pass


class FileIngester:
    """
    File ingestion utility for converting various file formats to Resources.
    """
    
    def __init__(self):
        self.supported_formats = {
            '.csv': self._ingest_csv,
            '.json': self._ingest_json,
            '.jsonl': self._ingest_jsonl,
            '.xlsx': self._ingest_excel,
            '.xls': self._ingest_excel,
            '.parquet': self._ingest_parquet,
            '.tsv': self._ingest_tsv,
            '.txt': self._ingest_text,
        }
    
    def ingest_file(self, 
                   file_path: Union[str, Path], 
                   labels: Optional[Union[str, List[str], set]] = None,
                   resource_per_row: bool = True,
                   id_column: Optional[str] = None,
                   label_column: Optional[str] = None,
                   property_mapping: Optional[Dict[str, str]] = None,
                   **kwargs) -> List[Resource]:
        """
        Ingest a file and convert it to Resources.
        
        Args:
            file_path: Path to the file to ingest
            labels: Labels to apply to resources (can be string, list, or set)
            resource_per_row: If True, create one resource per row (for CSV/Excel)
                             If False, create one resource containing all data
            id_column: Column to use as resource ID (if None, auto-generate)
            label_column: Column containing labels for each row
            property_mapping: Dict to rename columns/properties
            **kwargs: Additional arguments passed to pandas readers
            
        Returns:
            List of Resource objects
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataIngestionError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise DataIngestionError(f"Unsupported file format: {file_extension}")
        
        # Normalize labels
        if labels is None:
            labels = set()
        elif isinstance(labels, str):
            labels = {labels}
        elif isinstance(labels, list):
            labels = set(labels)
        elif not isinstance(labels, set):
            labels = set(labels)
        
        try:
            ingestion_func = self.supported_formats[file_extension]
            return ingestion_func(
                file_path, 
                labels=labels,
                resource_per_row=resource_per_row,
                id_column=id_column,
                label_column=label_column,
                property_mapping=property_mapping,
                **kwargs
            )
        except Exception as e:
            raise DataIngestionError(f"Failed to ingest file {file_path}: {e}")
    
    def _ingest_csv(self, file_path: Path, labels: set, resource_per_row: bool, 
                   id_column: Optional[str], label_column: Optional[str],
                   property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest CSV file."""
        try:
            df = pd.read_csv(file_path, **kwargs)
            return self._dataframe_to_resources(
                df, labels, resource_per_row, id_column, label_column, property_mapping
            )
        except Exception as e:
            raise DataIngestionError(f"Failed to read CSV file: {e}")
    
    def _ingest_tsv(self, file_path: Path, labels: set, resource_per_row: bool,
                   id_column: Optional[str], label_column: Optional[str],
                   property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest TSV file."""
        try:
            kwargs.setdefault('sep', '\t')
            df = pd.read_csv(file_path, **kwargs)
            return self._dataframe_to_resources(
                df, labels, resource_per_row, id_column, label_column, property_mapping
            )
        except Exception as e:
            raise DataIngestionError(f"Failed to read TSV file: {e}")
    
    def _ingest_excel(self, file_path: Path, labels: set, resource_per_row: bool,
                     id_column: Optional[str], label_column: Optional[str],
                     property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest Excel file."""
        try:
            df = pd.read_excel(file_path, **kwargs)
            return self._dataframe_to_resources(
                df, labels, resource_per_row, id_column, label_column, property_mapping
            )
        except Exception as e:
            raise DataIngestionError(f"Failed to read Excel file: {e}")
    
    def _ingest_parquet(self, file_path: Path, labels: set, resource_per_row: bool,
                       id_column: Optional[str], label_column: Optional[str],
                       property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest Parquet file."""
        try:
            df = pd.read_parquet(file_path, **kwargs)
            return self._dataframe_to_resources(
                df, labels, resource_per_row, id_column, label_column, property_mapping
            )
        except Exception as e:
            raise DataIngestionError(f"Failed to read Parquet file: {e}")
    
    def _ingest_json(self, file_path: Path, labels: set, resource_per_row: bool,
                    id_column: Optional[str], label_column: Optional[str],
                    property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                # List of objects - each becomes a resource
                resources = []
                for item in data:
                    if isinstance(item, dict):
                        resource = self._dict_to_resource(
                            item, labels, id_column, label_column, property_mapping
                        )
                        resources.append(resource)
                return resources
            elif isinstance(data, dict):
                if resource_per_row:
                    # Single object becomes one resource
                    resource = self._dict_to_resource(
                        data, labels, id_column, label_column, property_mapping
                    )
                    return [resource]
                else:
                    # Entire dict becomes properties of one resource
                    processed_data = data.copy()
                    if property_mapping:
                        processed_data = self._apply_property_mapping(processed_data, property_mapping)
                    
                    resource_labels = labels.copy()
                    resource_id = processed_data.pop(id_column, None) if id_column else None
                    
                    if label_column and label_column in processed_data:
                        additional_labels = processed_data.pop(label_column)
                        if isinstance(additional_labels, str):
                            resource_labels.add(additional_labels)
                        elif isinstance(additional_labels, (list, set)):
                            resource_labels.update(additional_labels)
                    
                    return [Resource(
                        id=resource_id,
                        labels=resource_labels,
                        properties=processed_data
                    )]
            else:
                raise DataIngestionError("JSON data must be a dictionary or list of dictionaries")
                
        except Exception as e:
            raise DataIngestionError(f"Failed to read JSON file: {e}")
    
    def _ingest_jsonl(self, file_path: Path, labels: set, resource_per_row: bool,
                     id_column: Optional[str], label_column: Optional[str],
                     property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest JSONL (JSON Lines) file."""
        try:
            resources = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        if isinstance(data, dict):
                            resource = self._dict_to_resource(
                                data, labels, id_column, label_column, property_mapping
                            )
                            resources.append(resource)
            return resources
        except Exception as e:
            raise DataIngestionError(f"Failed to read JSONL file: {e}")
    
    def _ingest_text(self, file_path: Path, labels: set, resource_per_row: bool,
                    id_column: Optional[str], label_column: Optional[str],
                    property_mapping: Optional[Dict[str, str]], **kwargs) -> List[Resource]:
        """Ingest plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            resource_labels = labels.copy()
            resource_labels.add("TextDocument")
            
            properties = {
                "content": content,
                "filename": file_path.name,
                "file_size": len(content),
                "file_path": str(file_path)
            }
            
            if property_mapping:
                properties = self._apply_property_mapping(properties, property_mapping)
            
            return [Resource(
                labels=resource_labels,
                properties=properties
            )]
        except Exception as e:
            raise DataIngestionError(f"Failed to read text file: {e}")
    
    def _dataframe_to_resources(self, df: pd.DataFrame, labels: set, resource_per_row: bool,
                               id_column: Optional[str], label_column: Optional[str],
                               property_mapping: Optional[Dict[str, str]]) -> List[Resource]:
        """Convert pandas DataFrame to Resources."""
        if resource_per_row:
            resources = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                resource = self._dict_to_resource(
                    row_dict, labels, id_column, label_column, property_mapping
                )
                resources.append(resource)
            return resources
        else:
            # Convert entire dataframe to one resource
            data_dict = df.to_dict(orient='tight')  # Same format as in the example
            
            if property_mapping:
                data_dict = self._apply_property_mapping(data_dict, property_mapping)
            
            resource_labels = labels.copy()
            resource_labels.add("DataFrame")
            
            return [Resource(
                labels=resource_labels,
                properties=data_dict
            )]
    
    def _dict_to_resource(self, data: Dict[str, Any], labels: set,
                         id_column: Optional[str], label_column: Optional[str],
                         property_mapping: Optional[Dict[str, str]]) -> Resource:
        """Convert dictionary to Resource."""
        processed_data = data.copy()
        
        # Apply property mapping
        if property_mapping:
            processed_data = self._apply_property_mapping(processed_data, property_mapping)
        
        # Extract ID
        resource_id = processed_data.pop(id_column, None) if id_column else None
        
        # Extract labels
        resource_labels = labels.copy()
        if label_column and label_column in processed_data:
            additional_labels = processed_data.pop(label_column)
            if isinstance(additional_labels, str):
                resource_labels.add(additional_labels)
            elif isinstance(additional_labels, (list, set)):
                resource_labels.update(additional_labels)
        
        # Handle NaN values from pandas
        cleaned_properties = {}
        for key, value in processed_data.items():
            if pd.isna(value):
                cleaned_properties[key] = None
            else:
                cleaned_properties[key] = value
        
        return Resource(
            id=resource_id if resource_id is not None else str(uuid4()),
            labels=resource_labels,
            properties=cleaned_properties
        )
    
    def _apply_property_mapping(self, data: Dict[str, Any], 
                               mapping: Dict[str, str]) -> Dict[str, Any]:
        """Apply property name mapping to data."""
        mapped_data = {}
        for key, value in data.items():
            new_key = mapping.get(key, key)
            mapped_data[new_key] = value
        return mapped_data


def create_resource_from_dataframe(df: pd.DataFrame, 
                                  labels: Optional[Union[str, List[str], set]] = None,
                                  orient: str = 'tight',
                                  **kwargs) -> Resource:
    """
    Create a single Resource from a pandas DataFrame.
    
    Args:
        df: pandas DataFrame
        labels: Labels to apply to the resource
        orient: Orientation for DataFrame.to_dict() method
        **kwargs: Additional properties to add to the resource
        
    Returns:
        Resource object containing the DataFrame data
    """
    # Normalize labels
    if labels is None:
        resource_labels = {"DataFrame"}
    elif isinstance(labels, str):
        resource_labels = {labels}
    elif isinstance(labels, list):
        resource_labels = set(labels)
    elif isinstance(labels, set):
        resource_labels = labels.copy()
    else:
        resource_labels = set(labels)
    
    # Convert DataFrame to dict
    df_dict = df.to_dict(orient=orient)
    
    # Add any additional properties
    properties = {**df_dict, **kwargs}
    
    return Resource(
        labels=resource_labels,
        properties=properties
    )


def create_resources_from_dataframe_rows(df: pd.DataFrame,
                                        labels: Optional[Union[str, List[str], set]] = None,
                                        id_column: Optional[str] = None,
                                        label_column: Optional[str] = None,
                                        **kwargs) -> List[Resource]:
    """
    Create Resources from DataFrame rows (one resource per row).
    
    Args:
        df: pandas DataFrame
        labels: Base labels to apply to all resources
        id_column: Column to use as resource ID
        label_column: Column containing additional labels
        **kwargs: Additional properties to add to all resources
        
    Returns:
        List of Resource objects (one per row)
    """
    # Normalize labels
    if labels is None:
        base_labels = set()
    elif isinstance(labels, str):
        base_labels = {labels}
    elif isinstance(labels, list):
        base_labels = set(labels)
    elif isinstance(labels, set):
        base_labels = labels.copy()
    else:
        base_labels = set(labels)
    
    resources = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        
        # Extract ID
        resource_id = row_dict.pop(id_column, None) if id_column else None
        
        # Extract labels
        resource_labels = base_labels.copy()
        if label_column and label_column in row_dict:
            additional_labels = row_dict.pop(label_column)
            if isinstance(additional_labels, str):
                resource_labels.add(additional_labels)
            elif isinstance(additional_labels, (list, set)):
                resource_labels.update(additional_labels)
        
        # Handle NaN values
        cleaned_properties = {}
        for key, value in row_dict.items():
            if pd.isna(value):
                cleaned_properties[key] = None
            else:
                cleaned_properties[key] = value
        
        # Add additional properties
        cleaned_properties.update(kwargs)
        
        resource = Resource(
            id=resource_id if resource_id is not None else str(uuid4()),
            labels=resource_labels,
            properties=cleaned_properties
        )
        resources.append(resource)
    
    return resources
