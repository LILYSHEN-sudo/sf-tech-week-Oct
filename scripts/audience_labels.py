"""Canonical display labels for the slim dataset's audience_inferred field."""

LABEL_ORDER = (
    "Founder", "Investor", "Engineer", "Marketing", "Sales", "HR", "Creator", "PM"
)

LEGACY_LABELS = {
    "founders": "Founder",
    "investors": "Investor",
    "engineers": "Engineer",
    "marketing-comms": "Marketing",
    "sales-bd": "Sales",
    "hr": "HR",
    "creators": "Creator",
    "product": "PM",
}


def parse_audience(value: str) -> set[str]:
    labels = {part.strip() for part in (value or "").split(";") if part.strip()}
    unknown = labels - set(LABEL_ORDER) - set(LEGACY_LABELS)
    if unknown:
        raise ValueError(f"Unknown audience labels: {sorted(unknown)}")
    return {LEGACY_LABELS.get(label, label) for label in labels}


def format_audience(labels: set[str]) -> str:
    unknown = labels - set(LABEL_ORDER)
    if unknown:
        raise ValueError(f"Unknown audience labels: {sorted(unknown)}")
    return "; ".join(label for label in LABEL_ORDER if label in labels)
