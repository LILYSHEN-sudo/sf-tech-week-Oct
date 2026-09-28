#!/usr/bin/env python3
"""Add the Creator audience where the slim dataset has the Creators theme."""

from __future__ import annotations

import json
from pathlib import Path

from audience_labels import format_audience, parse_audience


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"


def split_labels(value: str) -> list[str]:
    return [label.strip() for label in (value or "").split(";") if label.strip()]


def main() -> None:
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    matched = 0
    added = 0
    for row in rows:
        if "Creators" not in split_labels(row.get("themes", "")):
            continue
        matched += 1
        audience = parse_audience(row.get("audience_inferred", ""))
        if "Creator" not in audience:
            audience.add("Creator")
            row["audience_inferred"] = format_audience(audience)
            added += 1

    DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rows: {len(rows)}; Creators theme: {matched}; Creator audience added: {added}")


if __name__ == "__main__":
    main()
