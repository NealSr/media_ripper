# classify/classifier.py
from ..models.title import Title
from .scorer import score_title
from ..utils.logging import info

def classify_titles(
    titles: list[Title],
    min_bonus: int,
    max_bonus: int,
    min_main: int,
):
    for t in titles:
        t.score = score_title(t, min_bonus, min_main)

    best = max(titles, key=lambda t: t.score)
    info(f"Best title score: {best.score} (id={best.id})")

    main: list[Title] = []
    bonus: list[Title] = []
    junk: list[Title] = []

    for t in titles:
        if t is best:
            t.classification = "main"
            main.append(t)
        elif t.duration >= min_main and t.score >= best.score * 0.85:
            t.classification = "main"
            main.append(t)
        elif min_bonus <= t.duration <= max_bonus:
            t.classification = "bonus"
            bonus.append(t)
        else:
            t.classification = "junk"
            junk.append(t)

    info(f"Classification: {len(main)} main, {len(bonus)} bonus, {len(junk)} junk")
    return main, bonus, junk
