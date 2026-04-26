from __future__ import annotations

from pathlib import Path
from typing import List
from rich.spinner import Spinner
from rich.live import Live

from ..models.title import Title
from ..models.movie import Movie
from ..utils.utils import (
    copy_to_clipboard,
    format_size_mb,
    wait_for_temp_file_to_stabilize,
    prompt_with_optional_finder,
)


def rip_titles(titles: List[Title], movie: Movie, args):
    output_root = Path(args.output_root)
    disc_spec = args.device if args.device != "auto" else "disc:0"

    for t in titles:
        if t.action != "rip":
            continue

        out_dir = output_root / movie.safe_title
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / t.final_filename

        print(f"\n=== RIP TITLE {t.id} ===")
        print(f"Output file will be:\n  {out_file}\n")

        cmd = f'makemkvcon mkv {disc_spec} {t.id} "{out_dir}"'

        print("# Run this command to rip the title:")
        print(cmd)
        copy_to_clipboard(cmd)
        print("(Command copied to clipboard)\n")

        print("Waiting for you to run the command…")

        with Live(Spinner("dots", text="Ripping…"), refresh_per_second=10):
            input("Press Enter when the rip has started… ")

        # Wait for temp file to stabilize
        wait_for_temp_file_to_stabilize(interval_seconds=2.0, checks=3)

        input("Press Enter when you believe the rip is complete… ")

        print("\nVerifying rip output…")

        if not out_file.exists():
            print("❌ ERROR: Output file does not exist.")
            prompt_with_optional_finder(out_file)
            continue

        size_mb = format_size_mb(out_file)
        if size_mb < 1:
            print(f"❌ ERROR: Output file is too small ({size_mb:.2f} MB).")
            prompt_with_optional_finder(out_file)
            continue

        print(f"✔ Rip verified ({size_mb:.2f} MB)")
        prompt_with_optional_finder(out_file)
