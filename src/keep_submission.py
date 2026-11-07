"""Keep one Track B submission under its tag, so two runs of one session both come back.

`train_b.py --submit` always writes submission/model.onnx and submission/submission.json,
so a second run on the same machine replaces the first. `src/colab.py pack` packs
submission/ as it is at the end of the session and leaves the models in results/
behind, so this copies the two files to submission/<tag>/ right after each run:

    python src/train_b.py --tag b_starter --submit
    python src/check_submission.py --no-val
    python src/keep_submission.py --tag b_starter

After that, from_colab.zip holds submission/b_starter/model.onnx and
submission/b_starter/submission.json, and a release is made from those two files.
It refuses to file a submission that is not the one results/<tag>/ describes, so a
stale or mixed-up submission cannot be handed in under the wrong tag.
"""

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"
FILES = ("model.onnx", "submission.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True, help="the run this submission belongs to, as in results/<tag>")
    args = ap.parse_args()

    missing = [f"submission/{n}" for n in FILES if not (SUBMISSION / n).is_file()]
    if missing:
        raise SystemExit(f"{', '.join(missing)} is missing: run train_b.py --submit first")

    described = ROOT / "results" / args.tag / "submission.json"
    if not described.is_file():
        raise SystemExit(f"results/{args.tag}/submission.json is missing: was train_b.py run with --tag {args.tag}?")
    if described.read_bytes() != (SUBMISSION / "submission.json").read_bytes():
        raise SystemExit(f"submission/ does not describe run {args.tag}: run train_b.py --tag {args.tag} "
                         f"--submit again, and keep the submission before the next run")

    out = SUBMISSION / args.tag
    out.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy(SUBMISSION / name, out / name)
    mb = (out / "model.onnx").stat().st_size / 1e6
    print(f"kept submission/{args.tag}/: model.onnx {mb:.1f} MB and submission.json")


if __name__ == "__main__":
    main()