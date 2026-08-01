"""Pinned public-data downloader with provenance and checksum recording."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import requests


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    required = {"filename", "download_url", "role", "required"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Manifest must contain columns: {sorted(required)}")
    return rows


def _looks_like_fits(path: Path) -> bool:
    with path.open("rb") as stream:
        return stream.read(9).startswith(b"SIMPLE")


def download_manifest(
    manifest_path: Path,
    output_dir: Path,
    *,
    include_optional: bool = False,
    timeout_s: int = 120,
) -> list[dict[str, object]]:
    """Download pinned MAST products and write a local inventory.

    Raw FITS products remain outside Git. The inventory records exact byte sizes,
    SHA-256 hashes, URLs, and roles for reproducibility.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory: list[dict[str, object]] = []

    for row in read_manifest(manifest_path):
        required = row["required"].strip().lower() in {"1", "true", "yes"}
        if not required and not include_optional:
            continue

        destination = output_dir / row["filename"]
        if not destination.exists():
            partial = destination.with_suffix(destination.suffix + ".part")
            with requests.get(row["download_url"], stream=True, timeout=timeout_s) as response:
                response.raise_for_status()
                with partial.open("wb") as stream:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            stream.write(chunk)
            partial.replace(destination)

        if not _looks_like_fits(destination):
            raise RuntimeError(f"Downloaded file is not a FITS primary HDU: {destination}")

        inventory.append(
            {
                "filename": destination.name,
                "bytes": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "role": row["role"],
                "data_uri": row.get("data_uri", ""),
                "download_url": row["download_url"],
            }
        )

    inventory_path = output_dir / "inventory.json"
    inventory_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    return inventory
