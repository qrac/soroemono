"""Locked, read-only inputs. Network access is confined to fetch_baseline."""

import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verified(path: Path, expected: str) -> Path:
    if digest(path.read_bytes()) != expected:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return path


def lock(root: Path) -> dict:
    return json.loads((root / "sources.lock.json").read_text())


def source_paths(root: Path, style: str = "Regular") -> dict[str, Path]:
    if style not in {"Regular", "Bold"}:
        raise ValueError(f"Unsupported style: {style}")
    key = "fonts" if style == "Regular" else "bold_fonts"
    return {
        key: verified(root / spec["path"], spec["sha256"])
        for key, spec in lock(root)[key].items()
    }


def baseline_path(root: Path, style: str = "Regular") -> Path:
    if style not in {"Regular", "Bold"}:
        raise ValueError(f"Unsupported style: {style}")
    spec = lock(root)["baseline"]
    member = spec["member"] if style == "Regular" else spec["bold_member"]
    expected = spec["sha256"] if style == "Regular" else spec["bold_sha256"]
    path = root / ".cache" / "baseline" / member
    if not path.exists():
        raise FileNotFoundError("Baseline missing. Run: soroemono fetch-baseline")
    return verified(path, expected)


def fetch_baseline(root: Path, archive: Path | None = None) -> Path:
    spec = lock(root)["baseline"]
    if archive is not None:
        data = archive.read_bytes()
    else:
        with urllib.request.urlopen(spec["url"], timeout=60) as response:
            data = response.read()
    if digest(data) != spec["archive_sha256"]:
        raise ValueError("Baseline archive SHA-256 mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        font = zf.read(spec["member"])
        bold = zf.read(spec["bold_member"])
    if digest(font) != spec["sha256"]:
        raise ValueError("Baseline font SHA-256 mismatch")
    if digest(bold) != spec["bold_sha256"]:
        raise ValueError("Baseline Bold font SHA-256 mismatch")
    path = root / ".cache" / "baseline" / spec["member"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(font)
    (path.parent / spec["bold_member"]).write_bytes(bold)
    return path
