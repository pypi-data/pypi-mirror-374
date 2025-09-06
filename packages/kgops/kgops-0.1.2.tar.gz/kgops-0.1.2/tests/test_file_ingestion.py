"""
Tests for the new file ingestion functionality.
"""

import pytest
import pandas as pd
import json
import tempfile
import os
from pathlib import Path

from kgops import KGOps, Resource
from kgops.core.exceptions import KGOpsError
from kgops.utils.data_ingestion import FileIngester, create_resource_from_dataframe, create_resources_from_dataframe_rows, DataIngestionError


class TestFileIngestion:
    """Test file ingestion capabilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.kg = KGOps(backend="networkx")
        self.graph = self.kg.create_graph("test-ingestion-graph")
        
    def test_csv_ingestion_per_row(self):
        """Test CSV ingestion with one resource per row."""
        # Create temporary CSV file
        csv_data = """name,email,department
Alice,alice@example.com,Engineering
Bob,bob@example.com,Sales
Carol,carol@example.com,Marketing"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            resources = self.kg.ingest_csv(
                csv_path,
                labels={"Employee"},
                resource_per_row=True,
                add_to_graph=True
            )
            
            assert len(resources) == 3
            assert all(r.labels == {"Employee"} for r in resources)
            assert resources[0].get_property("name") == "Alice"
            assert resources[1].get_property("email") == "bob@example.com"
            assert resources[2].get_property("department") == "Marketing"
            
            # Check resources were added to graph
            stats = self.kg.stats()
            assert stats['resources'] >= 3
            
        finally:
            os.unlink(csv_path)
    
    def test_csv_ingestion_single_resource(self):
        """Test CSV ingestion as single resource."""
        csv_data = """name,email,department
Alice,alice@example.com,Engineering
Bob,bob@example.com,Sales"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            resources = self.kg.ingest_csv(
                csv_path,
                labels={"EmployeeDataset"},
                resource_per_row=False,
                add_to_graph=False
            )
            
            assert len(resources) == 1
            assert "DataFrame" in resources[0].labels
            assert "EmployeeDataset" in resources[0].labels
            
            # Should contain data structure
            properties = resources[0].properties
            assert "data" in properties
            assert "columns" in properties
            
        finally:
            os.unlink(csv_path)
    
    def test_json_ingestion(self):
        """Test JSON file ingestion."""
        json_data = [
            {"id": "1", "name": "Project Alpha", "status": "Active"},
            {"id": "2", "name": "Project Beta", "status": "Planning"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            json_path = f.name
        
        try:
            resources = self.kg.ingest_json(
                json_path,
                labels={"Project"},
                resource_per_row=True,
                id_column="id",
                add_to_graph=False
            )
            
            assert len(resources) == 2
            assert all("Project" in r.labels for r in resources)
            assert resources[0].id == "1"
            assert resources[1].id == "2"
            assert resources[0].get_property("name") == "Project Alpha"
            
        finally:
            os.unlink(json_path)
    
    def test_dataframe_ingestion_per_row(self):
        """Test DataFrame ingestion with one resource per row."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Carol'],
            'email': ['alice@example.com', 'bob@example.com', 'carol@example.com'],
            'active': [True, True, False]
        })
        
        resources = self.kg.ingest_dataframe(
            df,
            labels={"Person"},
            resource_per_row=True,
            add_to_graph=False
        )
        
        assert len(resources) == 3
        assert all("Person" in r.labels for r in resources)
        assert resources[0].get_property("name") == "Alice"
        assert resources[2].get_property("active") is False
    
    def test_dataframe_ingestion_single_resource(self):
        """Test DataFrame ingestion as single resource."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'score': [95, 87]
        })
        
        resources = self.kg.ingest_dataframe(
            df,
            labels={"ScoreData"},
            resource_per_row=False,
            add_to_graph=False
        )
        
        assert len(resources) == 1
        assert "ScoreData" in resources[0].labels
        # DataFrame label is only added by the FileIngester, not by ingest_dataframe directly
    
    def test_property_mapping(self):
        """Test property mapping during ingestion."""
        csv_data = """emp_name,emp_email
