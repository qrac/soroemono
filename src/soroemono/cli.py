"""Local build and proof commands. No OS font installation."""

import argparse
import json
from pathlib import Path

from .builder import FILENAME, build
from .sources import fetch_baseline
from .validation import check


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build").add_argument("--output", type=Path)
    sub.add_parser("check").add_argument("--font", type=Path)
    sub.add_parser("fetch-baseline").add_argument("--archive", type=Path)
    proof = sub.add_parser("proof")
    proof.add_argument("--font", type=Path)
    proof.add_argument("--output", type=Path)
    capture = sub.add_parser("capture")
    capture.add_argument("--proof", type=Path)
    capture.add_argument("--channel", help="Installed browser channel, e.g. chrome; default: Playwright Chromium")
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / "sources.lock.json").exists():
        parser.error("Run from the repository root, or pass --root")
    font = getattr(args, "font", None) or root / "build" / "preview" / FILENAME
    try:
        if args.command == "build":
            print(build(root, args.output))
        elif args.command == "check":
            result = check(root, font)
            (font.parent / "checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "fetch-baseline":
            print(fetch_baseline(root, args.archive))
        elif args.command == "proof":
            from .proof import make_proof
            print(make_proof(root, font, args.output))
        elif args.command == "capture":
            from .capture import capture_proof
            print(capture_proof(args.proof or root / "build" / "proofs" / "regular", args.channel))
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
