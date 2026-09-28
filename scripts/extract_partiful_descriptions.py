#!/usr/bin/env python3
"""Extract public Partiful event descriptions into a copied master JSON.

The extractor prefers structured schema.org Event JSON-LD embedded in public
Partiful pages. It falls back to Open Graph / Twitter meta descriptions when
JSON-LD is missing, and records an explicit status for pages whose description
is not public.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_INPUT = Path("data/interim/sf-tech-week-master.json")
DEFAULT_OUTPUT = Path("data/interim/sf-tech-week-master-with-descriptions.json")
DEFAULT_REPORT = Path("data/interim/partiful-description-extraction-report.csv")
DEFAULT_CACHE_DIR = Path("data/output/partiful-description-cache")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0 Safari/537.36"
)

STATUS_OK = "ok"
STATUS_NO_URL = "no_partiful_url"
STATUS_NOT_PUBLIC = "not_public"
STATUS_LOGIN_REQUIRED = "login_required"
STATUS_NOT_FOUND = "not_found"
STATUS_NO_DESCRIPTION = "no_description"
STATUS_FETCH_ERROR = "fetch_error"
STATUS_PARSE_ERROR = "parse_error"


@dataclass(frozen=True)
class ExtractionResult:
    status: str
    description: str = ""
    source: str = ""
    error: str = ""
    http_status: int | None = None
    cache_path: str = ""


class MetaParser:
    """Tiny attribute parser for the metadata tags we need."""

    JSONLD_RE = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    META_RE = re.compile(r"<meta\s+([^>]+)>", flags=re.IGNORECASE | re.DOTALL)
    ATTR_RE = re.compile(
        r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(".*?"|\'.*?\'|[^\s"\'>/]+)',
        flags=re.DOTALL,
    )

    @classmethod
    def json_ld_blocks(cls, document: str) -> list[Any]:
        blocks: list[Any] = []
        for match in cls.JSONLD_RE.finditer(document):
            raw = html.unescape(match.group(1)).strip()
            if not raw:
                continue
            try:
                blocks.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return blocks

    @classmethod
    def meta_tags(cls, document: str) -> list[dict[str, str]]:
        tags: list[dict[str, str]] = []
        for match in cls.META_RE.finditer(document):
            attrs: dict[str, str] = {}
            for key, value in cls.ATTR_RE.findall(match.group(1)):
                attrs[key.lower()] = html.unescape(value.strip("\"'"))
            if attrs:
                tags.append(attrs)
        return tags


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def partiful_event_id(url: str) -> str:
    parsed = urlparse(url)
    bits = [bit for bit in parsed.path.split("/") if bit]
    if len(bits) >= 2 and bits[-2] == "e":
        return bits[-1]
    return re.sub(r"[^A-Za-z0-9_-]+", "_", url).strip("_")[:120]


def cache_file_for(cache_dir: Path, url: str) -> Path:
    return cache_dir / f"{partiful_event_id(url)}.html"


def fetch_html(url: str, timeout: float) -> tuple[str, int]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        encoding = response.headers.get_content_charset() or "utf-8"
        body = response.read()
        return body.decode(encoding, errors="replace"), int(response.status)


def get_html(url: str, cache_dir: Path, timeout: float, force: bool) -> tuple[str, int | None, str]:
    cache_path = cache_file_for(cache_dir, url)
    if cache_path.exists() and not force:
        return cache_path.read_text(encoding="utf-8", errors="replace"), None, str(cache_path)

    document, status = fetch_html(url, timeout=timeout)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(document, encoding="utf-8")
    return document, status, str(cache_path)


def iter_json_objects(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(iter_json_objects(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(iter_json_objects(child))
    return found


def is_event_object(obj: dict[str, Any]) -> bool:
    kind = obj.get("@type")
    if isinstance(kind, list):
        return "Event" in kind
    return kind == "Event"


def extract_from_json_ld(document: str) -> tuple[str, str]:
    for block in MetaParser.json_ld_blocks(document):
        for obj in iter_json_objects(block):
            if is_event_object(obj):
                description = normalize_text(obj.get("description"))
                if description:
                    return description, "json_ld_event"
    return "", ""


def extract_from_meta(document: str) -> tuple[str, str]:
    candidates = [
        ("property", "og:description", "og_description"),
        ("name", "twitter:description", "twitter_description"),
        ("itemprop", "description", "itemprop_description"),
        ("name", "description", "meta_description"),
    ]
    tags = MetaParser.meta_tags(document)
    for attr, expected, source in candidates:
        for tag in tags:
            if tag.get(attr) == expected:
                description = normalize_text(tag.get("content"))
                if description and not description.endswith("…"):
                    return description, source
    for attr, expected, source in candidates:
        for tag in tags:
            if tag.get(attr) == expected:
                description = normalize_text(tag.get("content"))
                if description:
                    return description, source
    return "", ""


def classify_empty_page(document: str) -> str:
    lower = document.lower()
    if "page not found" in lower or "event not found" in lower:
        return STATUS_NOT_FOUND
    if "only rsvp'd guests can view" in lower or "restricted access" in lower:
        return STATUS_NOT_PUBLIC
    if "login" in lower and ("private" in lower or "sign in" in lower):
        return STATUS_LOGIN_REQUIRED
    return STATUS_NO_DESCRIPTION


def extract_description(url: str, cache_dir: Path, timeout: float, force: bool) -> ExtractionResult:
    try:
        document, http_status, cache_path = get_html(url, cache_dir, timeout, force)
    except HTTPError as exc:
        status = STATUS_NOT_FOUND if exc.code == 404 else STATUS_FETCH_ERROR
        return ExtractionResult(status=status, error=f"HTTP {exc.code}", http_status=exc.code)
    except (URLError, TimeoutError, OSError) as exc:
        return ExtractionResult(status=STATUS_FETCH_ERROR, error=str(exc))

    try:
        description, source = extract_from_json_ld(document)
        if not description:
            description, source = extract_from_meta(document)
        if description:
            return ExtractionResult(
                status=STATUS_OK,
                description=description,
                source=source,
                http_status=http_status,
                cache_path=cache_path,
            )
        return ExtractionResult(
            status=classify_empty_page(document),
            http_status=http_status,
            cache_path=cache_path,
        )
    except Exception as exc:  # noqa: BLE001 - keep batch jobs moving.
        return ExtractionResult(
            status=STATUS_PARSE_ERROR,
            error=f"{type(exc).__name__}: {exc}",
            http_status=http_status,
            cache_path=cache_path,
        )


def load_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise TypeError(f"Expected {path} to contain a list, got {type(data).__name__}")
    for index, row in enumerate(data):
        if not isinstance(row, dict):
            raise TypeError(f"Row {index} is {type(row).__name__}, expected object")
    return data


def select_work_indices(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[int]:
    indices = [i for i, row in enumerate(rows) if row.get("partiful_url")]
    if args.only_missing:
        indices = [
            i
            for i in indices
            if not rows[i].get("partiful_description_status")
            or rows[i].get("partiful_description_status") == STATUS_FETCH_ERROR
        ]
    if args.sample_size is not None:
        rng = random.Random(args.seed)
        sample_size = min(args.sample_size, len(indices))
        indices = rng.sample(indices, sample_size)
    if args.limit is not None:
        indices = indices[: args.limit]
    return indices


def apply_result(row: dict[str, Any], result: ExtractionResult, extracted_at: str) -> None:
    row["partiful_description"] = result.description
    row["partiful_description_status"] = result.status
    row["partiful_description_source"] = result.source
    row["partiful_description_extracted_at"] = extracted_at
    row["partiful_description_error"] = result.error
    row["partiful_description_http_status"] = result.http_status
    row["partiful_description_cache_path"] = result.cache_path


def save_outputs(rows: list[dict[str, Any]], output_json: Path, report_csv: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    report_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    fieldnames = [
        "event_id",
        "name",
        "date",
        "time",
        "primary_host",
        "partiful_url",
        "partiful_description_status",
        "partiful_description_source",
        "partiful_description_length",
        "partiful_description_error",
        "partiful_description_http_status",
        "partiful_description_cache_path",
    ]
    with report_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if not row.get("partiful_url"):
                continue
            description = row.get("partiful_description") or ""
            writer.writerow(
                {
                    "event_id": row.get("event_id", ""),
                    "name": row.get("name", ""),
                    "date": row.get("date", ""),
                    "time": row.get("time", ""),
                    "primary_host": row.get("primary_host", ""),
                    "partiful_url": row.get("partiful_url", ""),
                    "partiful_description_status": row.get("partiful_description_status", ""),
                    "partiful_description_source": row.get("partiful_description_source", ""),
                    "partiful_description_length": len(description),
                    "partiful_description_error": row.get("partiful_description_error", ""),
                    "partiful_description_http_status": row.get(
                        "partiful_description_http_status", ""
                    ),
                    "partiful_description_cache_path": row.get(
                        "partiful_description_cache_path", ""
                    ),
                }
            )


def summarize(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        if not row.get("partiful_url"):
            continue
        status = row.get("partiful_description_status") or "unprocessed"
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-csv", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--seed", type=int, default=20260926)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--save-every", type=int, default=50)
    parser.add_argument("--force", action="store_true", help="Ignore cached HTML and refetch.")
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Skip rows that already have a terminal extraction status in the input file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    rows = load_rows(args.input)
    indices = select_work_indices(rows, args)
    if not indices:
        save_outputs(rows, args.output_json, args.report_csv)
        print("No matching Partiful rows to process.")
        return 0

    started_at = now_iso()
    for row in rows:
        if not row.get("partiful_url") and not row.get("partiful_description_status"):
            row["partiful_description_status"] = STATUS_NO_URL

    completed = 0
    errors = 0
    print(f"Processing {len(indices)} Partiful URLs with {args.workers} workers...")

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_index = {}
        for n, index in enumerate(indices):
            if args.delay and n:
                time.sleep(args.delay)
            url = str(rows[index].get("partiful_url"))
            future = executor.submit(
                extract_description,
                url,
                args.cache_dir,
                args.timeout,
                args.force,
            )
            future_to_index[future] = index

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - keep batch jobs moving.
                result = ExtractionResult(
                    status=STATUS_FETCH_ERROR,
                    error=f"{type(exc).__name__}: {exc}",
                )
            apply_result(rows[index], result, started_at)
            completed += 1
            if result.status != STATUS_OK:
                errors += 1
            if completed % args.save_every == 0:
                save_outputs(rows, args.output_json, args.report_csv)
                print(f"Saved {completed}/{len(indices)}; latest status={result.status}")

    save_outputs(rows, args.output_json, args.report_csv)
    counts = summarize(rows)
    print(f"Done. Processed={completed}, non_ok={errors}")
    for status, count in counts.items():
        print(f"{status}: {count}")
    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.report_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
