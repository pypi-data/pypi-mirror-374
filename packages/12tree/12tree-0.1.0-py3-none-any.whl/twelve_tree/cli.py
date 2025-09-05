"""CLI interface for 12Tree"""

import typer
from pathlib import Path
from typing import Optional
from twelve_tree import FloatTreeStore

app = typer.Typer(help="12Tree - Efficient Floating Point Data Store")

store = FloatTreeStore()

@app.command()
def insert(value: float, data: Optional[str] = None):
    """Insert a floating point value"""
    store.insert(value, data)
    typer.echo(f"Inserted {value}")

@app.command()
def search(value: float, tolerance: float = 0.0):
    """Search for a value with optional tolerance"""
    result = store.search(value, tolerance)
    if result:
        typer.echo(f"Found: {result}")
    else:
        typer.echo("Value not found")

@app.command()
def range_search(min_val: float, max_val: float):
    """Find all values within a range"""
    results = store.find_range(min_val, max_val)
    if results:
        for result in results:
            typer.echo(f"Value: {result['value']}, Data: {result['data']}")
    else:
        typer.echo("No values found in range")

@app.command()
def list_values():
    """List all stored values"""
    values = store.get_all_values()
    if values:
        for value in values:
            typer.echo(f"{value}")
    else:
        typer.echo("Store is empty")

@app.command()
def stats():
    """Show store statistics"""
    typer.echo(f"Size: {store.size()}")
    typer.echo(f"Is empty: {store.is_empty()}")

@app.command()
def save(filepath: str):
    """Save store to file"""
    store.save_to_file(filepath)
    typer.echo(f"Saved to {filepath}")

@app.command()
def load(filepath: str):
    """Load store from file"""
    if Path(filepath).exists():
        store.load_from_file(filepath)
        typer.echo(f"Loaded from {filepath}")
    else:
        typer.echo(f"File {filepath} does not exist")

@app.command()
def clear():
    """Clear all data"""
    store.clear()
    typer.echo("Store cleared")

if __name__ == "__main__":
    app()
