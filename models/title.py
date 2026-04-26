# models/title.py
from dataclasses import dataclass, field

@dataclass
class Title:
    id: int

    # Core metadata from MakeMKV
    mpls: str | None = None
    duration: int = 0
    chapters: int = 0
    audio_tracks: list[str] = field(default_factory=list)
    subtitle_tracks: list[str] = field(default_factory=list)
    size_mb: int = 0

    # Classification / scoring
    score: int = 0
    classification: str | None = None

    # Optional metadata
    name: str | None = None
    type: str | None = None
    source: str | None = None

    # Picker workflow fields
    action: str = "keep"
    new_name: str | None = None

    # Movie context (injected later)
    movie_title: str | None = None
    movie_year: int | None = None

    @property
    def playlist_id(self) -> str | None:
        if self.mpls:
            return self.mpls.replace(".mpls", "")
        return None

    @property
    def bonus_display_name(self) -> str:
        """
        The part AFTER the main movie name.
        """
        # 1. User rename
        if self.new_name:
            return self.new_name.replace(" ", "_")

        # 2. MakeMKV name
        if self.name:
            return self.name.replace(" ", "_")

        # 3. Classification fallback
        if self.classification:
            return f"{self.classification.title()}_{self.id:02d}"

        # 4. Generic fallback
        return f"Title_{self.id:02d}"

    @property
    def safe_movie_name(self) -> str:
        if not self.movie_title:
            return "UnknownMovie"
        return self.movie_title.replace(" ", "_")

    @property
    def final_filename(self) -> str:
        """
        <MainMovieName>_(<year>)_<BonusName>_t<ID>_<MPLS>.mkv
        """
        year = f"({self.movie_year})" if self.movie_year else ""
        pid = self.playlist_id or "unknown"

        return (
            f"{self.safe_movie_name}_{year}_"
            f"{self.bonus_display_name}_"
            f"t{self.id:02d}_{pid}.mkv"
        )
