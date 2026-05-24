"""
CLI entry point for batch-property-intelligence.

Subcommands:
  bpi run       — one-shot pipeline on one or more CSVs (V1.1 behaviour, no DB)
  bpi watch     — start the Hub watcher on inputs/ (blocking)
  bpi ingest    — one-off DB ingest of a single CSV
  bpi rebuild   — regenerate the master dashboard from the current DB
  bpi launcher  — open the Tkinter launcher window
  bpi status    — print the latest status JSON
"""

import json
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from src.hub.dashboard import regenerate_dashboard
from src.hub.db import DEFAULT_DB_PATH, connect, db_stats
from src.hub.ingest import ingest_csv
from src.hub.recompute import recompute_all
from src.hub.status import read_status
from src.pipeline import run_pipeline


console = Console()


@click.group()
def cli():
    """Batch Property Intelligence — Elite Lifestyle Properties."""


# ─────────────── one-shot (V1.1 behaviour) ─────────────────────────────────

@cli.command()
@click.option("--input", "-i", "inputs", type=click.Path(exists=True, path_type=Path),
              multiple=True, required=True,
              help="Path to an RP Data CSV export. Repeat for multi-CSV runs.")
@click.option("--region", "-r", "region_label", required=True,
              help="Human-readable region label, e.g. 'Currimundi May 2026'.")
@click.option("--output-dir", "-o", type=click.Path(path_type=Path), default=Path("outputs"))
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path),
              default=Path("config/scoring-weights.yaml"))
def run(inputs, region_label, output_dir, config):
    """Run the one-shot pipeline (no DB, no Hub state)."""
    timestamp = datetime.now().strftime("%d-%m-%Y_%H%M")
    console.print(f"[bold #B8965A]Batch Property Intelligence — one-shot[/bold #B8965A]")
    console.print(f"Region: [bold]{region_label}[/bold]   Inputs: {[str(p) for p in inputs]}")
    summary = run_pipeline(
        input_paths=list(inputs), output_dir=output_dir,
        region_label=region_label, run_timestamp=timestamp, config_path=config,
    )
    _print_summary_table(summary)
    console.print(f"[bold green]XLSX:[/bold green] {summary['xlsx_path']}")
    console.print(f"[bold green]HTML:[/bold green] {summary['html_path']}")


# ─────────────── Hub ────────────────────────────────────────────────────────

@cli.command()
@click.option("--inputs", "inputs_dir", type=click.Path(path_type=Path), default=Path("inputs"))
@click.option("--outputs", "outputs_dir", type=click.Path(path_type=Path), default=Path("outputs"))
@click.option("--data", "db_path", type=click.Path(path_type=Path), default=DEFAULT_DB_PATH)
@click.option("--config", "config_path", type=click.Path(path_type=Path),
              default=Path("config/scoring-weights.yaml"))
def watch(inputs_dir, outputs_dir, db_path, config_path):
    """Start the Hub watcher (blocking). Each CSV dropped in `inputs/` is ingested + rescored."""
    from src.hub.watcher import run_watcher
    console.print(f"[bold #B8965A]BPI Hub watcher[/bold #B8965A]")
    console.print(f"Watching: {inputs_dir.resolve()}")
    console.print(f"DB:       {db_path.resolve()}")
    console.print(f"Outputs:  {outputs_dir.resolve()}")
    console.print("Press Ctrl+C to stop.\n")
    run_watcher(inputs_dir=inputs_dir, outputs_dir=outputs_dir,
                db_path=db_path, config_path=config_path)


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True, path_type=Path))
@click.option("--data", "db_path", type=click.Path(path_type=Path), default=DEFAULT_DB_PATH)
@click.option("--config", "config_path", type=click.Path(path_type=Path),
              default=Path("config/scoring-weights.yaml"))
@click.option("--outputs", "outputs_dir", type=click.Path(path_type=Path), default=Path("outputs"))
@click.option("--no-rebuild", is_flag=True, help="Ingest only; skip dashboard regeneration.")
def ingest(csv_path, db_path, config_path, outputs_dir, no_rebuild):
    """One-off CSV ingest into the Hub DB. Regenerates the master dashboard unless --no-rebuild."""
    delta = ingest_csv(csv_path, db_path, region_hint=csv_path.stem)
    console.print(f"[green]Ingested {delta['rows_in_csv']} rows from {csv_path.name}[/green]")
    console.print(f"  new parcels: {delta['new_parcels']}   new sales: {delta['new_sales']}")
    if no_rebuild:
        return
    _rebuild(db_path, config_path, outputs_dir)


@cli.command()
@click.option("--data", "db_path", type=click.Path(path_type=Path), default=DEFAULT_DB_PATH)
@click.option("--config", "config_path", type=click.Path(path_type=Path),
              default=Path("config/scoring-weights.yaml"))
@click.option("--outputs", "outputs_dir", type=click.Path(path_type=Path), default=Path("outputs"))
def rebuild(db_path, config_path, outputs_dir):
    """Recompute scores across the full DB and regenerate the master dashboard."""
    _rebuild(db_path, config_path, outputs_dir)


def _rebuild(db_path: Path, config_path: Path, outputs_dir: Path) -> None:
    summary = recompute_all(db_path, config_path)
    if summary.get("empty"):
        console.print("[yellow]DB is empty — nothing to render.[/yellow]")
        return
    dash = regenerate_dashboard(summary["df_final"], outputs_dir)
    _print_summary_table(summary)
    console.print(f"[bold green]XLSX:[/bold green] {dash['xlsx_path']}")
    console.print(f"[bold green]HTML:[/bold green] {dash['html_path']}")


@cli.command()
def launcher():
    """Open the Tkinter launcher window."""
    from src.launcher.app import main as launcher_main
    launcher_main()


@cli.command()
@click.option("--data", "db_path", type=click.Path(path_type=Path), default=DEFAULT_DB_PATH)
def status(db_path):
    """Print last-known status and DB stats."""
    st = read_status()
    with connect(db_path) as conn:
        stats = db_stats(conn)
    click.echo(json.dumps({"status": st, "db_stats": stats}, indent=2))


def _print_summary_table(summary: dict) -> None:
    table = Table(title="Run Summary", show_header=True, header_style="bold #B8965A")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    rows = [
        ("Sales records loaded", summary["sales_records_loaded"]),
        ("Unique parcels", summary["unique_parcels"]),
        ("Saleable parcels", summary["saleable_parcels"]),
        ("Non-saleable filtered", summary["non_saleable_filtered"]),
        ("Seller Lead: HIGH", summary["seller_high"]),
        ("Seller Lead: MEDIUM", summary["seller_medium"]),
        ("Seller Lead: LOW", summary["seller_low"]),
        ("Seller Lead: NO", summary["seller_no"]),
        ("Rental Lead: HIGH", summary["rental_high"]),
        ("Rental Lead: MEDIUM", summary["rental_medium"]),
        ("Rental Lead: LOW", summary["rental_low"]),
        ("Rental Lead: NO", summary["rental_no"]),
        ("Owners with 2+ properties", summary["owners_2plus"]),
        ("Owners with 3+ properties", summary["owners_3plus"]),
        ("Owners with 4+ (portfolio investors)", summary["owners_4plus"]),
        ("Confirmed rentals", summary["confirmed_rentals"]),
    ]
    for label, value in rows:
        table.add_row(label, str(value))
    console.print(table)


if __name__ == "__main__":
    cli()
