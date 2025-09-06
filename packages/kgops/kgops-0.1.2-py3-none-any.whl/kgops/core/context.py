"""
Context Management for kgops operations

[
GraphConfig,
TenantConfig,
Context[ from_file, to_file , update_graph_config , set_tenant_]
]
"""

from typing import Optional, Dict, Any, Union
from pathlib import Path
import yaml
import json
from pydantic import BaseModel, Field, ConfigDict
from kgops.core.exceptions import ConfigurationError

class GraphConfig(BaseModel):
    """
    Configuration for the graph backend
    """
    backend : str = Field(default='networkx', description="Graph backend type (e.g., networkx, neo4j)")
    connection : Optional[Dict[str, Any]] = Field(default=None, description="Connection details for the graph backend")
    options : Optional[Dict[str, Any]] = Field(default_factory=dict, description="Backend options")

class TenantConfig(BaseModel):
    """
    Configuration for multi-tenancy
    """
    tenant_id : str = Field(description='unique identifier for tenants')
    name : str = Field(description='name of the tenant')
    owner : Optional[str] = Field(default=None, description='Tenant Owner')
    settings : Optional[Dict[str, Any]] = Field(default_factory=dict, description='Tenant-specific settings')

class Context(BaseModel):
    """
    Context for kgops operations containing configuration and state information.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    graph : GraphConfig = Field(default_factory=GraphConfig)
    tenant : Optional[TenantConfig] = Field(default=None)
    version : str = Field(default='0.1.0', description='Context version')
    metadata: Dict[str, Any] = Field(default_factory=dict, description='Additional metadata')

    @classmethod
    def from_file(cls, path : Union[str, Path]) -> "Context":
        """
        Load context from a configuration file.
        """
        path = Path(path)

        if not path.exists():
            raise ConfigurationError(f"Configuration file {path} does not exist.")
        
        try:
            if(path.suffix.lower() in ['.yaml', '.yml']):
                with open(path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            elif(path.suffix.lower() == '.json'):
                with open(path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                raise ConfigurationError(f"Unsupported configuration file format: {path.suffix}")

            return cls(**config_data)

        except(yaml.YAMLError, json.JSONDecodeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration file at path: {path}: {e}")
        
    def to_file(self, path : Union[str, Path]) -> None:
        """
        save context to a configuration file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            config_data = self.model_dump()

            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config_data, f, default_flow_style=False, indent=2)
            elif path.suffix.lower() == '.json':
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2)

            else:
                raise ConfigurationError(f"Unsupported configuration file format: {path.suffix}")

        except (yaml.YAMLError, json.JSONEncodeError) as e:
            raise ConfigurationError(f"Failed to save configuration file at path: {path}: {e}")
        

    def update_graph_config(self, **kwargs: Any) -> None:
        """
        Update the graph configuration with new values.
        """
        for key,value in kwargs.items():
            if hasattr(self.graph, key):
                setattr(self.graph, key, value)
            else:
                if not self.graph.options:
                    self.graph.options = {}
                    self.graph.options[key] = value
    

    def set_tenant(
            self,
            tenant_id: str,
            name: str,
            owner : Optional[str] = None,
            **settings: Any
    ) -> None:
        """
        Set the tenant configuration.
        """
        self.tenant = TenantConfig(
            tenant_id=tenant_id,
            name=name,
            owner=owner,
            settings=settings
        )


