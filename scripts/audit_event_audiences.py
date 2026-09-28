#!/usr/bin/env python3
"""Independently audit existing audience labels against event-specific evidence."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from audience_labels import LABEL_ORDER, format_audience, parse_audience
from infer_event_intents import BARE_FOOTER, FOOTER, URL


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"
AUDIT = ROOT / "analysis/audience-intent-analysis/audience-evidence-audit.json"
REVIEW = ROOT / "analysis/audience-intent-analysis/audience-review-queue.json"
OVERRIDES = ROOT / "analysis/audience-intent-analysis/audience-manual-overrides.json"

NAME_RULES = {
    "Founder": r"\b(?:co[- ]?founders?|founders?|entrepreneurs?|startups?)\b",
    "Investor": r"\b(?:investors?|funders?|VCs?|venture capitalists?|angel investors?)\b",
    "Engineer": r"\b(?:engineers?|developers?|coders?|CTOs?|builders?)\b",
    "Marketing": r"\b(?:marketing|marketers?|brand strategists?|public relations|PR professionals?)\b",
    "Sales": r"\b(?:sales|business development|GTM|go[- ]to[- ]market)\b",
    "HR": r"\b(?:HR|recruiters?|hiring|talent acquisition|people (?:ops|leaders?))\b",
    "Creator": r"\b(?:creators?|creatives?|artists?|designers?|filmmakers?|musicians?)\b",
    "PM": r"(?<!\d )\b(?:PMs?|product managers?|product leaders?|CPOs?)\b",
}
DESCRIPTION_RULES = {
    **NAME_RULES,
    "PM": r"\b(?:PMs|product managers?|product leaders?|CPOs?)\b",
    "Engineer": r"\b(?:engineers?|developers?|coders?|CTOs?|builders?|engineering)\b",
    "Marketing": r"\b(?:marketing|marketers?|communications?|public relations|brand strategists?)\b",
    "HR": r"\b(?:HR|recruiters?|recruiting|hiring|talent acquisition|people (?:ops|leaders?))\b",
    "Creator": r"\b(?:creators?|creatives|artists?|designers?|filmmakers?|musicians?|creative professionals?)\b",
}
GENERIC_FOOTER = re.compile(
    r"\ba week of events hosted by VCs and startups\b.*?(?:tech ecosystem\.?|www\.tech-week\.com)",
    re.I | re.S,
)
THEME_RULES = {"Creators": ("Creator",), "Engineering": ("Engineer",), "Fundraising / Investing": ("Founder", "Investor"), "HR / Hiring": ("HR",)}
TRACK_RULES = {
    "Global Founders": ("Founder",), "Fundraising & Investing": ("Founder", "Investor"),
    "Developer Tools": ("Engineer",), "Hackathons and Demos": ("Engineer",),
    "Consumer & Creative AI": ("Creator",),
}
FORMAT_RULES = {"Hackathon": ("Engineer",), "Pitch Event / Demo Day": ("Founder",)}
WEAK_RULES = {
    "Founder": (("description", r"\b(?:compan(?:y|ies)|brands?|CFOs?)\b"), ("host", r"\bVentures\b")),
    "Investor": (("description", r"\bVPs?\b"), ("host", r"\bVentures\b")),
    "Engineer": (("name", r"\bbuilding\b"), ("format", r"Pitch Event / Demo Day")),
}


def split(value: str) -> set[str]:
    return {part.strip() for part in (value or "").split(";") if part.strip()}


def clean_description(value: str) -> str:
    text = FOOTER.sub(" ", value or "")
    text = BARE_FOOTER.sub(" ", text)
    text = GENERIC_FOOTER.sub(" ", text)
    return URL.sub(" ", text)


def text_hit(source: str, pattern: str, value: str, strength: str) -> dict | None:
    found = re.search(pattern, value, re.I)
    if not found:
        return None
    excerpt = " ".join(value[max(0, found.start() - 55):found.end() + 75].split())
    return {"source": source, "term": found.group(0), "strength": strength, "excerpt": excerpt}


def evidence_for(row: dict) -> dict[str, list[dict]]:
    evidence: dict[str, list[dict]] = defaultdict(list)
    description = clean_description(row.get("partiful_description") or "")
    name = row.get("name") or ""
    fields = {"name": name, "description": description, "host": row.get("primary_host") or "", "format": row.get("formats") or ""}

    for label, pattern in NAME_RULES.items():
        if hit := text_hit("name", pattern, name, "high"):
            evidence[label].append(hit)
    for label, pattern in DESCRIPTION_RULES.items():
        if hit := text_hit("description", pattern, description, "medium"):
            evidence[label].append(hit)
    for source, rules in (("themes", THEME_RULES), ("tracks", TRACK_RULES), ("formats", FORMAT_RULES)):
        for term in split(row.get(source) or "") & rules.keys():
            for label in rules[term]:
                evidence[label].append({"source": source, "term": term, "strength": "medium"})
    for label, rules in WEAK_RULES.items():
        for source, pattern in rules:
            if hit := text_hit(source, pattern, fields[source], "weak"):
                evidence[label].append(hit)
    return dict(evidence)


def audit_row(row: dict, overrides: dict[str, list[str]]) -> dict:
    current = parse_audience(row.get("audience_inferred") or "")
    evidence = evidence_for(row)
    manual = overrides.get(row["event_id"])
    candidate = set(manual) if manual is not None else {
        label for label, hits in evidence.items() if any(hit["strength"] != "weak" for hit in hits)
    }
    unsupported = current - candidate
    new = candidate - current
    auto_add = new if manual is not None else {
        label for label in new if any(
            hit["source"] in {"name", "themes", "tracks"} or
            (hit["source"] == "formats" and hit["term"] == "Hackathon")
            for hit in evidence.get(label, [])
        )
    }
    review_add = new - auto_add
    weak_only = {
        label for label in unsupported
        if label in evidence and all(hit["strength"] == "weak" for hit in evidence[label])
    }
    reasons = []
    if not current:
        reasons.append("currently-unlabeled")
    if weak_only:
        reasons.append("weak-only-old-label")
    if len(current) >= 5:
        reasons.append("many-old-labels")
    if not (row.get("partiful_description") or "").strip():
        reasons.append("no-public-description")
    if review_add:
        reasons.append("new-description-candidate")
    return {
        "event_id": row["event_id"], "name": row.get("name") or "",
        "current": format_audience(current), "candidate": format_audience(candidate),
        "manual_override": manual is not None,
        "auto_add": format_audience(auto_add), "review_add": format_audience(review_add),
        "review_remove": format_audience(unsupported),
        "weak_only": format_audience(weak_only), "evidence": evidence,
        "review_priority": "high" if reasons and any(reason in reasons for reason in (
            "currently-unlabeled", "weak-only-old-label", "many-old-labels", "no-public-description"
        )) else "normal",
        "review_reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply supported additions and manual overrides only")
    args = parser.parse_args()
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    audits = [audit_row(row, overrides) for row in rows]
    AUDIT.write_text(json.dumps(audits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = [record for record in audits if not record["manual_override"] and (
        record["review_add"] or record["review_remove"] or
        "many-old-labels" in record["review_reasons"] or not record["current"]
    )]
    review.sort(key=lambda record: (record["review_priority"] != "high", record["name"].casefold()))
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.apply:
        for row, record in zip(rows, audits):
            if record["manual_override"]:
                labels = parse_audience(record["candidate"])
            else:
                labels = parse_audience(record["current"]) | parse_audience(record["auto_add"])
            row["audience_inferred"] = format_audience(labels)
        DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = Counter()
    for record in audits:
        for key in ("auto_add", "review_add", "review_remove", "weak_only"):
            counts[key] += bool(record[key])
    print(f"events {len(rows)}; auto-add {counts['auto_add']}; add review {counts['review_add']}; removal review {counts['review_remove']}; weak-only {counts['weak_only']}; applied {args.apply}")


if __name__ == "__main__":
    main()
