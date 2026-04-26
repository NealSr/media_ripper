# organize/files.py
from pathlib import Path


def organize(titles, movie, output_root, tui=None):
    """
    Move ripped/encoded files into a movie-specific folder:

      <output_root>/<MainMovieName>_(<year>)/

    Filenames are already in the form:
      <MainMovieName>_(<year>)_<BonusName>_t<ID>_<MPLS>.mkv
    """

    root = Path(output_root)

    safe_movie_name = (movie.title or "NullMovie").replace(" ", "_")
    year = f"({movie.year})" if movie.year else ""
    movie_dir = root / f"{safe_movie_name}_{year}"

    movie_dir.mkdir(parents=True, exist_ok=True)

    if tui:
        tui.log(f"Organizing files into {movie_dir}")

    for title in titles:
        # We assume encode step produced final files in output_root
        src = root / title.final_filename
        dst = movie_dir / title.final_filename

        if not src.exists():
            if tui:
                tui.log(f"[yellow]Missing file, cannot organize: {src.name}[/yellow]")
            continue

        if tui:
            tui.log(f"Moving {src.name} → {dst}")

        src.replace(dst)

    if tui:
        tui.log("Organizing complete.")
