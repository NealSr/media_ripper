# models/movie.py
from __future__ import annotations

from dataclasses import dataclass, field
import re


def _safe(s: str) -> str:
    """Convert a string into a filesystem-safe token."""
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


@dataclass
class Movie:
    """
    Represents a movie selected or matched from TMDB.
    This object is the single source of truth for movie-level metadata.
    """

    disc_label: str
    title: str
    year: int | str | None = None

    # TMDB metadata (optional)
    tmdb_id: int | None = None
    runtime: int | None = None
    genres: list[str] = field(default_factory=list)
    score: float | None = None
    director: str | None = None
    cast: list[str] = field(default_factory=list)
    tagline: str | None = None
    overview: str | None = None

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def full_title(self) -> str:
        """
        Returns: "Movie Title (Year)" if year exists,
                 otherwise just "Movie Title".
        """
        if self.year:
            return f"{self.title} ({self.year})"
        return self.title

    @property
    def safe_title(self) -> str:
        """
        Filesystem-safe folder name for the movie.
        Example: "The_Matrix_1999"
        """
        if self.year:
            return f"{_safe(self.title)}_{self.year}"
        return _safe(self.title)

    @property
    def safe_filename(self) -> str:
        """
        Base filename for encoded output.
        Example: "The_Matrix_1999"
        """
        return self.safe_title

    # ------------------------------------------------------------------
    # Helpers for debugging / logging
    # ------------------------------------------------------------------

    def short(self) -> str:
        """Short human-readable label."""
        return self.full_title

    def __str__(self):
        return self.full_title

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_disc_label(cls, disc_label: str | None) -> Movie:
        """
        Fallback when TMDB is unavailable or no match is found.
        Uses disc label as the title and leaves metadata empty.
        """
        title = disc_label or "NULL_DISC_LABEL"
        return cls(title=title, year=None)
