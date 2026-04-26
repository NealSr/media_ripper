# utils/tui.py
from __future__ import annotations

from contextlib import contextmanager
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn


class RipperTUI:
    def __init__(self) -> None:
        self.console = Console()
        self.log_lines: list[str] = []

        # Right-side tables
        self.metadata_table = self._empty_metadata_table()
        self.tmdb_table = self._empty_tmdb_table()

        # Progress bars
        self.scan_progress = self._make_progress("Scanning")
        self.rip_progress = self._make_progress("Ripping")
        self.encode_progress = self._make_progress("Encoding")

        self.scan_task = None
        self.rip_task = None
        self.encode_task = None

        self.layout = self._build_layout()
        self._live: Optional[Live] = None

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def stop(self):
        """Stop the Live display if running."""
        if self._live:
            self._live.stop()
            self._live = None

    def start(self):
        """Restart the Live display if not running."""
        if not self._live:
            self._live = Live(self.layout, refresh_per_second=20, console=self.console)
            self._live.start()

    def pause_for_input(self, prompt: str) -> str:
        """
        Stop the TUI, show a normal terminal prompt, then restart the TUI.
        Returns the user's input string.
        """
        # Stop Live so the prompt isn't hidden
        self.stop()

        # Ask the question
        answer = self.console.input(prompt)

        # Restart Live
        self.start()

        return answer


    def _make_progress(self, label: str):
        return Progress(
            TextColumn(f"[cyan]{label}[/cyan]"),
            BarColumn(bar_width=None),
            TextColumn("{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        )

    def _empty_metadata_table(self):
        t = Table(show_header=False, expand=True)
        t.add_column("Field", style="bold")
        t.add_column("Value")
        return t

    def _empty_tmdb_table(self):
        t = Table(show_header=False, expand=True)
        t.add_column("TMDB")
        return t


    # ------------------------------------------------------------------ #
    # Popup input dialog (inside the TUI)
    # ------------------------------------------------------------------ #

    def popup_input(self, prompt: str) -> str:
        """
        Display a modal popup inside the TUI and capture user input.
        """
        # Temporarily suspend Live rendering
        self.stop()

        # Build popup panel
        from rich.panel import Panel
        from rich.align import Align

        popup = Panel(
            Align.center(f"[bold cyan]{prompt}[/bold cyan]\n\n", vertical="middle"),
            title="[cyan]Input Required[/cyan]",
            border_style="cyan",
            padding=(1, 2),
        )

        # Render popup
        self.console.print(popup)

        # Get input
        answer = self.console.input("[bold]> [/bold]")

        # Restart TUI
        self.start()

        return answer

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #

    def _build_layout(self):
        layout = Layout(name="root")

        layout.split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=3),
        )

        layout["left"].update(Panel(Text("Log will appear here."), title="Log"))

        layout["right"].split(
            Layout(name="title_meta", ratio=1),
            Layout(name="movie_meta", ratio=1),
            Layout(name="scan_progress", ratio=1),
            Layout(name="rip_progress", ratio=1),
            Layout(name="encode_progress", ratio=1),
        )

        layout["right"]["title_meta"].update(
            Panel(self.metadata_table, title="Title Metadata")
        )
        layout["right"]["movie_meta"].update(
            Panel(self.tmdb_table, title="Movie Metadata")
        )
        layout["right"]["scan_progress"].update(
            Panel(self.scan_progress, title="Scan Progress")
        )
        layout["right"]["rip_progress"].update(
            Panel(self.rip_progress, title="Rip Progress")
        )
        layout["right"]["encode_progress"].update(
            Panel(self.encode_progress, title="Encode Progress")
        )

        return layout

    # ------------------------------------------------------------------ #
    # Live lifecycle
    # ------------------------------------------------------------------ #

    @contextmanager
    def run(self):
        self._live = Live(self.layout, refresh_per_second=20, console=self.console)
        self._live.start()
        try:
            yield self
        finally:
            self._live.stop()
            self._live = None

    def _refresh(self):
        if self._live:
            self._live.update(self.layout, refresh=True)

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #

    def log(self, message: str):
        # Keep last 500 lines
        self.log_lines.append(message)
        self.log_lines = self.log_lines[-500:]

        # Determine visible height safely
        layout_size = self.layout["left"].size
        if layout_size is None or layout_size.height is None:
            visible_lines = 20  # fallback before Live renders
        else:
            visible_lines = max(5, layout_size.height - 2)  # minus borders

        # Slice raw strings (NOT Rich Text)
        sliced_lines = self.log_lines[-visible_lines:]
        sliced_text = "\n".join(sliced_lines)

        # Now convert to Rich Text
        text = Text(sliced_text, no_wrap=True, overflow="fold")

        panel = Panel(
            text,
            title="Log",
            border_style="cyan",
            padding=(0, 1),
        )

        self.layout["left"].update(panel)
        self._refresh()


    # ------------------------------------------------------------------ #
    # Progress bar updates
    # ------------------------------------------------------------------ #

    def update_scan_progress(self, percent: float):
        if self.scan_task is None:
            self.scan_task = self.scan_progress.add_task("scan", total=100)
        self.scan_progress.update(self.scan_task, completed=percent)
        self._refresh()

    def update_rip_progress(self, percent: float):
        if self.rip_task is None:
            self.rip_task = self.rip_progress.add_task("rip", total=100)
        self.rip_progress.update(self.rip_task, completed=percent)
        self._refresh()

    def update_encode_progress(self, percent: float):
        if self.encode_task is None:
            self.encode_task = self.encode_progress.add_task("encode", total=100)
        self.encode_progress.update(self.encode_task, completed=percent)
        self._refresh()

    # ------------------------------------------------------------------ #
    # Metadata panels
    # ------------------------------------------------------------------ #

    def update_metadata(self, title):
        t = self._empty_metadata_table()

        def add(label, value):
            t.add_row(label, str(value) if value is not None else "—")

        add("ID", title.id)
        add("MPLS", title.mpls)
        add("Duration", title.duration)
        add("Chapters", title.chapters)
        add("Size (MB)", title.size_mb)
        add("Name", title.name)
        add("Classification", title.classification)
        add("Action", title.action)

        self.metadata_table = t
        self.layout["right"]["title_meta"].update(
            Panel(self.metadata_table, title="Title Metadata")
        )
        self._refresh()

    def update_tmdb(self, movie):
        t = self._empty_tmdb_table()

        def add(label, value):
            t.add_row(f"[bold]{label}[/bold]: {value}")

        add("Title", movie.title)
        add("Year", movie.year)

        if getattr(movie, "runtime", None):
            h = movie.runtime // 60
            m = movie.runtime % 60
            add("Runtime", f"{h}h {m}m")

        if getattr(movie, "genres", None):
            add("Genres", ", ".join(movie.genres))

        if getattr(movie, "score", None) is not None:
            add("Score", movie.score)

        if getattr(movie, "director", None):
            add("Director", movie.director)

        if getattr(movie, "cast", None):
            add("Cast", ", ".join(movie.cast[:5]))

        if getattr(movie, "overview", None):
            ov = movie.overview
            wrapped = "\n".join(ov[i:i+80] for i in range(0, len(ov), 80))
            add("Overview", wrapped)

        self.tmdb_table = t
        self.layout["right"]["movie_meta"].update(
            Panel(self.tmdb_table, title="Movie Metadata")
        )
        self._refresh()
