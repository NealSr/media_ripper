from .cli import parse_args
from .makemkv.scanner import scan_disc
from .picker.picker import pick_titles
from .makemkv.ripper import rip_titles
from .encode.handbrake import encode_titles
from .tmdb.client import fetch_movie_metadata


def main():
    args = parse_args()

    print("\n=== Scanning Disc ===")
    titles, disc_label = scan_disc(args.device)

    print("\n=== Selecting Titles ===")
    movie = fetch_movie_metadata(args, disc_label)
    selected = pick_titles(titles, movie, args)

    print("\n=== Manual Rip Phase ===")
    rip_titles(selected, movie, args)

    print("\n=== Manual Encode Phase ===")
    encode_titles(selected, movie, args)

    print("\n=== Done ===")

if __name__ == "__main__":
    main()
