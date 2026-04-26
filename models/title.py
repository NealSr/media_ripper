from __future__ import annotations

from dataclasses import dataclass, field
import re


def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


@dataclass
class Title:
    id: int
    mpls: str | None
    duration: int
    chapters: int
    audio_tracks: list[str] = field(default_factory=list)
    subtitle_tracks: list[str] = field(default_factory=list)
    size_mb: int = 0
    name: str = ""
    source: str | None = None

    action: str = "skip"
    movie_title: str | None = None
    movie_year: int | str | None = None

    is_main: bool = False
    is_bonus: bool = False

    @property
    def safe_movie_name(self) -> str:
        if not self.movie_title:
            return "UnknownMovie"
        return _safe(self.movie_title)

    @property
    def bonus_display_name(self) -> str:
        if self.is_main:
            return "Main"
        if self.is_bonus:
            return f"Bonus{self.id:02d}"
        return f"Title{self.id:02d}"

    @property
    def final_filename(self) -> str:
        year = f"_{self.movie_year}" if self.movie_year else ""
        return f"{self.safe_movie_name}{year}_{self.bonus_display_name}_t{self.id:02d}.mkv"
