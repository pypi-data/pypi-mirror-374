"""Simple data utilities CLI."""

import typer
from pathlib import Path
from typing_extensions import Annotated
from enum import StrEnum
import polars as pl
from rich.console import Console
from rich.table import Table
import random
from datetime import datetime, timedelta
import time

# Import shared models from workspace
from ml_core import DatasetInfo, ProcessingResult

app = typer.Typer(
    help="Simple data utilities for common data operations.",
    rich_markup_mode="markdown"
)
console = Console()

class OutputFormat(StrEnum):
    csv = "csv"
    parquet = "parquet"
    json = "json"

@app.command()
def generate(
    rows: Annotated[int, typer.Option(help="Number of rows to generate")] = 1000,
    output: Annotated[Path, typer.Option(help="Output file path")] = Path("sample_data.parquet"),
    seed: Annotated[int, typer.Option(help="Random seed for reproducibility")] = 42
):
    """Generate sample data for testing."""
    random.seed(seed)
    
    console.print(f"🎲 Generating {rows:,} rows of sample data...", style="cyan")
    
    # Generate sample data
    base_date = datetime(2024, 1, 1)
    data = {
        "id": range(1, rows + 1),
        "name": [f"User_{i:04d}" for i in range(1, rows + 1)],
        "email": [f"user{i}@example.com" for i in range(1, rows + 1)],
        "age": [random.randint(18, 80) for _ in range(rows)],
        "score": [random.uniform(0, 100) for _ in range(rows)],
        "category": [random.choice(["A", "B", "C", "D"]) for _ in range(rows)],
        "created_at": [base_date + timedelta(days=random.randint(0, 365)) for _ in range(rows)],
        "is_active": [random.choice([True, False]) for _ in range(rows)],
    }
    
    df = pl.DataFrame(data)
    
    # Save based on file extension
    if output.suffix.lower() == ".parquet":
        df.write_parquet(output)
    elif output.suffix.lower() == ".csv":
        df.write_csv(output)
    elif output.suffix.lower() == ".json":
        df.write_json(output)
    else:
        console.print(f"❌ Unsupported file format: {output.suffix}", style="red")
        raise typer.Exit(1)
    
    # Create dataset info using shared model
    file_size_mb = output.stat().st_size / 1024 / 1024
    dataset_info = DatasetInfo(
        name=output.name,
        rows=df.shape[0],
        columns=df.shape[1],
        file_size_mb=file_size_mb,
        created_at=datetime.now(),
        metadata={"seed": seed, "format": output.suffix.lower()}
    )
    
    console.print(f"✅ Generated data saved to: {output}", style="green")
    console.print(f"📊 {dataset_info.summary}", style="blue")

@app.command()
def inspect(
    file_path: Annotated[Path, typer.Argument(help="Path to data file to inspect")]
):
    """Inspect a data file and show basic statistics."""
    if not file_path.exists():
        console.print(f"❌ File not found: {file_path}", style="red")
        raise typer.Exit(1)
    
    console.print(f"🔍 Inspecting: {file_path}", style="cyan")
    
    # Read file based on extension
    try:
        if file_path.suffix.lower() == ".parquet":
            df = pl.read_parquet(file_path)
        elif file_path.suffix.lower() == ".csv":
            df = pl.read_csv(file_path)
        elif file_path.suffix.lower() == ".json":
            df = pl.read_json(file_path)
        else:
            console.print(f"❌ Unsupported file format: {file_path.suffix}", style="red")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error reading file: {e}", style="red")
        raise typer.Exit(1)
    
    # Basic info
    console.print(f"\n📊 **Dataset Overview**", style="bold blue")
    console.print(f"   • Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    console.print(f"   • File size: {file_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Column info
    console.print(f"\n📋 **Column Information**", style="bold blue")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Column", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Null Count", style="yellow")
    table.add_column("Null %", style="yellow")
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].null_count()
        null_pct = (null_count / df.shape[0]) * 100
        table.add_row(col, dtype, f"{null_count:,}", f"{null_pct:.1f}%")
    
    console.print(table)
    
    # Show first few rows
    console.print(f"\n👀 **First 5 rows**", style="bold blue")
    console.print(df.head())

@app.command()
def convert(
    input_file: Annotated[Path, typer.Argument(help="Input file path")],
    output: Annotated[Path, typer.Option(help="Output file path")] = None,
    format: Annotated[OutputFormat, typer.Option(help="Output format")] = OutputFormat.csv
):
    """Convert data between different formats."""
    if not input_file.exists():
        console.print(f"❌ File not found: {input_file}", style="red")
        raise typer.Exit(1)
    
    # Determine output file if not specified
    if output is None:
        output = input_file.with_suffix(f".{format.value}")
    
    console.print(f"🔄 Converting {input_file} → {output}", style="cyan")
    
    # Read input file
    try:
        if input_file.suffix.lower() == ".parquet":
            df = pl.read_parquet(input_file)
        elif input_file.suffix.lower() == ".csv":
            df = pl.read_csv(input_file)
        elif input_file.suffix.lower() == ".json":
            df = pl.read_json(input_file)
        else:
            console.print(f"❌ Unsupported input format: {input_file.suffix}", style="red")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error reading input file: {e}", style="red")
        raise typer.Exit(1)
    
    # Write output file
    try:
        if format == OutputFormat.parquet:
            df.write_parquet(output)
        elif format == OutputFormat.csv:
            df.write_csv(output)
        elif format == OutputFormat.json:
            df.write_json(output)
    except Exception as e:
        console.print(f"❌ Error writing output file: {e}", style="red")
        raise typer.Exit(1)
    
    console.print(f"✅ Converted successfully!", style="green")
    console.print(f"📊 Processed {df.shape[0]:,} rows × {df.shape[1]} columns", style="blue")

@app.command()
def stats(
    file_path: Annotated[Path, typer.Argument(help="Path to data file")]
):
    """Show detailed statistics for numeric columns."""
    if not file_path.exists():
        console.print(f"❌ File not found: {file_path}", style="red")
        raise typer.Exit(1)
    
    console.print(f"📈 Computing statistics for: {file_path}", style="cyan")
    
    # Read file
    try:
        if file_path.suffix.lower() == ".parquet":
            df = pl.read_parquet(file_path)
        elif file_path.suffix.lower() == ".csv":
            df = pl.read_csv(file_path)
        elif file_path.suffix.lower() == ".json":
            df = pl.read_json(file_path)
        else:
            console.print(f"❌ Unsupported file format: {file_path.suffix}", style="red")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Error reading file: {e}", style="red")
        raise typer.Exit(1)
    
    # Get numeric columns
    numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]]
    
    if not numeric_cols:
        console.print("❌ No numeric columns found in the dataset", style="red")
        raise typer.Exit(1)
    
    console.print(f"\n📊 **Statistics for {len(numeric_cols)} numeric columns**", style="bold blue")
    
    # Calculate statistics
    stats_df = df.select(numeric_cols).describe()
    console.print(stats_df.to_pandas().to_string(index=False))

if __name__ == "__main__":
    app()
