from __future__ import annotations
import time
from pathlib import Path
import typer
from rich.console import Console

from .config import load_config
from .pipeline import process_pdf
from .utils import ensure_dir

app = typer.Typer(add_completion=False)
console = Console()

@app.command()
def run(
    pdf: Path = typer.Option(..., exists=True, readable=True, help="PDF to process"),
    config: Path = typer.Option(..., exists=True, readable=True, help="Path to TOML config"),
):
    cfg = load_config(config)
    ensure_dir(cfg.inbox.archive_path)
    result = process_pdf(pdf_path=pdf, cfg=cfg)
    console.print(f"[bold green]Done[/] status={result.status} run_id={result.run_id}")

@app.command()
def watch(
    inbox: Path = typer.Option(..., exists=True, readable=True, help="Folder to watch for PDFs"),
    config: Path = typer.Option(..., exists=True, readable=True, help="Path to TOML config"),
    poll_seconds: int = typer.Option(3, help="Polling interval"),
):
    cfg = load_config(config)
    ensure_dir(cfg.inbox.archive_path)
    console.print(f"Watching [bold]{inbox}[/]... (poll={poll_seconds}s)")
    seen: set[Path] = set()
    while True:
        for pdf in inbox.glob("*.pdf"):
            if pdf in seen:
                continue
            seen.add(pdf)
            try:
                result = process_pdf(pdf_path=pdf, cfg=cfg)
                console.print(f"[green]Processed[/] {pdf.name} -> {result.status}")
            except Exception as e:
                console.print(f"[red]Failed[/] {pdf.name}: {e}")
        time.sleep(poll_seconds)