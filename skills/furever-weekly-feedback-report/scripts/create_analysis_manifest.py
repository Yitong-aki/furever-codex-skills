#!/usr/bin/env python3
"""Create a full-coverage ordinary-feedback analysis manifest scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback-json", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feedback = json.loads(Path(args.feedback_json).read_text(encoding="utf-8-sig"))
    source = feedback.get("source", {})
    records = []
    for channel, rows in feedback.get("channels", {}).items():
        for row in rows:
            if row.get("_analysis_eligible") is not True:
                continue
            records.append(
                {
                    "record_id": row.get("_analysis_record_id"),
                    "channel": channel,
                    "analysis_text": row.get("_analysis_text", ""),
                    "issues": [],
                    "report_placement": [],
                }
            )

    payload = {
        "period_start": source.get("period_start"),
        "period_end": source.get("period_end"),
        "records": records,
    }
    output = Path(args.output)
    if output.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing manifest: {output}. Use --force if intentional.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "eligible_records": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
