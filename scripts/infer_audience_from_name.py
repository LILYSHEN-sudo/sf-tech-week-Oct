#!/usr/bin/env python3
"""Add audience labels supported by event names to the slim event dataset."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from audience_labels import format_audience, parse_audience


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"

NAME_RULES = (
    ("Founder", re.compile(r"\bfounders?\b", re.I)),
    ("Investor", re.compile(r"\binvestors?\b", re.I)),
    ("Engineer", re.compile(r"\bengineers?\b", re.I)),
    ("PM", re.compile(r"\b(?:PMs?|product managers?|product leaders?|CPOs?)\b", re.I)),
    ("Marketing", re.compile(r"\bmarketing\b", re.I)),
    ("Sales", re.compile(r"\bsales\b", re.I)),
    ("HR", re.compile(r"\bHR\b", re.I)),
    ("Creator", re.compile(r"\bcreators?\b", re.I)),
)


def add_name_labels(row: dict) -> set[str]:
    existing = parse_audience(row.get("audience_inferred", ""))
    matched = {label for label, pattern in NAME_RULES if pattern.search(row.get("name") or "")}
    row["audience_inferred"] = format_audience(existing | matched)
    return matched


def main() -> None:
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    counts = Counter()
    matched_rows = 0
    for row in rows:
        matched = add_name_labels(row)
        counts.update(matched)
        matched_rows += bool(matched)
    DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rows: {len(rows)}; title matches: {matched_rows}")
    for label, _ in NAME_RULES:
        print(f"{label}: {counts[label]}")


if __name__ == "__main__":
    main()
