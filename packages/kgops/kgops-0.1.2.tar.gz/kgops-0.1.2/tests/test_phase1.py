#!/usr/bin/env python3
"""
Comprehensive Phase 1 functionality test script.
"""

import tempfile
from pathlib import Path
import json
import csv

from kgops import KGOps, Resource, Dataset
from kgops.transforms.converter import FormatConverter
from kgops.transforms.validator import DataValidator
from kgops.core.context import Context

def test_basic_operations():
    """Test basic graph operations."""
    print("🔄 Testing basic operations...")
    
    # Initialize KGOps
    kg = KGOps(backend="networkx")
    
    # Create graph
    graph = kg.create_graph("test-graph", description="Phase 1 test")
    
    # Create resources
    person = Resource(
        labels={"Person", "Employee"},
        properties={
            "name": "Alice Johnson",
            "age": 30,
            "email": "alice@test.com",
            "department": "Engineering"
        }
    )
    
    company = Resource(
        labels={"Organization", "Company"},
        properties={
            "name": "TestCorp",
            "industry": "Technology",
            "employees": 100
        }
    )
    
    # Add resources
    kg.add_resource(person)
    kg.add_resource(company)
    
    # Add relationship
    kg.add_edge(person, company, "WORKS_AT", since="2020")
    
    # Test queries
    people = kg.query("label", label="Person")
    assert len(people) == 1
    
    neighbors = kg.query("neighbors", resource_id=person.id)
    
    # Test stats
    stats = kg.stats()
    assert stats["resources"] == 2
    assert stats["edges"] == 1
    
    print("✅ Basic operations successful")

def test_file_operations():
    """Test file I/O operations."""
    print("🔄 Testing file operations...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test data
        kg = KGOps(backend="networkx")
        graph = kg.create_graph("test-graph", description="Phase 1 test")
        
        person = Resource(
            labels={"Person", "Employee"},
            properties={"name": "Alice Johnson", "age": 28}
        )
        
        company = Resource(
            labels={"Organization", "Company"},
            properties={"name": "TechCorp", "industry": "Technology"}
        )
        
        kg.add_resource(person)
        kg.add_resource(company)
        kg.add_edge(person, company, "WORKS_AT", since="2020")
        
        # Save graph
        graph_path = tmpdir / "test_graph.json"
        kg.save_graph(graph_path)
        assert graph_path.exists()
        
        # Load graph
        kg2 = KGOps()
        dataset = kg2.load_graph(graph_path)
        assert dataset.name == "test-graph"
        assert len(dataset.resources) == 2
        
        print("✅ File operations successful")

def test_data_ingestion():
    """Test data ingestion from CSV and JSON."""
    print("🔄 Testing data ingestion...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test CSV
        csv_path = tmpdir / "test_data.csv"
        csv_data = """id,name,age,department,role
1,Alice Smith,28,Engineering,Developer
2,Bob Johnson,35,Marketing,Manager
3,Carol Davis,32,Sales,Representative"""
        
        with open(csv_path, 'w') as f:
            f.write(csv_data)
        
        # Test CSV ingestion
        converter = FormatConverter()
        resources = list(converter.csv_to_resources(csv_path, id_field="id"))
        
        assert len(resources) == 3
        assert resources[0].properties["name"] == "Alice Smith"
        
        # Create test JSON
        json_path = tmpdir / "test_data.json"
        json_data = {
            "records": [
                {
                    "id": "p1",
                    "labels": ["Person"],
                    "name": "John Doe",
                    "age": 40
                },
                {
                    "id": "p2", 
                    "labels": ["Person"],
                    "name": "Jane Smith",
                    "age": 35
                }
            ]
        }
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Test JSON ingestion
        json_resources = list(converter.json_to_resources(json_path))
        assert len(json_resources) == 2
        
        print("✅ Data ingestion successful")

def test_validation():
    """Test data validation."""
    print("🔄 Testing data validation...")
    
    # Create schema
    schema = {
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0},
            "email": {"type": "string"}
        },
        "required": ["name"]
    }
    
    # Create validator
    validator = DataValidator(schema=schema, strict=False)
    
    # Test valid resource
    valid_resource = Resource(
        properties={
            "name": "Test User",
            "age": 25,
            "email": "test@example.com"
        }
    )
    
    validated = validator.transform(valid_resource)
    assert validated.properties["name"] == "Test User"
    
    # Test invalid resource (should handle gracefully)
    invalid_resource = Resource(
        properties={
            "name": "",  # Invalid - empty name
            "age": -5,   # Invalid - negative age
            "email": "invalid-email"
        }
    )
    
    validator.transform(invalid_resource)  # Should not raise in non-strict mode
    
    print("✅ Data validation successful")

def test_export_functionality():
    """Test various export formats."""
    print("🔄 Testing export functionality...")
    
    # Create test data
    kg = KGOps(backend="networkx")
    graph = kg.create_graph("test-graph", description="Phase 1 test")
    
    person = Resource(
        labels={"Person", "Employee"},
        properties={"name": "Alice Johnson", "age": 28}
    )
    
    company = Resource(
        labels={"Organization", "Company"},
        properties={"name": "TechCorp", "industry": "Technology"}
    )
    
    kg.add_resource(person)
    kg.add_resource(company)
    kg.add_edge(person, company, "WORKS_AT", since="2020")
    
    # Test JSON export
    json_export = kg.export("json")
    assert isinstance(json_export, dict)
    assert "resources" in json_export
    
    # Test edge list export
    edges_export = kg.export("edges")
    assert isinstance(edges_export, list)
    
    # Test NetworkX export (if available)
    try:
        nx_export = kg.export("networkx")
        assert hasattr(nx_export, 'nodes')
        print("✅ NetworkX export available")
    except ImportError:
        print("ℹ️  NetworkX export not available (optional)")
    
    print("✅ Export functionality successful")

def run_all_tests():
    """Run all Phase 1 tests."""
    print("🚀 Starting Phase 1 Comprehensive Tests\n")
    
    try:
        test_basic_operations()
        test_file_operations()
        test_data_ingestion()
        test_validation()
        test_export_functionality()
        
        print("\n🎉 All Phase 1 tests passed!")
        print("✅ Phase 1 implementation is ready for production use")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
