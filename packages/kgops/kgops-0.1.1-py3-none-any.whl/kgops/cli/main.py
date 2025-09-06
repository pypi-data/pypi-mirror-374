"""
Main entry point for the kgops CLI.
"""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import sys
from pathlib import Path

from kgops import KGOps, __version__
from kgops.core.exceptions import KGOpsError
from kgops.utils.logging import configure_logging

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.pass_context
def cli(ctx, verbose, config):
    """
    kgops - End-to-End Knowledge Graph Builder for RAG & Sharing
    
    A Python framework for building, maintaining, and sharing Knowledge Graphs
    with LLM-assisted extraction and multi-tenant support.
    """
    # Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(level=log_level)
    
    # Ensure context exists
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config


@cli.command()
@click.option('--name', '-n', required=True, help='Graph name')
@click.option('--description', '-d', help='Graph description')
@click.option('--backend', '-b', default='networkx', help='Storage backend (default: networkx)')
@click.pass_context
def create(ctx, name, description, backend):
    """Create a new knowledge graph."""
    try:
        kg = KGOps(backend=backend, config=ctx.obj.get('config'))
        dataset = kg.create_graph(name=name, description=description)
        
        rprint(f"[green]✓[/green] Created graph: {name}")
        rprint(f"  Backend: {backend}")
        if description:
            rprint(f"  Description: {description}")
        
        console.print("\n📊 Graph Statistics:")
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric")
        stats_table.add_column("Value")
        
        stats = dataset.stats()
        stats_table.add_row("Resources", str(stats['resources']))
        stats_table.add_row("Edges", str(stats['edges']))
        stats_table.add_row("Created", stats['created_at'])
        
        console.print(stats_table)
        
    except KGOpsError as e:
        rprint(f"[red]✗[/red] Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--source', '-s', required=True, type=click.Path(exists=True), help='Source file path')
@click.option('--format', '-f', default='auto', help='Input format (auto, json)')
@click.option('--backend', '-b', default='networkx', help='Storage backend')
@click.pass_context
def load(ctx, source, format, backend):
    """Load a knowledge graph from file."""
    try:
        kg = KGOps(backend=backend, config=ctx.obj.get('config'))
        dataset = kg.load_graph(source=source, format=format)
        
        rprint(f"[green]✓[/green] Loaded graph: {dataset.name}")
        rprint(f"  Source: {source}")
        rprint(f"  Backend: {backend}")
        
        console.print("\n📊 Graph Statistics:")
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric")
        stats_table.add_column("Value")
        
        stats = dataset.stats()
        stats_table.add_row("Resources", str(stats['resources']))
        stats_table.add_row("Edges", str(stats['edges']))
        stats_table.add_row("Labels", str(len(stats['labels'])))
        stats_table.add_row("Edge Types", str(len(stats['edge_types'])))
        
        console.print(stats_table)
        
    except KGOpsError as e:
        rprint(f"[red]✗[/red] Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--graph', '-g', required=True, help='Graph file path')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--format', '-f', default='auto', help='Export format (auto, json, networkx)')
@click.option('--backend', '-b', default='networkx', help='Storage backend')
@click.pass_context
def export(ctx, graph, output, format, backend):
    """Export a knowledge graph to various formats."""
    try:
        kg = KGOps(backend=backend, config=ctx.obj.get('config'))
        dataset = kg.load_graph(source=graph)
        
        if format == 'auto':
            # Determine format from output extension
            output_path = Path(output)
            ext = output_path.suffix.lower().lstrip('.')
            
            if ext == 'json':
                format = 'json'
            elif ext in ['graphml', 'gml']:
                format = 'networkx'
            else:
                format = 'json'
        
        if format == 'json':
            dataset.to_json(output)
            rprint(f"[green]✓[/green] Exported to JSON: {output}")
        
        elif format == 'networkx':
            nx_graph = kg.export(format='networkx')
            
            # Save as GraphML
            import networkx as nx
            output_path = Path(output)
            
            if output_path.suffix.lower() == '.graphml':
                nx.write_graphml(nx_graph, output)
            elif output_path.suffix.lower() == '.gml':
                nx.write_gml(nx_graph, output)
            else:
                # Default to GraphML
                nx.write_graphml(nx_graph, str(output_path.with_suffix('.graphml')))
            
            rprint(f"[green]✓[/green] Exported to NetworkX format: {output}")
        
        else:
            raise KGOpsError(f"Unsupported export format: {format}")
        
    except KGOpsError as e:
        rprint(f"[red]✗[/red] Error: {e}")
        sys.exit(1)
    except ImportError as e:
        rprint(f"[red]✗[/red] Missing dependency for NetworkX export: {e}")
        sys.exit(1)


@cli.command()
@click.option('--graph', '-g', required=True, type=click.Path(exists=True), help='Graph file path')
@click.option('--query', '-q', default='stats', help='Query type (stats, labels, edges)')
@click.option('--backend', '-b', default='networkx', help='Storage backend')
@click.pass_context
def query(ctx, graph, query, backend):
    """Query a knowledge graph."""
    try:
        kg = KGOps(backend=backend, config=ctx.obj.get('config'))
        dataset = kg.load_graph(source=graph)
        
        if query == 'stats':
            stats = dataset.stats()
            
            console.print(f"\n📊 Graph Statistics for: {dataset.name}")
            
            # Basic stats
            basic_table = Table(show_header=True, header_style="bold magenta")
            basic_table.add_column("Metric")
            basic_table.add_column("Value")
            
            basic_table.add_row("Resources", str(stats['resources']))
            basic_table.add_row("Edges", str(stats['edges']))
            basic_table.add_row("Created", stats['created_at'])
            basic_table.add_row("Updated", stats['updated_at'])
            
            console.print(basic_table)
            
            # Label distribution
            if stats['labels']:
                console.print("\n🏷️  Label Distribution:")
                label_table = Table(show_header=True, header_style="bold blue")
                label_table.add_column("Label")
                label_table.add_column("Count")
                
                for label, count in sorted(stats['labels'].items(), key=lambda x: x[1], reverse=True):
                    label_table.add_row(label, str(count))
                
                console.print(label_table)
            
            # Edge type distribution
            if stats['edge_types']:
                console.print("\n🔗 Edge Type Distribution:")
                edge_table = Table(show_header=True, header_style="bold green")
                edge_table.add_column("Edge Type")
                edge_table.add_column("Count")
                
                for edge_type, count in sorted(stats['edge_types'].items(), key=lambda x: x[1], reverse=True):
                    edge_table.add_row(edge_type, str(count))
                
                console.print(edge_table)
        
        elif query == 'labels':
            resources_by_label = {}
            for resource in dataset.resources.values():
                for label in resource.labels:
                    if label not in resources_by_label:
                        resources_by_label[label] = []
                    resources_by_label[label].append(resource)
            
            console.print(f"\n🏷️  Labels in: {dataset.name}")
            for label, resources in sorted(resources_by_label.items()):
                console.print(f"  {label}: {len(resources)} resources")
        
        elif query == 'edges':
            edge_types = {}
            for edge in dataset.edges:
                if edge.type not in edge_types:
                    edge_types[edge.type] = []
                edge_types[edge.type].append(edge)
            
            console.print(f"\n🔗 Edge Types in: {dataset.name}")
            for edge_type, edges in sorted(edge_types.items()):
                console.print(f"  {edge_type}: {len(edges)} edges")
        
        else:
            rprint(f"[red]✗[/red] Unsupported query type: {query}")
            sys.exit(1)
        
    except KGOpsError as e:
        rprint(f"[red]✗[/red] Error: {e}")
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    rprint(f"kgops version {__version__}")
    rprint("End-to-End Knowledge Graph Builder for RAG & Sharing")


@cli.command()
def init():
    """Initialize a new kgops project."""
    try:
        # Create basic project structure
        project_dir = Path.cwd()
        
        # Create directories
        (project_dir / "data").mkdir(exist_ok=True)
        (project_dir / "config").mkdir(exist_ok=True)
        (project_dir / "graphs").mkdir(exist_ok=True)
        
        # Create example config
        example_config = {
            "version": __version__,
            "graph": {
                "backend": "networkx",
                "options": {}
            },
            "metadata": {
                "project": "my-kg-project",
                "created_at": "2025-09-02T20:41:00Z"
            }
        }
        
        import json
        config_path = project_dir / "config" / "kgops.json"
        with open(config_path, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        # Create example usage script
        example_script = '''#!/usr/bin/env python3
"""
Example kgops usage script
"""

from kgops import KGOps, Resource

# Initialize KGOps
kg = KGOps(config="config/kgops.json")

# Create a new graph
graph = kg.create_graph("my-first-graph", description="Example knowledge graph")

# Add some resources
person = Resource(
    labels={"Person"},
    properties={
        "name": "Alice Johnson",
        "age": 30,
        "occupation": "Data Scientist"
    }
)

company = Resource(
    labels={"Organization", "Company"},
    properties={
        "name": "TechCorp",
        "industry": "Technology",
        "founded": 2010
    }
)

kg.add_resource(person)
kg.add_resource(company)

# Add relationship
kg.add_edge(person, company, "WORKS_AT", start_date="2023-01-01")

# Query the graph
print("Graph statistics:", kg.stats())

# Export
kg.save_graph("graphs/my-first-graph.json")
print("Graph saved!")
'''
        
        example_path = project_dir / "example.py"
        with open(example_path, 'w') as f:
            f.write(example_script)
        
        rprint(f"[green]✓[/green] Initialized kgops project in: {project_dir}")
        rprint("📁 Created directories:")
        rprint("  • data/     - for input data files")
        rprint("  • config/   - for configuration files") 
        rprint("  • graphs/   - for saved knowledge graphs")
        rprint(f"\n📄 Created files:")
        rprint(f"  • config/kgops.json - example configuration")
        rprint(f"  • example.py - example usage script")
        rprint(f"\n🚀 Next steps:")
        rprint(f"  1. Edit config/kgops.json to customize settings")
        rprint(f"  2. Run: python example.py")
        rprint(f"  3. Explore the CLI: kgops --help")
        
    except Exception as e:
        rprint(f"[red]✗[/red] Error initializing project: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        rprint("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗[/red] Unexpected error: {e}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
