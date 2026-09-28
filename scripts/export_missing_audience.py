#!/usr/bin/env python3
"""Export slim events without an audience label for manual review."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"
TARGETS = (
    ROOT / "analysis/audience-intent-analysis/missing.json",
    ROOT / "analysis/audience-intent-analysis/audience-unlabeled.json",
)


def main() -> None:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    missing = [row for row in rows if not (row.get("audience_inferred") or "").strip()]
    payload = json.dumps(missing, ensure_ascii=False, indent=2) + "\n"
    for target in TARGETS:
        target.write_text(payload, encoding="utf-8")
    print(f"exported {len(missing)} of {len(rows)} events to {TARGETS[0]} and {TARGETS[1]}")


if __name__ == "__main__":
    main()
