"""
Individual CLI command implementations.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import print as rprint
from pathlib import Path
import json
import sys

from kgops import KGOps
from kgops.core.exceptions import KGOpsError
from kgops.transforms.converter import FormatConverter
from kgops.transforms.validator import DataValidator
from kgops.transforms.mapper import DataMapper

console = Console()


@click.command()
@click.option('--name', '-n', required=True, help='Graph name')
@click.option('--description', '-d', help='Graph description')
@click.option('--backend', '-b', default='networkx', help='Storage backend')
@click.option('--output', '-o', help='Save graph to file')
@click.pass_context
def create_graph(ctx, name, description, backend, output):
    """Create a new knowledge graph."""
    try:
        kg = KGOps(backend=backend, config=ctx.obj.get('config'))
        dataset = kg.create_graph(name=name, description=description)
        
        if output:
            kg.save_graph(output)
            rprint(f"[green]✓[/green] Graph saved to: {output}")
        
        rprint(f"[green]✓[/green] Created graph: {name}")
        
        # Show stats
        stats_table = Table(title="Graph Statistics")
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


@click.command()
@click.option('--source', '-s', required=True, help='Source file or directory')
@click.option('--format', '-f', default='auto', help='Input format (auto, csv, json)')
@click.option('--graph', '-g', required=True, help='Graph name or file')
@click.option('--id-field', help='Field to use as resource ID')
@click.option('--label-field', help='Field to use as labels')
@click.pass_context
def ingest_data(ctx, source, format, graph, id_field, label_field):
    """Ingest data from various sources into a knowledge graph."""
    try:
        kg = KGOps(config=ctx.obj.get('config'))
        converter = FormatConverter()
        
        # Load or create graph
        source_path = Path(source)
        if not source_path.exists():
            rprint(f"[red]✗[/red] Source not found: {source}")
            sys.exit(1)
        
        # Determine format
        if format == 'auto':
            format = source_path.suffix.lower().lstrip('.')
        
        # Create or load graph
        try:
            dataset = kg.load_graph(graph)
            if dataset is None:
                dataset = kg.create_graph(Path(graph).stem)
        except:
            dataset = kg.create_graph(Path(graph).stem)
        
        # Ingest data
        with Progress() as progress:
            task = progress.add_task("Ingesting data...", total=None)
            
            resources_added = 0
            
            if format == 'csv':
                for resource in converter.csv_to_resources(
                    source_path, 
                    id_field=id_field,
                    label_field=label_field
                ):
                    kg.add_resource(resource)
                    resources_added += 1
                    progress.update(task, description=f"Added {resources_added} resources")
            
            elif format == 'json':
                for resource in converter.json_to_resources(
                    source_path,
                    id_field=id_field or 'id',
                    label_field=label_field or 'labels'
                ):
                    kg.add_resource(resource)
                    resources_added += 1
                    progress.update(task, description=f"Added {resources_added} resources")
            
            else:
                rprint(f"[red]✗[/red] Unsupported format: {format}")
                sys.exit(1)
        
        # Save graph
        if isinstance(graph, str) and not Path(graph).exists():
            output_path = f"{graph}.json"
        else:
            output_path = graph
        
        kg.save_graph(output_path)
        
        rprint(f"[green]✓[/green] Ingested {resources_added} resources")
        rprint(f"[green]✓[/green] Saved to: {output_path}")
        
    except Exception as e:
        rprint(f"[red]✗[/red] Ingestion failed: {e}")
        sys.exit(1)


@click.command()
@click.option('--graph', '-g', required=True, help='Graph file')
@click.option('--schema', '-s', help='Validation schema file')
@click.option('--strict', is_flag=True, help='Strict validation mode')
@click.option('--output', '-o', help='Output validated graph')
@click.pass_context
def validate_graph(ctx, graph, schema, strict, output):
    """Validate and clean a knowledge graph."""
    try:
        kg = KGOps(config=ctx.obj.get('config'))
        dataset = kg.load_graph(graph)
        
        if dataset is None:
            rprint(f"[red]✗[/red] Graph not found: {graph}")
            sys.exit(1)
        
        # Load schema if provided
        schema_dict = None
        if schema:
            with open(schema, 'r') as f:
                schema_dict = json.load(f)
        
        # Create validator
        validator = DataValidator(schema=schema_dict, strict=strict)
        
        # Validate resources
        validated_count = 0
        error_count = 0
        
        with Progress() as progress:
            task = progress.add_task("Validating...", total=len(dataset.resources))
            
            for resource_id, resource in dataset.resources.items():
                try:
                    validated_resource = validator.transform(resource)
                    dataset.resources[resource_id] = validated_resource
                    validated_count += 1
                except Exception as e:
                    error_count += 1
                    if strict:
                        rprint(f"[red]✗[/red] Validation failed for {resource_id}: {e}")
                
                progress.update(task, advance=1)
        
        # Show validation report
        report = validator.get_validation_report()
        
        if report['error_count'] > 0:
            rprint(f"[yellow]⚠[/yellow] Found {report['error_count']} validation issues")
            for error in report['errors'][:5]:  # Show first 5 errors
                rprint(f"  - {error}")
            if len(report['errors']) > 5:
                rprint(f"  ... and {len(report['errors']) - 5} more")
        
        # Save validated graph
        output_path = output or graph
        kg.save_graph(output_path)
        
        rprint(f"[green]✓[/green] Validated {validated_count} resources")
        rprint(f"[green]✓[/green] Saved to: {output_path}")
        
    except Exception as e:
        rprint(f"[red]✗[/red] Validation failed: {e}")
        sys.exit(1)


@click.command()
@click.option('--graph', '-g', required=True, help='Graph file')
@click.option('--resource-id', '-r', help='Specific resource ID to show')
@click.option('--limit', '-l', default=10, help='Limit number of results')
@click.pass_context
def inspect_graph(ctx, graph, resource_id, limit):
    """Inspect graph contents and structure."""
    try:
        kg = KGOps(config=ctx.obj.get('config'))
        dataset = kg.load_graph(graph)
        
        if dataset is None:
            rprint(f"[red]✗[/red] Graph not found: {graph}")
            sys.exit(1)
        
        if resource_id:
            # Show specific resource
            resource = dataset.get_resource(resource_id)
            if resource is None:
                rprint(f"[red]✗[/red] Resource not found: {resource_id}")
                sys.exit(1)
            
            console.print(f"\n🔍 Resource: {resource_id}")
            console.print(f"Labels: {', '.join(sorted(resource.labels))}")
            console.print(f"Properties ({len(resource.properties)}):")
            
            prop_table = Table(show_header=True)
            prop_table.add_column("Property")
            prop_table.add_column("Value")
            prop_table.add_column("Type")
            
            for key, value in sorted(resource.properties.items()):
                prop_table.add_row(key, str(value)[:50], type(value).__name__)
            
            console.print(prop_table)
            
            # Show connected edges
            edges = dataset.get_edges(source=resource_id) + dataset.get_edges(target=resource_id)
            if edges:
                console.print(f"\n🔗 Connected Edges ({len(edges)}):")
                edge_table = Table(show_header=True)
                edge_table.add_column("Direction")
                edge_table.add_column("Type")
                edge_table.add_column("Connected To")
                
                for edge in edges[:limit]:
                    if edge.source == resource_id:
                        edge_table.add_row("OUT", edge.type, edge.target)
                    else:
                        edge_table.add_row("IN", edge.type, edge.source)
                
                console.print(edge_table)
        
        else:
            # Show graph overview
            stats = dataset.stats()
            
            console.print(f"\n📊 Graph Overview: {dataset.name}")
            
            # Basic stats
            basic_table = Table(show_header=True)
            basic_table.add_column("Metric")
            basic_table.add_column("Count")
            
            basic_table.add_row("Resources", str(stats['resources']))
            basic_table.add_row("Edges", str(stats['edges']))
            basic_table.add_row("Labels", str(len(stats['labels'])))
            basic_table.add_row("Edge Types", str(len(stats['edge_types'])))
            
            console.print(basic_table)
            
            # Sample resources
            if dataset.resources:
                console.print(f"\n🔍 Sample Resources (showing {min(limit, len(dataset.resources))}):")
                sample_table = Table(show_header=True)
                sample_table.add_column("ID")
                sample_table.add_column("Labels")
                sample_table.add_column("Properties")
                
                for i, (res_id, resource) in enumerate(dataset.resources.items()):
                    if i >= limit:
                        break
                    
                    labels_str = ", ".join(sorted(resource.labels)[:3])
                    if len(resource.labels) > 3:
                        labels_str += "..."
                    
                    sample_table.add_row(
                        res_id[:30] + "..." if len(res_id) > 30 else res_id,
                        labels_str,
                        str(len(resource.properties))
                    )
                
                console.print(sample_table)
        
    except Exception as e:
        rprint(f"[red]✗[/red] Inspection failed: {e}")
        sys.exit(1)


@click.command()
@click.option('--format', '-f', default='table', help='Output format (table, json)')
@click.pass_context
def list_graphs(ctx, format):
    """List available graphs."""
    try:
        # This would need to be enhanced based on storage backend
        rprint("[yellow]ℹ[/yellow] Graph listing not implemented for current storage backend")
        rprint("Use file system to browse saved .json files")
        
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to list graphs: {e}")
        sys.exit(1)
