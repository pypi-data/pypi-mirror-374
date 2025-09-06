"""
General utility functions for kgops.
"""

from typing import Any, Dict, List, Optional, Union, Set
import re
import hashlib
from datetime import datetime, timezone
import json


def generate_id(prefix: str = "", suffix: str = "") -> str:
    """Generate a unique identifier."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}{timestamp}{suffix}"


def normalize_string(text: str, lowercase: bool = True, 
                    remove_special: bool = False) -> str:
    """Normalize string for comparison and matching."""
    if not isinstance(text, str):
        return str(text)
    
    # Strip whitespace
    text = text.strip()
    
    # Convert to lowercase
    if lowercase:
        text = text.lower()
    
    # Remove special characters
    if remove_special:
        text = re.sub(r'[^\w\s]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text


def compute_hash(data: Union[str, Dict[str, Any], List[Any]], 
                 algorithm: str = "md5") -> str:
    """Compute hash of data for deduplication."""
    if isinstance(data, (dict, list)):
        # Sort keys for consistent hashing
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    else:
        json_str = str(data)
    
    if algorithm.lower() == "md5":
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()
    elif algorithm.lower() == "sha256":
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def extract_entities_simple(text: str, patterns: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """Simple regex-based entity extraction."""
    if not patterns:
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
    
    entities = []
    
    for entity_type, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            entities.append({
                "text": match,
                "type": entity_type,
                "start": text.find(match),
                "end": text.find(match) + len(match)
            })
    
    return entities


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math
    
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same length")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def jaccard_similarity(set1: Set[Any], set2: Set[Any]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, with later dicts taking precedence."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))
