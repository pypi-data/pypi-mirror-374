"""
Storage backends for kgforge knowledge graphs.
"""

from kgforge.storage.base import BaseStorage
from kgforge.storage.memory import MemoryStorage

__all__ = ["BaseStorage", "MemoryStorage"]
