# src/media_ripper/tmdb/client.py
from __future__ import annotations

import requests
from typing import Optional

from ..models.movie import Movie

TMDB_BASE = "https://api.themoviedb.org/3"


def _search_movie(api_key: str, title: str, year: Optional[int] = None):
    params = {
        "api_key": api_key,
        "query": title,
    }
    if year:
        params["year"] = year

    r = requests.get(f"{TMDB_BASE}/search/movie", params=params)
    r.raise_for_status()
    data = r.json()

    results = data.get("results", [])
    return results[0] if results else None


def _fetch_movie_details(api_key: str, movie_id: int):
    params = {"api_key": api_key, "append_to_response": "credits"}
    r = requests.get(f"{TMDB_BASE}/movie/{movie_id}", params=params)
    r.raise_for_status()
    return r.json()


def _manual_movie_entry(disc_label: Optional[str]) -> Movie:
    print("\n=== Manual Movie Entry ===")

    title = input("Enter movie title: ").strip() or disc_label or "Unknown Movie"
    year = input("Enter release year: ").strip() or "0000"
    runtime = input("Enter runtime (minutes): ").strip()
    genres = input("Enter genres (comma-separated): ").strip()
    overview = input("Enter overview (optional): ").strip()

    return Movie(
        title=title,
        year=year,
        runtime=int(runtime) if runtime.isdigit() else None,
        genres=[g.strip() for g in genres.split(",")] if genres else [],
        tagline=None,
        overview=overview or None,
        score=None,
        cast=[],
        director=None,
        disc_label=disc_label,
    )


def fetch_movie_metadata(args, disc_label: Optional[str]) -> Movie:
    """
    TMDB flow:
      1. Try TMDB search
      2. If found → ask user to confirm
      3. If rejected or not found → ask for custom search
      4. If still not found → manual entry
    """

    # No TMDB key → fallback immediately
    if not args.tmdb_key:
        print("No TMDB key provided — using disc label only.")
        return Movie.from_disc_label(disc_label)

    # Determine initial search title
    search_title = args.movie_title or disc_label
    search_year = args.movie_year

    # --- First TMDB search ---
    print(f"\nSearching TMDB for: {search_title} ({search_year or 'unknown year'})")
    result = _search_movie(args.tmdb_key, search_title, search_year)

    if result:
        # Ask user to confirm
        print(f"\nTMDB found: {result.get('title')} ({(result.get('release_date') or '0000')[:4]})")
        print(f"Overview: {result.get('overview')}")
        confirm = input("Use this movie? [Y/n]: ").strip().lower()

        if confirm in ("", "y", "yes"):
            return _build_movie_from_tmdb(args.tmdb_key, result, disc_label)

    # --- If no match or user rejected it ---
    print("\nTMDB match not accepted or not found.")
    new_title = input("Enter a new search title (or leave blank to skip TMDB): ").strip()

    if new_title:
        print(f"\nSearching TMDB for: {new_title}")
        result = _search_movie(args.tmdb_key, new_title)

        if result:
            print(f"\nTMDB found: {result.get('title')} ({(result.get('release_date') or '0000')[:4]})")
            print(f"Overview: {result.get('overview')}")
            confirm = input("Use this movie? [Y/n]: ").strip().lower()

            if confirm in ("", "y", "yes"):
                return _build_movie_from_tmdb(args.tmdb_key, result, disc_label)

    # --- Still no match → manual entry ---
    print("\nTMDB could not find a match.")
    return _manual_movie_entry(disc_label)


def _build_movie_from_tmdb(api_key: str, result: dict, disc_label: Optional[str]) -> Movie:
    movie_id = result["id"]
    details = _fetch_movie_details(api_key, movie_id)

    title = details.get("title") or result.get("title")
    year = (details.get("release_date") or "0000")[:4]
    runtime = details.get("runtime")
    genres = [g["name"] for g in details.get("genres", [])]
    tagline = details.get("tagline")
    overview = details.get("overview")
    score = details.get("vote_average")

    credits = details.get("credits", {})
    cast = [c["name"] for c in credits.get("cast", [])[:5]]
    director = None
    for crew in credits.get("crew", []):
        if crew.get("job") == "Director":
            director = crew.get("name")
            break

    print(f"\nTMDB: Using → {title} ({year})")

    return Movie(
        title=title,
        year=year,
        runtime=runtime,
        genres=genres,
        tagline=tagline,
        overview=overview,
        score=score,
        cast=cast,
        director=director,
        disc_label=disc_label,
    )
