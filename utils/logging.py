# utils/logging.py
from rich.console import Console
from rich.panel import Panel

console = Console()

def banner():
    console.print(Panel.fit("🎬 Blu-ray Workflow — Rip · Encode · Organize", style="magenta"))

def info(msg: str):
    console.print(f"[cyan][INFO][/cyan] {msg}")

def ok(msg: str):
    console.print(f"[green][OK][/green] {msg}")

def warn(msg: str):
    console.print(f"[yellow][WARN][/yellow] {msg}")

def err(msg: str):
    console.print(f"[red][ERROR][/red] {msg}")
