"""Create a reproducible, verified 2.0.0 distribution without publishing it."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from .builder import STYLES, build
from .sources import digest
from .validation import check

VERSION = "2.0.0"
ARCHIVE = f"SOROEMONO_v{VERSION}.zip"
ZIP_TIME = (2024, 8, 13, 0, 0, 0)


def _zip_entry(name: str, data: bytes, archive: ZipFile) -> None:
    info = ZipInfo(name, ZIP_TIME)
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data, compresslevel=9)


def release_package(root: Path, output_dir: Path | None = None) -> Path:
    """Build twice, validate every style, then atomically place the ZIP."""
    output_dir = output_dir or root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="soroemono-release-", dir=output_dir) as temp:
        work = Path(temp)
        files: dict[str, bytes] = {}
        for style in STYLES:
            first = build(root, work / "first", style)
            second = build(root, work / "second", style)
            if first.read_bytes() != second.read_bytes():
                raise ValueError(f"Non-reproducible build: {style}")
            result = check(root, first, style)
            files[first.name] = first.read_bytes()
            slug = style.lower().replace(" ", "-")
            files[f"reports/build-{slug}.json"] = (work / "first" / f"build-{slug}.json").read_bytes()
            files[f"reports/checks-{slug}.json"] = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
        for source in ("JetBrainsMono", "BIZUDGothic"):
            files[f"licenses/OFL-{source}.txt"] = (root / "resource" / source / "OFL.txt").read_bytes()
        files["sources.lock.json"] = (root / "sources.lock.json").read_bytes()
        files["README.txt"] = (
            "SOROEMONO 2.0.0\n\n"
            "JetBrains Mono 2.304とBIZ UDGothic 1.051を組み合わせたエディタ用フォント。\n"
            "Regular、Bold、Italic、Bold Italicの4つの静的TTFを収録しています。\n"
            "4ファイルをインストールし、アプリのフォントファミリーにSOROEMONOを指定してください。\n"
            "v1.0.0から更新するときは旧版を削除してからインストールし、アプリを再起動してください。\n"
            "Italic系の欧文はJetBrains Mono純正、日本語は9度の機械的な斜体です。\n"
            "licenses/には両元フォントのOFL、sources.lock.jsonには入力版とハッシュを収録しています。\n"
            "reports/には生成と数値検査の結果を収録しています。Windows実アプリの受け入れは別途必要です。\n"
        ).encode("utf-8")
        files["SHA256SUMS"] = "".join(
            f"{digest(data)}  {name}\n" for name, data in sorted(files.items())
        ).encode("ascii")
        target = output_dir / ARCHIVE
        staged = work / ARCHIVE
        with ZipFile(staged, "w") as archive:
            for name, data in sorted(files.items()):
                _zip_entry(name, data, archive)
        staged.replace(target)
        (output_dir / f"{ARCHIVE}.sha256").write_text(f"{digest(target.read_bytes())}  {ARCHIVE}\n")
        return target
