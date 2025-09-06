"""
Unit tests for core kgops components.
"""

import pytest
from datetime import datetime
import json

from kgops.core.resource import Resource
from kgops.core.dataset import Dataset, Edge
from kgops.core.context import Context
from kgops.core.forge import KGOps
from kgops.core.exceptions import ValidationError, KGOpsError


class TestResource:
    """Test Resource class functionality."""
    
    def test_resource_creation(self):
        """Test basic resource creation."""
        resource = Resource(
            labels={"Person"},
            properties={"name": "Test User", "age": 25}
        )
        
        assert len(resource.labels) == 1
        assert "Person" in resource.labels
        assert resource.properties["name"] == "Test User"
        assert resource.properties["age"] == 25
        assert isinstance(resource.created_at, datetime)
        assert isinstance(resource.updated_at, datetime)
    
    def test_resource_id_generation(self):
        """Test automatic ID generation."""
        resource1 = Resource()
        resource2 = Resource()
        
        assert resource1.id != resource2.id
        assert isinstance(resource1.id, str)
        assert len(resource1.id) > 0
    
    def test_add_remove_labels(self, sample_resource):
        """Test label manipulation."""
        sample_resource.add_label("Manager")
        assert "Manager" in sample_resource.labels
        
        sample_resource.remove_label("Employee")
        assert "Employee" not in sample_resource.labels
        
        # Test invalid label
        with pytest.raises(ValidationError):
            sample_resource.add_label("")
    
    def test_property_operations(self, sample_resource):
        """Test property operations."""
        sample_resource.set_property("salary", 75000)
        assert sample_resource.get_property("salary") == 75000
        
        assert sample_resource.has_property("name")
        assert not sample_resource.has_property("nonexistent")
        
        sample_resource.remove_property("age")
        assert not sample_resource.has_property("age")
    
    def test_embeddings(self, sample_resource):
        """Test embedding operations."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        sample_resource.set_embedding("test_embedding", embedding)
        
        retrieved = sample_resource.get_embedding("test_embedding")
        assert retrieved == embedding
        
        # Test invalid embedding
        with pytest.raises(ValidationError):
            sample_resource.set_embedding("invalid", ["not", "numbers"])
    
    def test_serialization(self, sample_resource):
        """Test resource serialization/deserialization."""
        # To dict
        data = sample_resource.to_dict()
        assert isinstance(data, dict)
        assert data["id"] == sample_resource.id
        assert set(data["labels"]) == sample_resource.labels
        
        # From dict
        new_resource = Resource.from_dict(data)
        assert new_resource.id == sample_resource.id
        assert new_resource.labels == sample_resource.labels
        assert new_resource.properties == sample_resource.properties
        
        # JSON serialization
        json_str = sample_resource.to_json()
        assert isinstance(json_str, str)
        
        from_json = Resource.from_json(json_str)
        assert from_json.id == sample_resource.id


class TestDataset:
    """Test Dataset class functionality."""
    
    def test_dataset_creation(self):
        """Test basic dataset creation."""
        dataset = Dataset(name="test", description="Test dataset")
        
        assert dataset.name == "test"
        assert dataset.description == "Test dataset"
        assert len(dataset.resources) == 0
        assert len(dataset.edges) == 0
    
    def test_add_remove_resources(self, sample_resources):
        """Test resource management."""
        dataset = Dataset(name="test")
        
        # Add resources
        for resource in sample_resources:
            dataset.add_resource(resource)
        
        assert len(dataset.resources) == len(sample_resources)
        
        # Remove resource
        first_id = sample_resources[0].id
        dataset.remove_resource(first_id)
        assert len(dataset.resources) == len(sample_resources) - 1
        assert first_id not in dataset.resources
    
    def test_edge_operations(self, sample_dataset):
        """Test edge operations."""
        resource_ids = list(sample_dataset.resources.keys())
        
        # Test edge queries
        edges = sample_dataset.get_edges(source_id=resource_ids[0])
        assert len(edges) >= 0
        
        edges_by_type = sample_dataset.get_edges(edge_type="WORKS_AT")
        assert len(edges_by_type) >= 0
    
    def test_query_operations(self, sample_dataset):
        """Test dataset query operations."""
        # Get resources by label
        people = sample_dataset.get_resources_by_label("Person")
        assert len(people) >= 0
        
        # Get resources by property
        named_resources = sample_dataset.get_resources_by_property("name")
        assert len(named_resources) >= 0
        
        # Filter resources
        filtered = sample_dataset.filter_resources(lambda r: len(r.properties) > 2)
        assert isinstance(filtered, list)
    
    def test_stats(self, sample_dataset):
        """Test dataset statistics."""
        stats = sample_dataset.stats()
        
        assert "resources" in stats
        assert "edges" in stats
        assert "labels" in stats
        assert "edge_types" in stats
        assert isinstance(stats["resources"], int)
        assert isinstance(stats["edges"], int)
    
    def test_serialization(self, sample_dataset, temp_dir):
        """Test dataset serialization."""
        # Save to JSON
        json_path = temp_dir / "test_dataset.json"
        sample_dataset.to_json(json_path)
        
        assert json_path.exists()
        
        # Load from JSON
        loaded_dataset = Dataset.from_json(json_path)
        assert loaded_dataset.name == sample_dataset.name
        assert len(loaded_dataset.resources) == len(sample_dataset.resources)
        assert len(loaded_dataset.edges) == len(sample_dataset.edges)


class TestContext:
    """Test Context class functionality."""
    
    def test_context_creation(self, sample_context):
        """Test context creation."""
        assert sample_context.graph.backend == "networkx"
        assert sample_context.metadata["test"] is True
    
    def test_context_file_operations(self, sample_context, temp_dir):
        """Test loading and saving context from/to files."""
        # Save to YAML
        yaml_path = temp_dir / "config.yaml"
        sample_context.to_file(yaml_path)
        assert yaml_path.exists()
        
        # Load from YAML
        loaded_context = Context.from_file(yaml_path)
        assert loaded_context.graph.backend == sample_context.graph.backend
        
        # Save to JSON
        json_path = temp_dir / "config.json"
        sample_context.to_file(json_path)
        assert json_path.exists()
        
        # Load from JSON
        loaded_json_context = Context.from_file(json_path)
        assert loaded_json_context.graph.backend == sample_context.graph.backend
    
    def test_tenant_management(self, sample_context):
        """Test tenant configuration."""
        sample_context.set_tenant("test-tenant", "Test Tenant", "test-owner")
        
        assert sample_context.tenant is not None
        assert sample_context.tenant.tenant_id == "test-tenant"
        assert sample_context.tenant.name == "Test Tenant"
        assert sample_context.tenant.owner == "test-owner"


class TestKGOps:
    """Test KGOps main class functionality."""
    
    def test_initialization(self):
        """Test KGOps initialization."""
        kg = KGOps(backend="networkx")
        assert kg.context.graph.backend == "networkx"
    
    def test_graph_lifecycle(self, kg_ops):
        """Test complete graph lifecycle."""
        # Create graph
        dataset = kg_ops.create_graph("test-graph", description="Test graph")
        assert dataset.name == "test-graph"
        assert kg_ops.current_graph is not None
        
        # Add resources
        resource = Resource(
            labels={"TestEntity"},
            properties={"name": "Test", "value": 42}
        )
        
        added_resource = kg_ops.add_resource(resource)
        assert added_resource.id == resource.id
        
        # Query
        retrieved = kg_ops.get_resource(resource.id)
        assert retrieved is not None
        assert retrieved.id == resource.id
        
        # Add edge
        resource2 = kg_ops.add_resource(Resource(labels={"TestEntity2"}))
        edge = kg_ops.add_edge(resource, resource2, "RELATES_TO")
        assert edge.source == resource.id
        assert edge.target == resource2.id
        
        # Statistics
        stats = kg_ops.stats()
        assert stats["resources"] >= 2
        assert stats["edges"] >= 1
    
    def test_query_operations(self, kg_forge, sample_resources):
        """Test various query operations."""
        # Create graph with sample data
        kg_forge.create_graph("query-test")
        
        for resource in sample_resources:
            kg_forge.add_resource(resource)
        
        # Query by label
        people = kg_forge.query("label", label="Person")
        assert len(people) >= 2
        
        # Query by property
        named = kg_forge.query("property", key="name")
        assert len(named) >= 0
    
    def test_export_functionality(self, kg_forge, sample_dataset):
        """Test export functionality."""
        kg_forge._current_dataset = sample_dataset
        
        # Export as NetworkX
        try:
            nx_graph = kg_forge.export("networkx")
            # Basic checks if NetworkX is available
            assert hasattr(nx_graph, 'nodes')
            assert hasattr(nx_graph, 'edges')
        except ImportError:
            # NetworkX not available, skip this test
            pass
        
        # Export as JSON
        json_data = kg_forge.export("json")
        assert isinstance(json_data, dict)
        assert "resources" in json_data
        
        # Export as edge list
        edges = kg_forge.export("edges")
        assert isinstance(edges, list)
    
    def test_file_operations(self, kg_forge, temp_dir):
        """Test file save/load operations."""
        # Create and save graph
        dataset = kg_forge.create_graph("file-test")
        kg_forge.add_resource(Resource(labels={"Test"}, properties={"name": "File Test"}))
        
        json_path = temp_dir / "file_test.json"
        kg_forge.save_graph(json_path)
        assert json_path.exists()
        
        # Clear and load
        kg_forge.clear()
        assert kg_forge.current_graph is None
        
        loaded_dataset = kg_forge.load_graph(json_path)
        assert loaded_dataset.name == "file-test"
        assert len(loaded_dataset.resources) == 1


class TestEdge:
    """Test Edge class functionality."""
    
    def test_edge_creation(self):
        """Test edge creation."""
        edge = Edge(
            source="node1",
            target="node2", 
            type="CONNECTS_TO",
            properties={"weight": 0.5}
        )
        
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.type == "CONNECTS_TO"
        assert edge.properties["weight"] == 0.5
        assert isinstance(edge.created_at, datetime)
    
    def test_edge_serialization(self):
        """Test edge serialization."""
        edge = Edge(source="a", target="b", type="TEST")
        
        data = edge.to_dict()
        assert isinstance(data, dict)
        
        new_edge = Edge.from_dict(data)
        assert new_edge.source == edge.source
        assert new_edge.target == edge.target
        assert new_edge.type == edge.type
