from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Optional, Iterable
import glob
import os


def copy_to_clipboard(command: str) -> None:
    try:
        proc = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            text=True,
        )
        proc.communicate(command)
    except Exception:
        pass


def reveal_in_finder(path: Path) -> None:
    try:
        subprocess.Popen(["open", "-R", str(path)])
    except Exception:
        pass


def format_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def find_latest_makemkv_temp() -> Optional[Path]:
    candidates: list[Path] = []

    # CLI temp: /private/var/folders/**/T/makemkv_*.tmp
    for pattern in [
        "/private/var/folders/*/*/*/T/makemkv_*.tmp",
        "/private/var/folders/*/*/T/makemkv_*.tmp",
    ]:
        for p in glob.glob(pattern):
            candidates.append(Path(p))

    # GUI temp: ~/Library/MakeMKV/*
    gui_dir = Path.home() / "Library" / "MakeMKV"
    if gui_dir.exists():
        for p in gui_dir.glob("**/*"):
            if p.is_file():
                candidates.append(p)

    if not candidates:
        return None

    return max(candidates, key=lambda p: p.stat().st_mtime)


def wait_for_temp_file_to_stabilize(interval_seconds: float = 2.0, checks: int = 3) -> None:
    """
    Poll the latest MakeMKV temp file and wait until its size stops changing.
    """
    stable_count = 0
    last_size = None

    while True:
        temp = find_latest_makemkv_temp()
        if temp is None:
            # Nothing to watch; just return.
            return

        try:
            size = temp.stat().st_size
        except FileNotFoundError:
            return

        if last_size is not None and size == last_size:
            stable_count += 1
        else:
            stable_count = 0

        last_size = size

        if stable_count >= checks:
            return

        print("⚠️  MakeMKV temp file still growing — rip may not be finished.")
        time.sleep(interval_seconds)


def prompt_with_optional_finder(path: Path, message: str = "Press Enter to continue, or press O to reveal the file in Finder… ") -> None:
    while True:
        resp = input(message).strip().lower()
        if resp == "":
            return
        if resp == "o":
            reveal_in_finder(path)
        else:
            return
