"""
Pytest configuration and fixtures for kgops tests.
"""

import pytest
from pathlib import Path
import tempfile
import json

from kgops import KGOps, Resource, Dataset
from kgops.core.context import Context


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_resource():
    """Create a sample resource for testing."""
    return Resource(
        labels={"Person", "Employee"},
        properties={
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com",
            "department": "Engineering"
        }
    )


@pytest.fixture
def sample_resources():
    """Create multiple sample resources."""
    resources = []
    
    # Person 1
    resources.append(Resource(
        labels={"Person"},
        properties={
            "name": "Alice Smith",
            "age": 28,
            "role": "Data Scientist"
        }
    ))
    
    # Person 2
    resources.append(Resource(
        labels={"Person"},
        properties={
            "name": "Bob Johnson",
            "age": 35,
            "role": "Software Engineer"
        }
    ))
    
    # Company
    resources.append(Resource(
        labels={"Organization", "Company"},
        properties={
            "name": "TechCorp",
            "industry": "Technology",
            "founded": 2010
        }
    ))
    
    return resources


@pytest.fixture
def sample_dataset(sample_resources):
    """Create a sample dataset with resources and edges."""
    dataset = Dataset(
        name="test-dataset",
        description="Test dataset for unit tests"
    )
    
    # Add resources
    for resource in sample_resources:
        dataset.add_resource(resource)
    
    # Add edges (assuming first two are people, third is company)
    if len(sample_resources) >= 3:
        dataset.add_edge(
            sample_resources[0].id,
            sample_resources[2].id,
            "WORKS_AT"
        )
        dataset.add_edge(
            sample_resources[1].id,
            sample_resources[2].id,
            "WORKS_AT"
        )
    
    return dataset


@pytest.fixture
def kg_ops():
    """Create a KGOps instance for testing."""
    return KGOps(backend="networkx")


@pytest.fixture
def sample_context():
    """Create a sample context for testing."""
    return Context(
        graph={
            "backend": "networkx",
            "options": {}
        },
        metadata={
            "test": True,
            "created_by": "pytest"
        }
    )


@pytest.fixture
def sample_csv_data(temp_dir):
    """Create sample CSV data file."""
    csv_path = temp_dir / "sample_data.csv"
    
    csv_content = """id,name,age,department,email
1,Alice Johnson,28,Engineering,alice@example.com
2,Bob Smith,35,Marketing,bob@example.com
3,Carol Davis,32,Sales,carol@example.com"""
    
    with open(csv_path, 'w') as f:
        f.write(csv_content)
    
    return csv_path


@pytest.fixture
def sample_json_data(temp_dir):
    """Create sample JSON data file."""
    json_path = temp_dir / "sample_data.json"
    
    json_data = {
        "records": [
            {
                "id": "1",
                "labels": ["Person", "Employee"],
                "name": "Alice Johnson",
                "age": 28,
                "department": "Engineering"
            },
            {
                "id": "2", 
                "labels": ["Person", "Employee"],
                "name": "Bob Smith",
                "age": 35,
                "department": "Marketing"
            }
        ]
    }
    
    with open(json_path, 'w') as f:
        json.dump(json_data, f)
    
    return json_path


@pytest.fixture
def sample_schema():
    """Create a sample validation schema."""
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
            "department": {"type": "string"}
        },
        "required": ["name"]
    }
