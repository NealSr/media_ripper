# tmdb/client.py
from __future__ import annotations

import os
import requests
from typing import Optional

from ..models.movie import Movie


class TMDBClient:
    """
    Minimal TMDB API client for movie search + metadata fetch.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise RuntimeError("TMDB API key not set. Set TMDB_API_KEY env var.")

        self.base = "https://api.themoviedb.org/3"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict):
        params["api_key"] = self.api_key
        url = f"{self.base}{path}"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_movie(self, query: str, year: Optional[int] = None):
        """
        Search TMDB for a movie by title (and optional year).
        Returns the best match dict or None.
        """
        params = {"query": query}
        if year:
            params["year"] = year

        data = self._get("/search/movie", params)

        results = data.get("results", [])
        if not results:
            return None

        # Best match = first result
        return results[0]

    def get_movie_details(self, movie_id: int):
        """
        Fetch full movie details including credits.
        """
        details = self._get(f"/movie/{movie_id}", params={})
        credits = self._get(f"/movie/{movie_id}/credits", params={})

        return details, credits

    # ------------------------------------------------------------------
    # High-level helper: populate Movie model
    # ------------------------------------------------------------------

    def populate_movie(self, movie: Movie):
        """
        Given a Movie(title, year), search TMDB and populate metadata.
        Mutates the Movie object.
        """

        # 1. Search
        result = self.search_movie(movie.title, movie.year)
        if not result:
            return movie  # no match, leave as-is

        movie_id = result["id"]

        # 2. Fetch full details
        details, credits = self.get_movie_details(movie_id)

        # 3. Populate fields
        movie.runtime = details.get("runtime")
        movie.genres = [g["name"] for g in details.get("genres", [])]
        movie.score = details.get("vote_average")
        movie.tagline = details.get("tagline")
        movie.overview = details.get("overview")

        # Director
        crew = credits.get("crew", [])
        directors = [c["name"] for c in crew if c.get("job") == "Director"]
        movie.director = directors[0] if directors else None

        # Cast (top 5)
        cast = credits.get("cast", [])
        movie.cast = [c["name"] for c in cast[:5]]

        return movie
