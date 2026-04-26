# makemkv/ripper.py
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from ..models.title import Title


def rip_titles(titles: List[Title], movie, args, tui=None):
    """
    Rip selected titles using MakeMKV.
    """

    output_root = Path(args.output_root)
    disc_spec = args.device if args.device != "auto" else "disc:0"

    for t in titles:
        if t.action == "skip":
            continue

        out_dir = output_root / movie.safe_title
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / f"{t.safe_movie_name}_{t.movie_year}_{t.bonus_display_name}_t{t.id:02d}.mkv"

        if tui:
            tui.log(f"Ripping title {t.id} → {out_file}")
            tui.rip_task = None
            tui.update_rip_progress(0)

        cmd = [
            "makemkvcon",
            "-r",
            "--progress=-stdout",
            "mkv",
            disc_spec,
            str(t.id),
            str(out_dir),
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

            # Progress lines
            if tui and line.startswith("PRGV:"):
                try:
                    _, rest = line.split(":", 1)
                    cur, base, maxv = [int(x) for x in rest.split(",")]
                    if maxv > base:
                        percent = ((cur - base) / (maxv - base)) * 100
                        tui.update_rip_progress(percent)
                except Exception:
                    pass
                continue  # DO NOT LOG PRGV LINES

            # Log everything else
            if tui:
                tui.log(line)

        proc.wait()

        if tui:
            tui.update_rip_progress(100)
            tui.log(f"[green]Rip complete for title {t.id}[/green]")
