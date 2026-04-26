from __future__ import annotations

from typing import List
from ..models.title import Title
from ..models.movie import Movie


def pick_titles(titles: List[Title], movie: Movie, args):
    print("\nAvailable Titles:")

    if titles:
        longest = max(titles, key=lambda t: t.duration)
        longest.is_main = True

    for t in titles:
        if not t.is_main:
            t.is_bonus = True

    for t in titles:
        label = "MAIN" if t.is_main else "BONUS"
        mins = t.duration // 60
        print(f"{t.id}: {t.name} ({mins} min) [{label}]")

    print("\nEnter title IDs to rip (comma-separated), or 'all':")
    choice = input("> ").strip()

    if choice.lower() == "all":
        selected = titles
    else:
        ids = {int(x.strip()) for x in choice.split(",") if x.strip()}
        selected = [t for t in titles if t.id in ids]

    for t in selected:
        t.action = "rip"
        t.movie_title = movie.title
        t.movie_year = movie.year

    return selected
