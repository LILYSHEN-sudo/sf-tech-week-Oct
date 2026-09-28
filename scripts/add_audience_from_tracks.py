#!/usr/bin/env python3
"""Add audience labels supported by the event's official tracks."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from audience_labels import LABEL_ORDER, format_audience, parse_audience


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"
TRACK_AUDIENCES = {
    "Global Founders": {"Founder"},
    "Fundraising & Investing": {"Founder", "Investor"},
    "Developer Tools": {"Engineer"},
    "Hackathons and Demos": {"Engineer"},
    "Consumer & Creative AI": {"Creator"},
}


def split_tracks(value: str) -> set[str]:
    return {part.strip() for part in (value or "").split(";") if part.strip()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing data")
    args = parser.parse_args()

    rows = json.loads(DATA.read_text(encoding="utf-8"))
    matched_tracks = Counter()
    added_labels = Counter()
    changed_rows = 0
    for row in rows:
        tracks = split_tracks(row.get("tracks", ""))
        matched = tracks & TRACK_AUDIENCES.keys()
        matched_tracks.update(matched)
        inferred = set().union(*(TRACK_AUDIENCES[track] for track in matched)) if matched else set()
        existing = parse_audience(row.get("audience_inferred", ""))
        added = inferred - existing
        added_labels.update(added)
        changed_rows += bool(added)
        row["audience_inferred"] = format_audience(existing | inferred)

    if not args.dry_run:
        DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rows: {len(rows)}; events with added labels: {changed_rows}")
    for track in TRACK_AUDIENCES:
        print(f"{track}: {matched_tracks[track]}")
    for label in LABEL_ORDER:
        if added_labels[label]:
            print(f"added {label}: {added_labels[label]}")
    print("dry run" if args.dry_run else "written")


if __name__ == "__main__":
    main()
