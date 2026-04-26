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
    prompt_with_optional_finder,
)


def encode_titles(titles: List[Title], movie: Movie, args):
    output_root = Path(args.output_root)
    preset = args.preset or "Fast 1080p30"

    for t in titles:
        if t.action != "rip":
            continue

        in_file = output_root / movie.safe_title / t.final_filename
        out_file = output_root / movie.safe_title / t.final_filename

        print(f"\n=== ENCODE TITLE {t.id} ===")
        print(f"Input file:\n  {in_file}")
        print(f"Output file:\n  {out_file}\n")

        if not in_file.exists():
            print("❌ ERROR: Input file does not exist. Did the rip succeed?")
            prompt_with_optional_finder(in_file, "Press Enter to continue, or press O to reveal the expected input in Finder… ")
            continue

        in_size_mb = format_size_mb(in_file)
        if in_size_mb < 1:
            print(f"❌ ERROR: Input file is too small ({in_size_mb:.2f} MB).")
            prompt_with_optional_finder(in_file, "Press Enter to continue, or press O to reveal the input in Finder… ")
            continue

        cmd = (
            f'HandBrakeCLI -i "{in_file}" -o "{out_file}" '
            f'--preset "{preset}" --format av_mkv'
        )

        print("# Run this command to encode the title:")
        print(cmd)
        copy_to_clipboard(cmd)
        print("(Command copied to clipboard)\n")

        print("Waiting for you to run the command…")

        with Live(Spinner("dots", text="Encoding…"), refresh_per_second=10):
            input("Press Enter when encoding is complete… ")

        print("\nVerifying encoded output…")

        if not out_file.exists():
            print("❌ ERROR: Output file does not exist.")
            prompt_with_optional_finder(out_file)
            continue

        size_mb = format_size_mb(out_file)
        if size_mb < 1:
            print(f"❌ ERROR: Output file is too small ({size_mb:.2f} MB).")
            prompt_with_optional_finder(out_file)
            continue

        print(f"✔ Encode verified ({size_mb:.2f} MB)")
        prompt_with_optional_finder(out_file)
