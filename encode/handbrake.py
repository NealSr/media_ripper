# encode/handbrake.py
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from ..models.title import Title


def encode_titles(titles: List[Title], movie, args, tui=None):
    """
    Encode ripped MKVs using HandBrakeCLI with real-time progress updates.
    """

    output_root = Path(args.output_root)
    preset = args.preset or "Fast 1080p30"

    for t in titles:
        if t.action == "skip":
            continue

        # Input file (ripped MKV)
        in_file = (
            output_root
            / movie.safe_title
            / f"{t.safe_movie_name}_{t.movie_year}_{t.bonus_display_name}_t{t.id:02d}.mkv"
        )

        # Output encoded file
        out_file = (
            output_root
            / movie.safe_title
            / f"{t.final_filename}"
        )

        if tui:
            tui.log(f"Encoding title {t.id} → {out_file}")
            tui.encode_task = None
            tui.update_encode_progress(0)

        cmd = [
            "HandBrakeCLI",
            "-i", str(in_file),
            "-o", str(out_file),
            "--preset", preset,
            "--format", "av_mkv",
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for raw in proc.stdout:
            line = raw.strip()

            # HandBrake progress lines look like:
            # Encoding: task 1 of 1, 42.35 % (xxx fps, eta 00h00m)
            if tui and "Encoding:" in line and "%" in line:
                try:
                    percent_str = line.split("%")[0].split()[-1]
                    percent = float(percent_str)
                    tui.update_encode_progress(percent)
                except Exception:
                    pass
                continue  # DO NOT LOG PROGRESS LINES

            # Log everything else
            if tui:
                tui.log(line)

        proc.wait()

        if tui:
            tui.update_encode_progress(100)
            tui.log(f"[green]Encode complete for title {t.id}[/green]")
