#!/usr/bin/env python3
"""Infer seven participant goals from event content, themes, and formats."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/00-ready-to-use-data/sf-tech-week-events-master-slim.json"
LABELS = ("Funding", "Networking", "Building", "Learning", "Consumer", "Hiring", "Entertainment")
FOOTER = re.compile(
    r"This event is (?:an? )?(?:official )?part of #SF\s*TechWeek\b"
    r".*?(?:www\.tech-week\.com|https?://tech-week\.com|(?:tech|technology) ecosystem\.?)", re.I | re.S
)
BARE_FOOTER = re.compile(r"This event is (?:an? )?(?:official )?part of #SF\s*TechWeek\.[ \t]*(?=\n|$)", re.I)
URL = re.compile(r"https?://\S+", re.I)


def has(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, re.I))


def event_description(row: dict) -> str:
    description = FOOTER.sub(" ", row.get("partiful_description") or "")
    description = BARE_FOOTER.sub(" ", description)
    return URL.sub(" ", description)


def event_text(row: dict) -> str:
    return f"{row.get('name') or ''}\n{event_description(row)}"


def infer(row: dict) -> set[str]:
    name = row.get("name") or ""
    text = event_text(row)
    formats = {part.strip() for part in (row.get("formats") or "").split(";")}
    tracks = {part.strip() for part in (row.get("tracks") or "").split(";")}
    themes = {part.strip() for part in (row.get("themes") or "").split(";")}
    labels: set[str] = set()

    if formats & {"Networking", "Matchmaking", "Happy Hour", "Dinner", "Breakfast, Brunch or Lunch"} or has(
        r"\b(?:networking|mingle|mingling|meetup|meet[- ]up|connect(?:ions?|ing)? with|"
        r"meet (?:your|new|fellow|like[- ]minded|other|potential) (?:people|peers|professionals|"
        r"founders|investors|builders)|roundtable|curated dinner|social mixer|"
        r"happy hour|intentional connection|genuine connections|mixer)\b", text
    ) or has(r"\b(?:breakfast|brunch|lunch|afterparty)\b", name):
        labels.add("Networking")

    if formats & {"Panel / Fireside Chat", "Roundtable / Workshop", "Pitch Event / Demo Day"} or has(
        r"\b(?:learn (?:how|from|about (?!you\b))|learning session|teach(?:ing)?|"
        r"tutorial|masterclass|seminar|lecture|keynote|demo (?:night|day|session)|"
        r"fireside chat|panel(?: discussion|ists?)?|Q\s*&\s*A|talks?|speakers?|"
        r"presentation|deep dive|deep-dive|case stud(?:y|ies)|live demo|"
        r"walkthrough|discussion on|conversation (?:about|on)|insights into)\b", text
    ) or has(r"\b(?:showcase|101)\b", name):
        labels.add("Learning")

    if "Hackathon" in formats or has(
        r"\b(?:hackathon|hack (?:night|day)|build(?:ing)? (?:sprint|session|jam)|"
        r"code[- ]?along|hands[- ]on (?:build|cod(?:e|ing)|prototype|workshop|lab)|"
        r"build (?:a|an|your|with) (?:working |live )?(?:app|agent|prototype|product|"
        r"pipeline|model|tool|demo)|prototype (?:a|your)|ship (?:a|your) (?:app|agent|"
        r"prototype|product)|open building|co[- ]creat(?:e|ion))\b", text
    ):
        labels.add("Building")

    if "Fundraising & Investing" in tracks or "Fundraising / Investing" in themes or has(
        r"\b(?:fundrais(?:e|ing)|rais(?:e|ing) (?:a |your |the )?(?:funding|capital|"
        r"seed|series [a-f]|round)|pitch(?:ing)? (?:to|for|your) (?:investors?|VCs?)|"
        r"investor (?:matchmaking|meetings?|office hours|introductions?|networking)|"
        r"meet (?:potential |your next )?(?:investors?|VCs?|angels?)|"
        r"connect with (?:potential )?(?:investors?|VCs?|angels?)|"
        r"your next investor)\b", text
    ) or ("Matchmaking" in formats and has(r"\b(?:investors?|VCs?|angels?)\b", text)) or (
        "Networking" in labels and has(r"\b(?:founders?|startups?)\b", name)
        and has(r"\b(?:investors?|funders?|VCs?)\b", name)
    ) or (
        "Pitch Event / Demo Day" in formats and has(r"\b(?:investor (?:judges?|panel|pitch)|pitch(?:ing)? to investors?)\b", text)
    ):
        labels.add("Funding")

    if has(
        r"\b(?:find|meet|connect with|introduc(?:e|tion(?:s)? to)|match(?:ed)? with|"
        r"sell to|pitch to|reach|win|land) (?:your |new |potential |future |enterprise |"
        r"prospective )*(?:customers?|buyers?|clients?)\b|"
        r"\b(?:acquir(?:e|ing) customers|buyer[- ]seller matchmaking|"
        r"(?:generate|find|get|collect) (?:qualified )?(?:sales )?leads|"
        r"your next customer|pilot customers?|design partners?)\b", text
    ) or ("Matchmaking" in formats and has(r"\b(?:buyers?|customers?|clients?)\b", text)):
        labels.add("Consumer")

    if has(
        r"\b(?:job fair|career fair|recruiting event|recruitment event|talent matchmaking|"
        r"hiring (?:event|fair|opportunit(?:y|ies)|managers?|for|talent|engineers?|"
        r"your next)|looking to hire|find (?:your next |new )?(?:employees?|hires?|"
        r"talent|candidates?)|meet (?:potential |future )?(?:employees?|hires?|"
        r"candidates?)|your next hire|open (?:roles|positions)|job (?:hunt|search|opportunit(?:y|ies))|"
        r"open to work|find (?:a |your next )?job)\b", text
    ) or ("Matchmaking" in formats and has(r"\b(?:hires?|employees?|talent|candidates?)\b", text)):
        labels.add("Hiring")

    if has(
        r"\b(?:karaoke|comedy|comedians?|improvisors?|improv show|murder mystery|"
        r"mahjong|poker (?:night|tournament|invitational)|game show|game night|"
        r"scavenger hunt|geoguessr|beat battle|movie night|film screening|"
        r"stand[- ]up (?:show|comedy)|loter[ií]a|DJ set|coffee rave|masquerave|"
        r"live (?:music|band)|dance (?:floor|party)|block party)\b", name
    ) or has(
        r"\b(?:karaoke|comedy show|stand[- ]up comedy|improv show|murder mystery|"
        r"mahjong night|poker (?:night|tournament)|trivia night|DJ set|"
        r"live (?:music|band)|dance (?:floor|party)|film screening)\b", event_description(row)[:1600]
    ):
        labels.add("Entertainment")

    if themes & {"Media / Entertainment", "Gaming", "AR / VR"}:
        labels.add("Entertainment")
    if "B2C / Consumer" in themes:
        labels.add("Consumer")

    return labels


def classify(row: dict) -> set[str]:
    labels = infer(row)
    return labels | {"Networking"} if not labels - {"Entertainment", "Consumer"} else labels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    counts = Counter()
    for row in rows:
        labels = classify(row)
        row["intent_inferred"] = "; ".join(label for label in LABELS if label in labels)
        counts.update(labels)
    if not args.dry_run:
        DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"events: {len(rows)}; unlabeled: {sum(not r['intent_inferred'] for r in rows)}")
    for label in LABELS:
        print(f"{label}: {counts[label]}")


if __name__ == "__main__":
    main()
