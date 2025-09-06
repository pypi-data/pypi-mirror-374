# KGOps — End-to-End Knowledge Graph Builder

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
pip install kgops
```

### Initialize a project

```bash
kgops init
```

### Basic Python usage

```python
from kgops import KGOps, Resource

# Initialize
kg = KGOps(backend="networkx")

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
kgops create --name "my-graph" --description "My first KG"

# Query neighbors for a resource
kgops query neighbors --resource-id <RESOURCE_ID>
```

## Architecture

```
kgops/
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

- KGOps — main interface for graph operations
- Resource — graph node/entity (labels + properties)
- Dataset — collection of resources and relationships
- Edge — relationship between two resources
- MemoryStorage — NetworkX-based in-memory backend
- BaseStorage — abstract base for custom backends

## Development

### Setup
```bash
git clone https://github.com/SohamChaudhari2004/kgops
cd kgops
pip install -e ".[dev]"
````

### Run tests and linters

```bash
pytest tests/
black kgops/
isort kgops/
flake8 kgops/
mypy kgops/
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

- Docs: https://kgops.readthedocs.io
- Issues: https://github.com/SohamChaudhari2004/kgops/issues
- Discussions: https://github.com/SohamChaudhari2004/kgops/discussions

---
