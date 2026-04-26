# picker/picker.py
from rich.console import Console
from ..utils.durations import seconds_to_hms

console = Console()


def pick_titles(titles, tui=None):
    """
    Simple text-based picker using TUI popups for input.
    Actions:
      y = keep
      n = skip
      r = rename
      enter = keep (default)
    """

    console.print("\n[bold cyan]Title Selection[/bold cyan]")
    console.print(
        "For each title: [green]y[/green]=keep  "
        "[red]n[/red]=skip  "
        "[cyan]r[/cyan]=rename  "
        "[dim](enter=keep)[/dim]\n"
    )

    for t in titles:
        # Show basic info
        console.print(
            f"\n[bold]{t.name} - {t.id}[/bold]: {t.mpls or '—'}  "
            f"[dim]{seconds_to_hms(t.duration)}, {t.chapters} chapters[/dim]"
        )

        # Ask user (via popup if TUI is active)
        if tui:
            choice = tui.popup_input("Keep this title? [y/n/r]").strip().lower()
        else:
            choice = console.input("Keep this title? [y/n/r]: ").strip().lower()

        # Skip
        if choice == "n":
            t.action = "skip"
            continue

        # Rename
        if choice == "r":
            if tui:
                new_name = tui.popup_input("Enter new name: ").strip()
            else:
                new_name = console.input("Enter new name: ").strip()

            if new_name:
                t.new_name = new_name
                t.action = "rename"
            else:
                t.action = "keep"
            continue

        # Default: keep
        t.action = "keep"

    return titles
