"""
kgforge - End-to-End Knowledge Graph Builder for RAG & Sharing

A Python framework for building, maintaining, and sharing Knowledge Graphs
with LLM-assisted extraction and multi-tenant support.
"""

from kgforge.core.forge import KGForge
from kgforge.core.resource import Resource
from kgforge.core.dataset import Dataset
from kgforge.core.exceptions import (
    KGForgeError,
    ValidationError,
    StorageError,
    ConnectorError,
    TransformError,
)

__version__ = "0.1.0"
__author__ = "KGForge Team"
__email__ = "info@kgforge.dev"

__all__ = [
    "KGForge",
    "Resource",
    "Dataset", 
    "KGForgeError",
    "ValidationError",
    "StorageError",
    "ConnectorError",
    "TransformError",
]

# Configure logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
