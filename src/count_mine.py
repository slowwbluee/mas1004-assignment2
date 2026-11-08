"""Say how many of your own photos in data/mine are used, city by city.

    python src/count_mine.py
    python src/count_mine.py data/mine

train_b.py takes the photos with rules.list_photos, the same list this counts:
files with a photo suffix inside a <city>/ folder. Anything else in the folder,
for example .DS_Store, is named at the end so it is clear it was not used.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rules  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", nargs="?", default=str(ROOT / "data" / "mine"),
                    help="the folder with <city>/ subfolders (default: data/mine)")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        raise SystemExit(f"{folder} is not a folder: there are no photos of your own to add.")
    rows = rules.list_photos(folder)
    counts = {c: sum(1 for _, city in rows if city == c) for c in rules.CITIES}
    print(f"{folder}: {len(rows)} photos ("
          + ", ".join(f"{c} {n}" for c, n in counts.items()) + ")")

    for d in sorted(folder.iterdir()):
        if d.is_dir() and d.name.lower() not in rules.CITIES:
            print(f"  {d.name}/ is not one of the five cities ({', '.join(rules.CITIES)}); "
                  f"nothing in it is used")
    others = [p.relative_to(folder).as_posix() for p in sorted(folder.rglob("*"))
              if p.is_file() and p.suffix.lower() not in rules.IMAGE_SUFFIXES]
    if others:
        listed = ", ".join(others[:10])
        if len(others) > 10:
            listed += f", and {len(others) - 10} more"
        print(f"  not photos, so not used: {len(others)} ({listed})")
    else:
        print("  every file in it is a photo")


if __name__ == "__main__":
    main()