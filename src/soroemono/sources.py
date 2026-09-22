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


def source_paths(root: Path) -> dict[str, Path]:
    return {
        key: verified(root / spec["path"], spec["sha256"])
        for key, spec in lock(root)["fonts"].items()
    }


def baseline_path(root: Path) -> Path:
    spec = lock(root)["baseline"]
    path = root / ".cache" / "baseline" / spec["member"]
    if not path.exists():
        raise FileNotFoundError("Baseline missing. Run: soroemono fetch-baseline")
    return verified(path, spec["sha256"])


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
    if digest(font) != spec["sha256"]:
        raise ValueError("Baseline font SHA-256 mismatch")
    path = root / ".cache" / "baseline" / spec["member"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(font)
    return path
