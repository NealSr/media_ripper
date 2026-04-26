# organize/nfo.py
from pathlib import Path
from ..models.movie import Movie

def write_nfo(movie: Movie, target_dir: Path):
    nfo_path = target_dir / "movie.nfo"
    lines = [
        "<movie>",
        f"  <title>{movie.title}</title>",
        f"  <year>{movie.year or ''}</year>",
        f"  <plot>{(movie.overview or '').strip()}</plot>",
        "</movie>",
    ]
    nfo_path.write_text("\n".join(lines), encoding="utf-8")