Alice,alice@example.com
Bob,bob@example.com"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            resources = self.kg.ingest_csv(
                csv_path,
                labels={"Employee"},
                resource_per_row=True,
                property_mapping={"emp_name": "name", "emp_email": "email"},
                add_to_graph=False
            )
            
            assert len(resources) == 2
            assert resources[0].get_property("name") == "Alice"
            assert resources[0].get_property("email") == "alice@example.com"
            assert resources[0].get_property("emp_name") is None  # Original name should be gone
            
        finally:
            os.unlink(csv_path)
    
    def test_label_column(self):
        """Test using a column for additional labels."""
        csv_data = """name,department,role
Alice,Engineering,Engineer
Bob,Sales,Manager"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name
        
        try:
            resources = self.kg.ingest_csv(
                csv_path,
                labels={"Employee"},
                resource_per_row=True,
                label_column="department",
                add_to_graph=False
            )
            
            assert len(resources) == 2
            assert "Employee" in resources[0].labels
            assert "Engineering" in resources[0].labels
            assert "Sales" in resources[1].labels
            
        finally:
            os.unlink(csv_path)
    
    def test_file_ingester_unsupported_format(self):
        """Test error handling for unsupported file formats."""
        ingester = FileIngester()
        
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"some data")
            invalid_path = f.name
        
        try:
            with pytest.raises(DataIngestionError) as exc_info:
                ingester.ingest_file(invalid_path, labels={"Test"})
            assert "Unsupported file format" in str(exc_info.value)
            
        finally:
            os.unlink(invalid_path)
    
    def test_file_not_found(self):
        """Test error handling for non-existent files."""
        with pytest.raises(KGOpsError) as exc_info:
            self.kg.ingest_csv("nonexistent_file.csv")
        assert "File not found" in str(exc_info.value)
    
    def test_utility_functions(self):
        """Test utility functions directly."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'score': [95, 87]
        })
        
        # Test create_resource_from_dataframe
        resource = create_resource_from_dataframe(df, labels={"TestData"})
        assert "TestData" in resource.labels
        # DataFrame label is only added by FileIngester, not this utility function
        assert "data" in resource.properties
        
        # Test create_resources_from_dataframe_rows
        resources = create_resources_from_dataframe_rows(df, labels={"Person"})
        assert len(resources) == 2
        assert all("Person" in r.labels for r in resources)
        assert resources[0].get_property("name") == "Alice"
        assert resources[1].get_property("score") == 87
    
    def test_nan_handling(self):
        """Test handling of NaN values from pandas."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'optional_field': ['value1', None]
        })
        
        resources = self.kg.ingest_dataframe(
            df,
            labels={"Person"},
            resource_per_row=True,
            add_to_graph=False
        )
        
        assert len(resources) == 2
        assert resources[0].get_property("optional_field") == "value1"
        assert resources[1].get_property("optional_field") is None
    
    def test_integration_with_existing_workflow(self):
        """Test that new methods work with existing kgops workflow."""
        # Create some data
        df = pd.DataFrame({
            'email': ['alice@example.com', 'bob@example.com'],
            'department': ['Engineering', 'Sales']
        })
        
        # Use original approach
        df_dict = df.to_dict(orient='tight')
        manual_resource = Resource(
            labels={'ManualData'},
            properties=df_dict
        )
        self.kg.add_resource(manual_resource)
        
        # Use new ingestion approach
        ingested_resources = self.kg.ingest_dataframe(
            df,
            labels={"IngestedData"},
            resource_per_row=True,
            add_to_graph=True
        )
        
        # Create relationships
        for resource in ingested_resources:
            self.kg.add_edge(manual_resource, resource, "CONTAINS")
        
        # Verify everything works
        stats = self.kg.stats()
        assert stats['resources'] >= 3  # 1 manual + 2 ingested
        assert stats['edges'] >= 2  # 2 CONTAINS relationships
        
        neighbors = self.kg.query("neighbors", resource_id=manual_resource.id)
        assert len(neighbors) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
