# src/media_ripper/makemkv/scanner.py
from __future__ import annotations

import subprocess
from typing import List, Tuple, Optional, Dict
from rich.progress import Progress, BarColumn, TextColumn

from ..models.title import Title
from ..utils.durations import hms_to_seconds


def _normalize_device(device: str) -> str:
    if device == "auto":
        return "disc:0"
    if device.startswith("disc:"):
        return device
    if device.isdigit():
        return f"disc:{device}"
    return device


def scan_disc(device: str, minlength: int = 120) -> Tuple[List[Title], Optional[str]]:
    disc_spec = _normalize_device(device)

    cmd = [
        "makemkvcon",
        "-r",
        "--progress=-stdout",
        "info",
        disc_spec,
        f"--minlength={minlength}",
    ]

    print(f"Running: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    disc_label = None
    tinfo: Dict[int, Dict[int, str]] = {}
    sinfo: Dict[int, Dict[int, Dict[int, str]]] = {}

    with Progress(
        TextColumn("[bold blue][SCAN][/bold blue] {task.description}"),
        TextColumn("{task.fields[metrics]}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
    ) as progress:

        task = progress.add_task("Scanning disc", metrics="", total=100)

        for raw in proc.stdout:
            line = raw.strip()

            if line.startswith("PRGV:"):
                try:
                    _, rest = line.split(":", 1)
                    cur, base, maxv = [int(x) for x in rest.split(",")]
                    pct = ((cur - base) / (maxv - base)) * 100 if maxv > base else 0
                    progress.update(task, completed=pct, metrics=f"cur={cur} base={base} max={maxv}")
                except:
                    pass
                continue

            print(line)

            if line.startswith("DRV:"):
                parts = line.split(",", 5)
                if len(parts) >= 6:
                    tail = parts[5]
                    if tail.count(",") >= 1:
                        label_part = tail.rsplit(",", 1)[0]
                    else:
                        label_part = tail
                    disc_label = label_part.strip().strip('"')

            if line.startswith("TINFO:"):
                try:
                    _, rest = line.split(":", 1)
                    parts = rest.split(",", 3)
                    t_idx = int(parts[0])
                    field_id = int(parts[1])
                    value = parts[3].strip().strip('"')
                    tinfo.setdefault(t_idx, {})[field_id] = value
                except:
                    pass

            if line.startswith("SINFO:"):
                try:
                    _, rest = line.split(":", 1)
                    parts = rest.split(",", 4)
                    t_idx = int(parts[0])
                    track_idx = int(parts[1])
                    field_id = int(parts[2])
                    value = parts[4].strip().strip('"')
                    sinfo.setdefault(t_idx, {}).setdefault(track_idx, {})[field_id] = value
                except:
                    pass

    proc.wait()

    titles: List[Title] = []

    for t_idx, fields in tinfo.items():
        playlist = fields.get(16)
        name = fields.get(2) or playlist or f"Title {t_idx}"

        duration_seconds = hms_to_seconds(fields.get(9, "0:0:0"))
        if duration_seconds < minlength:
            continue

        chapters = int(fields.get(8, "0"))
        size_bytes = int(fields.get(11, "0"))
        size_mb = size_bytes // (1024 * 1024)

        audio_tracks = []
        subtitle_tracks = []

        for track_idx, tfields in sinfo.get(t_idx, {}).items():
            kind = tfields.get(1, "")
            lang = tfields.get(4, "") or tfields.get(3, "")
            desc = tfields.get(30, "")
            label = " ".join(x for x in [lang, desc] if x)

            if kind.lower() == "audio":
                audio_tracks.append(label)
            elif kind.lower() == "subtitles":
                subtitle_tracks.append(label)

        titles.append(
            Title(
                id=t_idx,
                mpls=playlist,
                duration=duration_seconds,
                chapters=chapters,
                audio_tracks=audio_tracks,
                subtitle_tracks=subtitle_tracks,
                size_mb=size_mb,
                name=name,
                source=playlist,
            )
        )

    titles.sort(key=lambda t: t.duration, reverse=True)
    return titles, disc_label
