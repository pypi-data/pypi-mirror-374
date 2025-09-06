"""
Storage backends for kgops knowledge graphs.
"""

from kgops.storage.base import BaseStorage
from kgops.storage.memory import MemoryStorage

__all__ = ["BaseStorage", "MemoryStorage"]
