# classify/scorer.py
from ..models.title import Title

def score_title(t: Title, min_bonus: int, min_main: int) -> int:
    if t.audio_tracks == 0:
        return -5000
    if t.duration < min_bonus:
        return -5000

    score = 0
    if t.duration >= min_main:
        score += 2000
        score += t.duration // 60
    else:
        score += t.duration // 120

    if t.chapters >= 10:
        score += 500
    if t.chapters >= 30:
        score += 500

    score += t.audio_tracks * 200
    score += t.subtitle_tracks * 50
    return score
