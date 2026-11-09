"""Draw the per-city validation scores as one bar chart for the long report.

    uv run --with matplotlib python scripts/make_score_chart.py

The bars are the mean of the seeds in experiments.csv for the four Track A
recipes, which are the values in table 2 of long_report/long_report.tex. The
script prints them so they can be checked against the table. It writes
long_report/figures/per_city_scores.png and touches nothing else.

matplotlib is not one of the packages in uv.lock, so it comes in through --with
and the training environment is left as it is.
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CITIES = ["seoul", "busan", "tokyo", "osaka", "taipei"]
TAGS = ["baseline", "street", "drop_street", "balanced"]
OUT = ROOT / "long_report" / "figures" / "per_city_scores.png"


def korean_font():
    """A font that has the Korean in the axis label, or None."""
    for name in ("AppleGothic", "Apple SD Gothic Neo", "Noto Sans CJK KR", "NanumGothic"):
        try:
            font_manager.findfont(name, fallback_to_default=False)
            return name
        except Exception:
            continue
    return None


def means():
    """{(tag, city): mean over the seeds}, from experiments.csv."""
    rows = list(csv.DictReader((ROOT / "experiments.csv").open(encoding="utf-8")))
    values = defaultdict(list)
    for row in rows:
        if row["track"] == "A" and row["tag"] in TAGS:
            for city in CITIES:
                values[(row["tag"], city)].append(float(row[city]))
    return {key: sum(v) / len(v) for key, v in values.items()}


def main():
    data = means()
    for city in CITIES:
        print(f"{city:7s} " + "  ".join(f"{tag} {data[(tag, city)]:.4f}" for tag in TAGS))

    font = korean_font()
    if font:
        plt.rcParams["font.family"] = font
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    width = 0.8 / len(TAGS)
    for i, tag in enumerate(TAGS):
        xs = [p + (i - (len(TAGS) - 1) / 2) * width for p in range(len(CITIES))]
        ax.bar(xs, [data[(tag, c)] for c in CITIES], width=width * 0.92, label=tag)

    ax.set_ylim(0.30, 0.68)
    ax.set_ylabel("검증 점수", fontsize=9, labelpad=12)
    ax.tick_params(labelsize=9)
    ax.set_xticks(range(len(CITIES)))
    ax.set_xticklabels(CITIES)
    ax.yaxis.grid(True, color="0.85", linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=len(TAGS),
              frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT, dpi=200)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()