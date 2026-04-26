# cli.py
import argparse
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(
        prog="bluray-workflow",
        description="Blu-ray rip · encode · organize pipeline",
    )

    p.add_argument("-t", "--tmdb-key", help="TMDB API key", required=False)
    p.add_argument("-d", "--device", help="Disc device or index", default="auto")
    p.add_argument("-p", "--preset", help="HandBrake preset name (required if no --preset-file)")
    p.add_argument("-f", "--preset-file", type=Path, help="HandBrake preset JSON file", default=Path.home() / "Media" / "M5_HEVC_HQ_10bit.json")
    p.add_argument("-o", "--output-root", type=Path, default=Path.home() / "Media")
    p.add_argument("-m", "--movie-title", help="Override movie title")
    p.add_argument("-y", "--movie-year", help="Override movie year")
    p.add_argument("--min-bonus-secs", type=int, default=30)
    p.add_argument("--max-bonus-secs", type=int, default=5400)
    p.add_argument("--min-main-secs", type=int, default=3600)
    p.add_argument("-n", "--dry-run", action="store_true")
    p.add_argument("-r", "--rip-only", action="store_true")
    p.add_argument("-e", "--encode-only", action="store_true")
    p.add_argument("-i", "--input-dir", type=Path, help="Input MKV dir for encode-only")

    args = p.parse_args()

    if args.encode_only and not args.input_dir:
        p.error("encode-only mode requires --input-dir")

    return args
