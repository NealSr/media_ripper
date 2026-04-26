import argparse

def parse_args():
    p = argparse.ArgumentParser(description="Media Ripper (Manual Mode Only)")

    p.add_argument("--device", default="auto", help="Disc device (default: auto)")
    p.add_argument("--output-root", required=True, help="Output directory")
    p.add_argument("--preset", default="Fast 1080p30", help="HandBrake preset")

    p.add_argument("--movie-title", help="Movie title override")
    p.add_argument("--movie-year", type=int, help="Movie year override")
    p.add_argument("--tmdb-key", help="TMDB API key")

    return p.parse_args()
