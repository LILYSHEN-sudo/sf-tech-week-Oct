#!/usr/bin/env python3
"""Add audience labels from explicit role mentions in public descriptions."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from audience_labels import LABEL_ORDER, format_audience, parse_audience


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"
ROLE_PATTERNS = {
    "Founder": r"\b(?:founders?|co[- ]founders?|start[- ]?ups?|entrepreneurs?)\b",
    "Investor": r"\b(?:investors?|VCs?|venture capitalists?|angel investors?)\b",
    "Engineer": r"\b(?:engineers?|developers?|software developers?|builders?)\b",
    "PM": r"\b(?:product managers?|product leaders?|chief product officers?|CPOs?)\b",
    "Marketing": r"\b(?:marketing|marketers?|communications?|public relations)\b",
    "Sales": r"\b(?:sales|business development|GTM|go[- ]to[- ]market)\b",
    "HR": r"\b(?:HR|recruiters?|recruiting|hiring|talent acquisition|people ops)\b",
    "Creator": r"\b(?:creators?|artists?|filmmakers?|musicians?|creative professionals?)\b",
}
ROLE_RULES = {label: re.compile(pattern, re.I) for label, pattern in ROLE_PATTERNS.items()}
FOOTER_START = re.compile(r"\bthis event is (?:an? )?(?:official )?part of #SFTechWeek\b", re.I)
GENERIC_LINE = re.compile(r"\ba week of events hosted by VCs and startups\b", re.I)
URL = re.compile(r"https?://\S+", re.I)


def meaningful_description(value: str) -> str:
    text = value or ""
    footer = FOOTER_START.search(text)
    if footer:
        text = text[:footer.start()]
    text = GENERIC_LINE.sub(" ", text)
    return URL.sub(" ", text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing data")
    args = parser.parse_args()

    rows = json.loads(DATA.read_text(encoding="utf-8"))
    matched_counts = Counter()
    added_counts = Counter()
    changed_rows = 0
    for row in rows:
        description = meaningful_description(row.get("partiful_description", ""))
        matched = {label for label, rule in ROLE_RULES.items() if rule.search(description)}
        existing = parse_audience(row.get("audience_inferred", ""))
        added = matched - existing
        matched_counts.update(matched)
        added_counts.update(added)
        changed_rows += bool(added)
        row["audience_inferred"] = format_audience(existing | matched)

    if not args.dry_run:
        DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"rows: {len(rows)}; descriptions with added labels: {changed_rows}")
    for label in LABEL_ORDER:
        print(f"{label}: matched {matched_counts[label]}, added {added_counts[label]}")
    print("dry run" if args.dry_run else "written")


if __name__ == "__main__":
    main()
