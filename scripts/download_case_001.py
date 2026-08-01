#!/usr/bin/env python3
"""Download the pinned public products for Case 001."""

from pathlib import Path

from brooks_cases.download import download_manifest

CASE_DIR = Path("cases/001_wfc3_ir_ramp_anomaly")


def main() -> None:
    inventory = download_manifest(
        CASE_DIR / "data" / "manifest.csv",
        CASE_DIR / "data" / "raw",
        include_optional=True,
        timeout_s=300,
    )
    for item in inventory:
        print(f"{item['filename']}: {item['bytes']} bytes, sha256={item['sha256']}")


if __name__ == "__main__":
    main()
