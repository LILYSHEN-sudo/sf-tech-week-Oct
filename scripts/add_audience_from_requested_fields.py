#!/usr/bin/env python3
"""Apply the requested cross-field audience keyword rules to the slim dataset."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from add_audience_from_description import meaningful_description
from audience_labels import LABEL_ORDER, format_audience, parse_audience


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"

TEXT_RULES = (
    ("description:company", "description", re.compile(r"\bcompan(?:y|ies)\b", re.I), {"Founder"}),
    ("description:brand", "description", re.compile(r"\bbrands?\b", re.I), {"Founder"}),
    ("description:CFOs", "description", re.compile(r"\bCFOs?\b", re.I), {"Founder"}),
    ("description:VPs", "description", re.compile(r"\bVPs?\b", re.I), {"Investor"}),
    ("description:Engineering", "description", re.compile(r"\bengineering\b", re.I), {"Engineer"}),
    ("name:Building", "name", re.compile(r"\bbuilding\b", re.I), {"Engineer"}),
    ("name:CTO", "name", re.compile(r"\bCTOs?\b", re.I), {"Engineer", "Founder"}),
    ("name:Builders", "name", re.compile(r"\bbuilders?\b", re.I), {"Engineer"}),
    ("primary_host:Ventures", "primary_host", re.compile(r"\bVentures\b", re.I), {"Founder", "Investor"}),
)

TAG_RULES = (
    ("themes:Engineering", "themes", "Engineering", {"Engineer"}),
    ("themes:Fundraising / Investing", "themes", "Fundraising / Investing", {"Founder", "Investor"}),
    ("formats:Pitch Event / Demo Day", "formats", "Pitch Event / Demo Day", {"Founder", "Investor", "Engineer"}),
    ("formats:Hackathon", "formats", "Hackathon", {"Engineer"}),
)


def tags(value: str) -> set[str]:
    return {part.strip() for part in (value or "").split(";") if part.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show matches without writing data")
    args = parser.parse_args()

    rows = json.loads(DATA.read_text(encoding="utf-8"))
    rule_matches = Counter()
    added_labels = Counter()
    changed_rows = 0
    for row in rows:
        text = {
            "description": meaningful_description(row.get("partiful_description", "")),
            "name": row.get("name", "") or "",
            "primary_host": row.get("primary_host", "") or "",
        }
        inferred = set()
        for rule_name, field, pattern, labels in TEXT_RULES:
            if pattern.search(text[field]):
                inferred.update(labels)
                rule_matches[rule_name] += 1
        for rule_name, field, value, labels in TAG_RULES:
            if value in tags(row.get(field, "")):
                inferred.update(labels)
                rule_matches[rule_name] += 1

        existing = parse_audience(row.get("audience_inferred", ""))
        added = inferred - existing
        added_labels.update(added)
        changed_rows += bool(added)
        row["audience_inferred"] = format_audience(existing | inferred)

    if not args.dry_run:
        DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rows: {len(rows)}; events with added labels: {changed_rows}")
    for rule_name, *_ in TEXT_RULES + TAG_RULES:
        print(f"{rule_name}: {rule_matches[rule_name]}")
    for label in LABEL_ORDER:
        if added_labels[label]:
            print(f"added {label}: {added_labels[label]}")
    print("dry run" if args.dry_run else "written")


if __name__ == "__main__":
    main()
