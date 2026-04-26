# makemkv/scanner.py
from __future__ import annotations

import subprocess
from typing import List, Tuple, Dict, Optional

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


def _run_makemkv_info(device: str, minlength: int, tui=None):
    disc_spec = _normalize_device(device)

    cmd = [
        "makemkvcon",
        "-r",
        "--progress=-stdout",
        "info",
        disc_spec,
        f"--minlength={minlength}",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    if tui:
        tui.log(f"Running: {' '.join(cmd)}")

    for raw in proc.stdout:
        line = raw.strip()

        # Progress updates
        if tui and line.startswith("PRGV:"):
            try:
                _, rest = line.split(":", 1)
                cur, base, maxv = [int(x) for x in rest.split(",")]
                if maxv > base:
                    percent = ((cur - base) / (maxv - base)) * 100
                    tui.update_scan_progress(percent)
            except Exception:
                pass
            continue  # DO NOT LOG PRGV LINES

        yield line

    proc.wait()


def scan_disc(device: str, tui=None, minlength: int = 120) -> Tuple[List[Title], Optional[str]]:
    if tui:
        tui.log(f"Starting MakeMKV scan on {device}")

    disc_label: Optional[str] = None
    tinfo: Dict[int, Dict[int, str]] = {}
    sinfo: Dict[int, Dict[int, Dict[int, str]]] = {}

    for line in _run_makemkv_info(device, minlength=minlength, tui=tui):
        # Log non-progress lines
        if not (line.startswith("PRGV:") or line.startswith("TINFO:") or line.startswith("SINFO:")) and tui:
            tui.log(line)

        # Disc label
        if line.startswith("DRV:"):
            parts = line.split(",", 5)
            if len(parts) >= 6:
                tail = parts[5]
                if tail.count(",") >= 1:
                    label_part = tail.rsplit(",", 1)[0]
                else:
                    label_part = tail
                label_part = label_part.strip().strip('"')
                if label_part:
                    disc_label = label_part

        # TINFO
        if line.startswith("TINFO:"):
            try:
                _, rest = line.split(":", 1)
                parts = rest.split(",", 3)
                if len(parts) < 4:
                    continue
                t_idx = int(parts[0])
                field_id = int(parts[1])
                value = parts[3].strip().strip('"')
            except Exception:
                continue

            tinfo.setdefault(t_idx, {})[field_id] = value

        # SINFO
        if line.startswith("SINFO:"):
            try:
                _, rest = line.split(":", 1)
                parts = rest.split(",", 4)
                if len(parts) < 5:
                    continue
                t_idx = int(parts[0])
                track_idx = int(parts[1])
                field_id = int(parts[2])
                value = parts[4].strip().strip('"')
            except Exception:
                continue

            sinfo.setdefault(t_idx, {}).setdefault(track_idx, {})[field_id] = value

    titles: List[Title] = []

    for t_idx, fields in tinfo.items():
        playlist = None
        if 16 in fields and fields[16].lower().endswith(".mpls"):
            playlist = fields[16]
        else:
            for v in fields.values():
                lv = v.lower()
                if lv.endswith(".mpls") or lv.endswith(".ifo"):
                    playlist = v
                    break

        name = fields.get(2) or fields.get(27) or playlist or f"Title {t_idx}"

        duration_seconds = 0
        if 9 in fields:
            duration_seconds = hms_to_seconds(fields[9])
        elif 30 in fields:
            duration_seconds = hms_to_seconds(fields[30])

        chapters = 0
        if 8 in fields:
            chapters = int(fields[8]) if fields[8].isdigit() else 0
        elif 25 in fields:
            chapters = int(fields[25]) if fields[25].isdigit() else 0

        size_bytes = int(fields.get(11, 0)) if fields.get(11, "").isdigit() else 0
        size_mb = size_bytes // (1024 * 1024)

        if duration_seconds < minlength:
            continue

        audio_tracks = []
        subtitle_tracks = []

        for track_idx, tfields in sinfo.get(t_idx, {}).items():
            kind = tfields.get(1, "")
            lang_code = tfields.get(3, "")
            lang_name = tfields.get(4, "")
            desc = tfields.get(30, "") or tfields.get(7, "")

            label_parts = []
            if lang_name:
                label_parts.append(lang_name)
            elif lang_code:
                label_parts.append(lang_code)
            if desc:
                label_parts.append(desc)

            label = " ".join(label_parts) if label_parts else kind or f"Track {track_idx}"

            if kind.lower() == "audio":
                audio_tracks.append(label)
            elif kind.lower() == "subtitles":
                subtitle_tracks.append(label)

        title = Title(
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

        titles.append(title)

    titles.sort(key=lambda t: t.duration, reverse=True)

    if tui:
        tui.update_scan_progress(100)
        tui.log(f"Scan complete. Found {len(titles)} titles.")

    return titles, disc_label
