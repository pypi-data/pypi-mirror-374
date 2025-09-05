# KGForge — End-to-End Knowledge Graph Builder

A Python framework for building, maintaining, and sharing knowledge graphs, with a local in-memory backend and CLI/Python API. Features like LLM-assisted extraction and multi-tenant support are planned for future releases.

## Features

- Local NetworkX backend (in-memory)
- CLI and Python API
- Resource management (create, query, update)
- JSON import/export
- Query system for traversal and filtering
- Typed, tested, production-ready code

## Planned Features

- Neo4j integration
- LLM extraction
- Embeddings
- KG Store
- Multi-tenancy

## Quick Start

### Installation

```bash
pip install kgforge
```

### Initialize a project

```bash
kgforge init
```

### Basic Python usage

```python
from kgforge import KGForge, Resource

# Initialize
kg = KGForge(backend="networkx")

# Create graph
graph = kg.create_graph("my-knowledge-graph")

# Add entities
person = Resource(
    labels={"Person"},
    properties={"name": "Alice Johnson", "role": "Data Scientist"}
)

company = Resource(
    labels={"Organization"},
    properties={"name": "TechCorp", "industry": "AI"}
)

kg.add_resource(person)
kg.add_resource(company)

# Add relationship
kg.add_edge(person, company, "WORKS_AT")

# Query
neighbors = kg.query("neighbors", resource_id=person.id)
print(f"Alice is connected to {len(neighbors)} entities")

# Export
kg.save_graph("my-graph.json")
```

### CLI examples

```bash
# Create new graph
kgforge create --name "my-graph" --description "My first KG"

# Query neighbors for a resource
kgforge query neighbors --resource-id <RESOURCE_ID>
```

## Architecture

```
kgforge/
├── core/         # core data models and logic
├── storage/      # backend implementations (NetworkX, Neo4j)
├── connector/    # data ingestion (CSV, JSON, APIs)
├── transform/    # processing and extraction
├── utils/        # utilities and helpers
└── cli/          # command line interface
```

├── storage/ # backend implementations (NetworkX, Neo4j)
├── connectors/ # data ingestion (CSV, JSON, APIs)
├── transforms/ # processing and extraction
├── utils/ # utilities and helpers
└── cli/ # command line interface

````

## API Reference (high level)

- KGForge — main interface for graph operations
- Resource — graph node/entity (labels + properties)
- Dataset — collection of resources and relationships
- Edge — relationship between two resources
- MemoryStorage — NetworkX-based in-memory backend
- BaseStorage — abstract base for custom backends

## Development

### Setup
```bash
git clone https://github.com/kgforge/kgforge
cd kgforge
pip install -e ".[dev]"
````

### Run tests and linters

```bash
pytest tests/
black kgforge/
isort kgforge/
flake8 kgforge/
mypy kgforge/
```

## Roadmap

- Phase 1: Core Package MVP (NetworkX, CLI, Python API) ✅
- Phase 2: Neo4j Integration + LLM Extraction
- Phase 3: KG Store (Private Alpha)
- Phase 4: Multi-tenancy + Streaming
- Phase 5: Public Release + Governance

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.

## Support

- Docs: https://kgforge.readthedocs.io
- Issues: https://github.com/kgforge/kgforge/issues
- Discussions: https://github.com/kgforge/kgforge/discussions

---
