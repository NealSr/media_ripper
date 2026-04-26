# main.py
from rich.console import Console

from .cli import parse_args
from .utils.logging import banner, info
from .utils.tui import RipperTUI
from .makemkv.scanner import scan_disc
from .picker.picker import pick_titles
from .makemkv.ripper import rip_titles
from .encode.handbrake import encode_titles
from .organize.files import organize
from .tmdb.client import TMDBClient
from .models.movie import Movie


def main():
    args = parse_args()
    banner()

    tui = RipperTUI()
    console = Console()

    with tui.run():

        # Build movie object from CLI
        movie = Movie(title=args.movie_title, year=args.movie_year)

        # --- SCAN DISC ---
        titles, disc_label = scan_disc(args.device, tui=tui)

        # If user didn't provide a title, use disc label
        if not movie.title and disc_label:
            movie.title = disc_label

        # --- EMPTY TITLE LIST GUARD ---
        if not titles:
            tui.log("[red]No valid titles found on disc.[/red]")

            # Ask user for a movie name
            new_name = tui.pause_for_input(
                "\nNo titles detected. Enter movie name manually (or leave blank to abort): "
            ).strip()

            if not new_name:
                tui.log("[yellow]Aborting workflow — no movie name provided.[/yellow]")
                return

            movie.title = new_name
            movie.year = None
            tui.log(f"Using manual movie name: {movie.title}")

            # No titles → nothing to rip/encode → just organize folder
            organize([], movie, args.output_root, tui=tui)
            tui.log(f"Workflow complete for {movie.title}")
            return

        # --- STOP TUI BEFORE PICKER (avoid nested Live) ---
        tui.stop()

        # --- PICK TITLES (no TUI active here) ---
        titles = pick_titles(titles)

        # Filter out skipped titles
        selected = [t for t in titles if t.action != "skip"]

        # If user skipped everything, bail gracefully
        if not selected:
            console.print("[yellow]No titles selected. Aborting workflow.[/yellow]")
            return

        # --- RESTART TUI AFTER PICKER ---
        tui.start()

        # --- TMDB LOOKUP ---
        tmdb = TMDBClient(args.tmdb_key)
        tmdb.populate_movie(movie)
        tui.update_tmdb(movie)
        tui.log(f"TMDB metadata loaded for {movie.full_title}")

        # Inject movie context for filename generation
        for t in selected:
            t.movie_title = movie.title
            t.movie_year = movie.year

        # --- RIP ---
        tui.log("Starting rip…")
        rip_titles(selected, movie, args, tui=tui)

        # --- ENCODE ---
        tui.log("Starting encode…")
        encode_titles(selected, movie, args, tui=tui)

        # --- ORGANIZE ---
        tui.log("Organizing output…")
        organize(selected, movie, args.output_root, tui=tui)

        tui.log(f"Workflow complete for {movie.full_title}")

    info(f"Workflow complete for {movie.full_title}")


if __name__ == "__main__":
    main()
