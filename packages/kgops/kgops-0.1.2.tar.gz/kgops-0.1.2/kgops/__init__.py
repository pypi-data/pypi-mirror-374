"""
kgops - End-to-End Knowledge Graph Operations for RAG & Data Integration

A Python framework for building, maintaining, and operating Knowledge Graphs
with LLM-assisted extraction and multi-tenant support.
"""

from kgops.core.forge import KGOps
from kgops.core.resource import Resource
from kgops.core.dataset import Dataset
from kgops.core.exceptions import (
    KGOpsError,
    ValidationError,
    StorageError,
    ConnectorError,
    TransformError,
)
from kgops.utils.data_ingestion import (
    FileIngester,
    create_resource_from_dataframe,
    create_resources_from_dataframe_rows,
    DataIngestionError,
)

__version__ = "0.1.0"
__author__ = "Soham Chaudhari"
__email__ = "sohamchaudhari2004@gmail.com"

__all__ = [
    "KGOps",
    "Resource",
    "Dataset", 
    "KGOpsError",
    "ValidationError",
    "StorageError",
    "ConnectorError",
    "TransformError",
    "FileIngester",
    "create_resource_from_dataframe",
    "create_resources_from_dataframe_rows",
    "DataIngestionError",
]

# Configure logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
