#!/usr/bin/env python3
"""Export events without an inferred intent for manual review."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"
TARGET = ROOT / "analysis/audience-intent-analysis/intent-missing.json"


def main() -> None:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    missing = [row for row in rows if not (row.get("intent_inferred") or "").strip()]
    TARGET.write_text(json.dumps(missing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"exported {len(missing)} of {len(rows)} events to {TARGET}")


if __name__ == "__main__":
    main()
