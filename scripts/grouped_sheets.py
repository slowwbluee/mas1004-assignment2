"""Sheets of whole bundles: one YouTube video, or one Commons uploader, per sheet.

A video's frames and one uploader's photos come in bundles, so deciding about
one bundle decides a hundred photos at once. This script draws one sheet per
bundle, biggest bundles first, with the video title or the uploader name as the
caption.

    uv run python scripts/grouped_sheets.py                      every city, biggest first
    uv run python scripts/grouped_sheets.py --city busan          one city
    uv run python scripts/grouped_sheets.py --source youtube      videos only
    uv run python scripts/grouped_sheets.py --min-photos 50       only the biggest bundles

The sheets go to results/curate/ as grp_<city>_<source>_<rank>_00.png, with the
same .csv that src/curate.py writes, so a photo can be dropped by number:

    uv run python src/curate.py drop grp_busan_youtube_01_00 3 17 44 --reason "..."

A bundle bigger than one sheet is sampled evenly over the whole bundle, and
each sheet gets a .paths.txt naming every photo in the bundle, so a whole
bundle can be dropped as well:

    uv run python src/curate.py drop $(cat results/curate/grp_busan_youtube_01_00.paths.txt) --reason "..."

results/curate/grp_index.csv lists every bundle with its sheet, size and the
number of photos drawn, biggest first. Nothing here changes the selection:
`curate.py drop` does that, and only for the photos you name.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import curate  # noqa: E402  # its OUT, TILE, COLS, ROWS and path_name keep the sheets compatible
import rules  # noqa: E402

ATTRIBUTION = ROOT / "data" / "starter" / "ATTRIBUTION.csv"
TRAIN = ROOT / "data" / "starter" / "train"
SOURCES = ("youtube", "commons")
VIDEO = re.compile(r"^youtube_(.+)_\d+\.jpg$")
FRAME_TIME = re.compile(r"\s+at\s+\d+\s*s$")
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u20E3]+")
# A font with Hangul and kana, so a Korean or Japanese title is readable.
FONTS = ["/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
         "/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/Arial Unicode.ttf",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "C:/Windows/Fonts/malgun.ttf"]
CAPTION_HEIGHT = 22
HEADER = 26


def clean(text):
    """A title without emoji or runs of spaces: this font has no emoji, they only make boxes."""
    text = EMOJI.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_bundles():
    """(city, source, bundle, caption) -> [path relative to the training folder], from ATTRIBUTION.csv."""
    groups = {}
    with open(ATTRIBUTION, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["split"] != "train":
                continue
            path = row["file"].split("/", 1)[1]
            name = path.split("/")[-1]
            if row["source"] == "youtube":
                match = VIDEO.match(name)
                bundle = match.group(1) if match else name
                caption = clean(FRAME_TIME.sub("", row["title"])) or bundle
            elif row["source"] == "commons":
                bundle = caption = clean(row["group"]) or "unknown uploader"
            else:
                continue
            groups.setdefault((row["city"], row["source"], bundle, caption), []).append(path)
    return groups


def sampled(paths, tiles):
    """At most tiles photos, evenly spread over the bundle, first and last included."""
    if len(paths) <= tiles:
        return list(paths)
    step = (len(paths) - 1) / (tiles - 1)
    return [paths[round(i * step)] for i in range(tiles)]


def caption_font(size=11):
    for path in FONTS:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def shortened(text, font, width):
    """text with an ellipsis, narrow enough to fit in width pixels."""
    if font.getlength(text) <= width:
        return text
    while text and font.getlength(text + "...") > width:
        text = text[:-1]
    return text + "..."


def draw_sheet(name, items, header, small, big):
    """One sheet of (path, caption) pairs, laid out as src/curate.py lays out its own."""
    curate.OUT.mkdir(parents=True, exist_ok=True)
    width = curate.COLS * curate.TILE
    sheet = Image.new("RGB", (width, HEADER + curate.ROWS * (curate.TILE + CAPTION_HEIGHT)), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((6, 7), shortened(header, big, width - 12), fill="black", font=big)
    draw.line([0, HEADER - 1, width, HEADER - 1], fill="black")
    for k, (path, caption) in enumerate(items):
        x = (k % curate.COLS) * curate.TILE
        y = HEADER + (k // curate.COLS) * (curate.TILE + CAPTION_HEIGHT)
        try:
            image = rules.load_photo(path)
            image.thumbnail((curate.TILE - 4, curate.TILE - 4))
            sheet.paste(image, (x + (curate.TILE - image.width) // 2,
                                y + (curate.TILE - image.height) // 2))
        except OSError:
            draw.text((x + 10, y + 90), "unreadable", fill="red")
        draw.rectangle([x + 2, y + 2, x + 30, y + 18], fill="black")
        draw.text((x + 5, y + 4), str(k + 1), fill="white")
        draw.text((x + 4, y + curate.TILE + 4), shortened(caption, small, curate.TILE - 6),
                  fill="black", font=small)
    sheet.save(curate.OUT / f"{name}.png")
    with open(curate.OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["number", "path", "caption"])
        for k, (path, caption) in enumerate(items):
            writer.writerow([k + 1, curate.path_name(path), caption])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", choices=rules.CITIES, help="one city only, the default is all of them")
    ap.add_argument("--source", choices=SOURCES, help="one source only, the default is both")
    ap.add_argument("--min-photos", type=int, default=20, help="leave out bundles smaller than this")
    ap.add_argument("--tiles", type=int, default=curate.COLS * curate.ROWS, help="photos drawn per sheet")
    args = ap.parse_args()

    groups = read_bundles()
    small, big = caption_font(11), caption_font(15)
    index = []
    for city in [args.city] if args.city else rules.CITIES:
        for source in [args.source] if args.source else SOURCES:
            mine = [(key, paths) for key, paths in groups.items()
                    if key[0] == city and key[1] == source and len(paths) >= args.min_photos]
            mine.sort(key=lambda kv: (-len(kv[1]), kv[0][2]))
            if not mine:
                continue
            print(f"\n{city}, {source}: {len(mine)} bundles of {args.min_photos} or more photos,"
                  f" {sum(len(p) for _, p in mine)} photos, biggest first")
            for rank, (key, paths) in enumerate(mine, start=1):
                name = f"grp_{city}_{source}_{rank:02d}_00"
                caption = clean(key[3])
                paths = sorted(paths)
                shown = sampled(paths, args.tiles)
                header = (f"{name} | {caption} | {len(shown)} of {len(paths)} photos"
                          f" | {source} {key[2]}")
                draw_sheet(name, [(TRAIN / p, caption) for p in shown], header, small, big)
                with open(curate.OUT / f"{name}.paths.txt", "w", encoding="utf-8") as f:
                    f.write("".join(p + "\n" for p in paths))
                index.append([name, city, source, key[2], key[3], len(paths), len(shown)])
                print(f"  {name}  {key[3][:44]:44s} {len(shown):3d} of {len(paths):4d} photos")
    if not index:
        print(f"no bundle has {args.min_photos} photos; try a smaller --min-photos")
        return
    scope = "_".join(part for part in (args.city, args.source) if part)
    index_path = curate.OUT / (f"grp_index_{scope}.csv" if scope else "grp_index.csv")
    with open(index_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sheet", "city", "source", "bundle", "caption", "photos", "on_sheet"])
        writer.writerows(index)
    print(f"\n{len(index)} sheets in {curate.OUT} ({index_path.name} lists them, biggest first)."
          f"\nDrop the photos you name by sheet and number, for example:"
          f"\n  uv run python src/curate.py drop {index[0][0]} 3 17 --reason \"...\"")


if __name__ == "__main__":
    main()