#!/usr/bin/env python3
"""Collect one Furever reporting week from Feedback Collection (read only)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path


DEFAULT_BASE_TOKEN = "PhntbXzNxaY6mSsIVIgc3tYMnDc"
WIKI_TOKEN = "QB4hwPN8Ri5RCDkCuYVcivVBnPh"

TABLES = {
    "Gmail": {
        "table_id": "tblLWrYDT9Np0T8w",
        "time_field": "fldQsX4PCY",
        "unique_field": "Thread ID",
        "fields": [
            "fldq3LQ2WD",
            "fldfJ90AWE",
            "fldQsX4PCY",
            "fldEORHPwY",
            "fldj93pwkm",
            "fldyDtAYEZ",
            "fldgz36zue",
            "fldN9yfHA1",
        ],
    },
    "Typeform": {
        "table_id": "tblAgndOBZEUqrG7",
        "time_field": "fldMNjXoIO",
        "unique_field": "Submit ID",
        "fields": ["fldyZxeepT", "fldL3K1zbj", "fldwlGIFdZ", "fldMNjXoIO"],
    },
    "App Store": {
        "table_id": "tbllD74urwkj0gkX",
        "time_field": "fldBenvv26",
        "unique_field": "Review ID",
        "fields": [
            "fld1GqzuPg",
            "fldhJem0q0",
            "fldepgBJJS",
            "fldDEK6Koe",
            "fldvA5PnO4",
            "fldBenvv26",
            "fldEChy4P2",
            "fld8p84WMc",
        ],
    },
    "Discord": {
        "table_id": "tblZ7lS9m0FJGL4j",
        "time_field": None,
        "unique_field": None,
        "fields": ["fldXrsOSRK"],
    },
}

GMAIL_MESSAGE_HEADER = re.compile(
    r"(?m)^\[(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})\]\s*"
    r"(?:.*?<([^>]+)>|([^\s:<>]+@[^\s:<>]+)):\s*\n?"
)

SYSTEM_TEMPLATE_ONLY = re.compile(
    r"^\s*[（(]?\s*仅包含系统模板或引用\s*[，,]\s*无手写正文\s*[）)]?\s*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="Inclusive YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Inclusive YYYY-MM-DD")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--base-token", default=DEFAULT_BASE_TOKEN)
    parser.add_argument("--identity", choices=("user", "bot"), default="user")
    return parser.parse_args()


def run_record_list(
    *,
    base_token: str,
    identity: str,
    table_id: str,
    field_ids: list[str],
    time_field: str | None,
    day: date | None,
    offset: int,
) -> dict:
    argv = [
        "lark-cli",
        "base",
        "+record-list",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--limit",
        "200",
        "--offset",
        str(offset),
        "--as",
        identity,
        "--format",
        "json",
    ]
    if time_field and day:
        filter_value = {
            "logic": "and",
            "conditions": [[time_field, "==", f"ExactDate({day.isoformat()})"]],
        }
        argv += ["--filter-json", json.dumps(filter_value, separators=(",", ":"))]
        argv += ["--sort-json", json.dumps([{"field": time_field, "desc": False}])]
    for field_id in field_ids:
        argv += ["--field-id", field_id]

    completed = subprocess.run(argv, check=True, text=True, capture_output=True)
    payload = json.loads(completed.stdout)
    if not payload.get("ok"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    return payload["data"]


def collect_rows(
    *,
    channel: str,
    config: dict,
    base_token: str,
    identity: str,
    day: date | None,
) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        data = run_record_list(
            base_token=base_token,
            identity=identity,
            table_id=config["table_id"],
            field_ids=config["fields"],
            time_field=config["time_field"],
            day=day,
            offset=offset,
        )
        names = data["fields"]
        page = data.get("data", [])
        for record_id, values in zip(data.get("record_id_list", []), page):
            row = dict(zip(names, values))
            row.update(
                {
                    "_channel": channel,
                    "_table_id": config["table_id"],
                    "_record_id": record_id,
                    "_period_verified": bool(config["time_field"]),
                }
            )
            rows.append(row)
        if not data.get("has_more"):
            return rows
        if not page:
            raise RuntimeError(f"Pagination stalled for {channel}")
        offset += len(page)


def deduplicate_rows(rows: list[dict], unique_field: str | None) -> list[dict]:
    """Keep one record per source-native ID, falling back to the Base record ID."""
    unique: dict[str, dict] = {}
    for row in rows:
        native_id = row.get(unique_field) if unique_field else None
        key = str(native_id or row["_record_id"])
        unique[key] = row
    return list(unique.values())


def analysis_record_id(channel: str, row: dict, unique_field: str | None) -> str:
    native_id = row.get(unique_field) if unique_field else None
    return f"{channel}:{native_id or row['_record_id']}"


def resolve_message_date(month: int, day: int, start: date, end: date) -> date | None:
    """Resolve a month/day Gmail header against a possibly cross-year period."""
    for year in range(start.year, end.year + 1):
        try:
            candidate = date(year, month, day)
        except ValueError:
            return None
        if start <= candidate <= end:
            return candidate
    return None


def extract_gmail_analysis_text(row: dict, start: date, end: date) -> tuple[str, str | None]:
    """Return only in-period messages authored by the synchronized Gmail user."""
    feedback = str(row.get("Feedback") or "")
    user_email = str(row.get("Gmail") or "").strip().lower()
    matches = list(GMAIL_MESSAGE_HEADER.finditer(feedback))
    if not feedback.strip():
        return "", "empty_feedback"
    if not user_email:
        return "", "missing_user_email"
    if not matches:
        return "", "unparseable_message_headers"

    selected: list[str] = []
    saw_system_template_only = False
    for index, match in enumerate(matches):
        message_date = resolve_message_date(int(match.group(1)), int(match.group(2)), start, end)
        sender = str(match.group(5) or match.group(6) or "").strip().lower()
        message_end = matches[index + 1].start() if index + 1 < len(matches) else len(feedback)
        body = feedback[match.end() : message_end].strip()
        body = re.sub(r"\n?\s*-{6,}\s*$", "", body).strip()
        if message_date and sender == user_email and body:
            if SYSTEM_TEMPLATE_ONLY.fullmatch(body):
                saw_system_template_only = True
                continue
            selected.append(body)

    if not selected:
        if saw_system_template_only:
            return "", "system_template_or_quote_only"
        return "", "no_in_period_user_message"
    return "\n\n---\n\n".join(selected), None


def prepare_analysis_fields(
    *, channel: str, rows: list[dict], unique_field: str | None, start: date, end: date
) -> None:
    for row in rows:
        row["_analysis_record_id"] = analysis_record_id(channel, row, unique_field)
        if channel == "Gmail":
            analysis_text, exclusion_reason = extract_gmail_analysis_text(row, start, end)
            row["_analysis_text"] = analysis_text
            row["_analysis_eligible"] = exclusion_reason is None
            if exclusion_reason:
                row["_analysis_exclusion_reason"] = exclusion_reason
            else:
                row.pop("_analysis_exclusion_reason", None)
        elif row.get("_period_verified"):
            if channel == "Typeform":
                analysis_text = str(row.get("Q&A") or row.get("Questionnaire") or "").strip()
            elif channel == "App Store":
                analysis_text = "\n".join(
                    value for value in (str(row.get("Title") or "").strip(), str(row.get("Content") or "").strip()) if value
                )
            else:
                analysis_text = str(row.get("Text") or "").strip()
            row["_analysis_text"] = analysis_text
            row["_analysis_eligible"] = bool(analysis_text)
            if not analysis_text:
                row["_analysis_exclusion_reason"] = "empty_feedback"
        else:
            row["_analysis_text"] = ""
            row["_analysis_eligible"] = False
            row["_analysis_exclusion_reason"] = "period_not_verifiable"


def main() -> None:
    args = parse_args()
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    if end < start:
        raise SystemExit("--end must be on or after --start")

    raw_channels: dict[str, list[dict]] = {}
    for channel, config in TABLES.items():
        if config["time_field"]:
            current = start
            rows: list[dict] = []
            while current <= end:
                rows.extend(
                    collect_rows(
                        channel=channel,
                        config=config,
                        base_token=args.base_token,
                        identity=args.identity,
                        day=current,
                    )
                )
                current += timedelta(days=1)
            raw_channels[channel] = rows
        else:
            raw_channels[channel] = collect_rows(
                channel=channel,
                config=config,
                base_token=args.base_token,
                identity=args.identity,
                day=None,
            )

    channels = {
        channel: deduplicate_rows(rows, TABLES[channel]["unique_field"])
        for channel, rows in raw_channels.items()
    }
    for channel, rows in channels.items():
        prepare_analysis_fields(
            channel=channel,
            rows=rows,
            unique_field=TABLES[channel]["unique_field"],
            start=start,
            end=end,
        )

    analysis_counts = {
        name: sum(1 for row in rows if row.get("_analysis_eligible") is True)
        for name, rows in channels.items()
    }

    payload = {
        "source": {
            "wiki_title": "Feedback Collection",
            "wiki_token": WIKI_TOKEN,
            "base_token": args.base_token,
            "base_timezone": "Asia/Shanghai",
            "period_start": f"{start.isoformat()} 00:00:00",
            "period_end": f"{end.isoformat()} 23:59:59",
            "scope_note": "Ordinary feedback includes in-period user-authored Gmail messages, Typeform, App Store, and period-verifiable Discord records from Feedback Collection. Direct Gmail mailbox access is not used.",
            "date_filter": "Server-side ExactDate(day) with exhausted pagination for timestamped tables.",
            "gmail_filter": "Only messages whose sender matches the synchronized Gmail user and whose message header date falls inside the period are analysis-eligible.",
            "warning": "Discord has no configured timestamp field and is excluded from analysis totals unless its timestamp becomes verifiable.",
        },
        "channels": channels,
        "counts": {name: len(rows) for name, rows in channels.items()},
        "analysis_counts": analysis_counts,
        "ordinary_total": sum(analysis_counts.values()),
        "raw_counts": {name: len(rows) for name, rows in raw_channels.items()},
        "deduplication": {
            name: config["unique_field"] or "Base record ID"
            for name, config in TABLES.items()
        },
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output),
                "raw_counts": payload["raw_counts"],
                "deduplicated_counts": payload["counts"],
                "analysis_counts": payload["analysis_counts"],
                "ordinary_total": payload["ordinary_total"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
