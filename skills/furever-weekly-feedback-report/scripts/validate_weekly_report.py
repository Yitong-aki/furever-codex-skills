#!/usr/bin/env python3
"""Validate Furever weekly-report inputs and final Feishu XML."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


REQUIRED_H1 = [
    "1. 数据来源与样本概览",
    "2. 一句话结论",
    "3. Executive Summary",
    "4. 补充观察与趋势信号",
    "5. P1–P2 深度问题分析",
    "6. AI 生成质量专项分析",
    "7. 功能诉求与机会点",
    "8. 各渠道专项分析",
]

EXECUTIVE_HEADERS = [
    "优先级",
    "严重度",
    "具体问题 / 机会",
    "去重数 / 占比",
    "证据",
    "影响",
    "Team Comment",
]

AI_HEADERS = [
    "User ID",
    "Snap/Generation ID",
    "图片或视频 link",
    "Snap Type",
    "后台原始 Tag",
    "用户原文",
    "用户输入原图",
    "AI 生成图片",
    "AI 生成视频",
    "是否有 character sheet",
]

AI_TAG_HEADERS = ["后台原始 Tag", "记录数 / 占比", "Tag 含义"]

GMAIL_SECTION_HEADING = "8.1 Gmail｜主要反馈主题与代表原文"

ORDINARY_CATEGORIES = {
    "AI 生成质量",
    "核心流程与稳定性",
    "付费、订阅与权益",
    "功能与交互需求",
    "内容与情感体验",
    "正向体验",
    "其他",
}

SYSTEM_TEMPLATE_ONLY = re.compile(
    r"^\s*[（(]?\s*仅包含系统模板或引用\s*[，,]\s*无手写正文\s*[）)]?\s*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback-json")
    parser.add_argument("--previous-feedback-json")
    parser.add_argument("--analysis-json")
    parser.add_argument("--backend-json")
    parser.add_argument("--report-xml")
    parser.add_argument("--output")
    parser.add_argument("--allow-placeholders", action="store_true")
    parser.add_argument("--skip-wow-reason")
    return parser.parse_args()


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def text_of(element: ET.Element) -> str:
    return "".join(element.itertext()).strip()


def validate_feedback(payload: dict, errors: list[str], warnings: list[str]) -> None:
    source = payload.get("source", {})
    channels = payload.get("channels")
    counts = payload.get("counts")
    if not isinstance(channels, dict) or not isinstance(counts, dict):
        errors.append("Feedback JSON must contain object fields: channels and counts.")
        return
    for required in ("Gmail", "Typeform", "App Store"):
        if required not in channels:
            errors.append(f"Missing required Feedback Collection channel: {required}.")
    for name, rows in channels.items():
        if not isinstance(rows, list):
            errors.append(f"Channel {name} is not a list.")
            continue
        if counts.get(name) != len(rows):
            errors.append(f"Count mismatch for {name}: metadata={counts.get(name)}, actual={len(rows)}.")
        for row in rows:
            if not row.get("_analysis_record_id"):
                errors.append(f"Channel {name} has a row without _analysis_record_id.")
                break
            if not isinstance(row.get("_analysis_eligible"), bool):
                errors.append(f"Channel {name} has a row without boolean _analysis_eligible.")
                break
            if row.get("_analysis_eligible") is True and SYSTEM_TEMPLATE_ONLY.fullmatch(
                str(row.get("_analysis_text") or "")
            ):
                errors.append(
                    f"Channel {name} marks a system-template-only row as analysis eligible: "
                    f"{row.get('_analysis_record_id')}."
                )
                break
    raw_counts = payload.get("raw_counts", {})
    if isinstance(raw_counts, dict):
        for name, deduplicated_count in counts.items():
            raw_count = raw_counts.get(name)
            if isinstance(raw_count, int) and raw_count < deduplicated_count:
                errors.append(
                    f"Raw count cannot be smaller than deduplicated count for {name}: "
                    f"raw={raw_count}, deduplicated={deduplicated_count}."
                )
    if not source.get("period_start") or not source.get("period_end"):
        errors.append("Feedback JSON is missing period_start or period_end.")
    analysis_counts = payload.get("analysis_counts")
    if not isinstance(analysis_counts, dict):
        errors.append("Feedback JSON is missing analysis_counts.")
    else:
        for name, rows in channels.items():
            actual = sum(1 for row in rows if row.get("_analysis_eligible") is True)
            if analysis_counts.get(name) != actual:
                errors.append(
                    f"Analysis count mismatch for {name}: metadata={analysis_counts.get(name)}, actual={actual}."
                )
        expected_total = sum(value for value in analysis_counts.values() if isinstance(value, int))
        if payload.get("ordinary_total") != expected_total:
            errors.append(
                f"ordinary_total mismatch: metadata={payload.get('ordinary_total')}, actual={expected_total}."
            )
    discord = channels.get("Discord", [])
    if discord and any(row.get("_period_verified") is False for row in discord):
        warnings.append("Discord contains records without a verified reporting-period timestamp.")


def validate_analysis_manifest(
    feedback: dict, analysis: dict, errors: list[str], warnings: list[str]
) -> None:
    expected_ids = {
        str(row.get("_analysis_record_id"))
        for rows in feedback.get("channels", {}).values()
        for row in rows
        if row.get("_analysis_eligible") is True
    }
    records = analysis.get("records")
    if not isinstance(records, list):
        errors.append("Analysis JSON must contain a records list.")
        return

    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"Analysis record {index} is not an object.")
            continue
        record_id = str(record.get("record_id") or "")
        if not record_id:
            errors.append(f"Analysis record {index} is missing record_id.")
            continue
        if record_id in seen:
            errors.append(f"Analysis manifest contains duplicate record_id: {record_id}.")
        seen.add(record_id)
        issues = record.get("issues")
        if not isinstance(issues, list) or not issues:
            errors.append(f"Analysis record {record_id} has no issues.")
            continue
        for issue_index, issue in enumerate(issues, start=1):
            if not isinstance(issue, dict) or not str(issue.get("summary") or "").strip():
                errors.append(
                    f"Analysis record {record_id} issue {issue_index} has no concrete summary."
                )
                continue
            categories = issue.get("categories")
            if not isinstance(categories, list) or not categories:
                errors.append(
                    f"Analysis record {record_id} issue {issue_index} has no categories."
                )
                continue
            invalid = [category for category in categories if category not in ORDINARY_CATEGORIES]
            if invalid:
                errors.append(
                    f"Analysis record {record_id} issue {issue_index} uses invalid categories: {invalid}."
                )

    missing = sorted(expected_ids - seen)
    unknown = sorted(seen - expected_ids)
    if missing:
        errors.append(f"Analysis manifest is missing {len(missing)} eligible records: {missing[:10]}.")
    if unknown:
        errors.append(f"Analysis manifest contains {len(unknown)} unknown or ineligible records: {unknown[:10]}.")
    if not expected_ids:
        warnings.append("Current ordinary-feedback input has no analysis-eligible records.")


def validate_period_pair(current: dict, previous: dict, errors: list[str]) -> None:
    try:
        current_start = datetime.fromisoformat(current["source"]["period_start"]).date()
        current_end = datetime.fromisoformat(current["source"]["period_end"]).date()
        previous_start = datetime.fromisoformat(previous["source"]["period_start"]).date()
        previous_end = datetime.fromisoformat(previous["source"]["period_end"]).date()
    except (KeyError, TypeError, ValueError):
        errors.append("Cannot verify current/previous period adjacency from source period metadata.")
        return
    if previous_end != current_start - timedelta(days=1):
        errors.append("Previous feedback period must end one day before the current period starts.")
    if (previous_end - previous_start) != (current_end - current_start):
        errors.append("Current and previous feedback periods must contain the same number of days.")


def validate_backend(payload: dict, errors: list[str], warnings: list[str]) -> None:
    denominator = payload.get("denominator")
    if not isinstance(denominator, dict):
        errors.append("Backend JSON is missing denominator metadata.")
        return
    for key in ("image_events", "video_events"):
        value = denominator.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"Backend denominator {key} must be a non-negative integer.")
    for media in ("image", "video"):
        tags = payload.get(media)
        if not isinstance(tags, dict):
            errors.append(f"Backend JSON is missing {media} Tag groups.")
            continue
        for tag, value in tags.items():
            if not isinstance(value, dict) or not isinstance(value.get("count"), int):
                errors.append(f"Backend Tag {media}.{tag} is missing an integer count.")
    if denominator.get("image_events", 0) == 0 and denominator.get("video_events", 0) == 0:
        warnings.append("Backend input has zero image and video events.")


def count_tag_cases(table: ET.Element, tag: str) -> int:
    count = 0
    for row in table.findall("./tbody/tr"):
        cells = list(row)
        if len(cells) >= 5 and tag.casefold() in text_of(cells[4]).casefold():
            count += 1
    return count


def top_level_section_nodes(root: ET.Element, heading: str) -> list[ET.Element]:
    """Return the top-level nodes after a named h1 and before the next h1."""
    children = list(root)
    start = None
    for index, node in enumerate(children):
        if node.tag == "h1" and text_of(node) == heading:
            start = index + 1
            break
    if start is None:
        return []
    end = len(children)
    for index in range(start, len(children)):
        if children[index].tag == "h1":
            end = index
            break
    return children[start:end]


def validate_section5_presentation(root: ET.Element, errors: list[str]) -> None:
    section_nodes = top_level_section_nodes(root, "5. P1–P2 深度问题分析")
    if not section_nodes:
        return

    if any(descendant.tag == "callout" for node in section_nodes for descendant in node.iter()):
        errors.append("Section 5 must not use callout/highlight boxes.")

    subsections: list[tuple[str, list[ET.Element]]] = []
    current_heading = ""
    current_nodes: list[ET.Element] = []
    for node in section_nodes:
        if node.tag == "h2":
            if current_heading:
                subsections.append((current_heading, current_nodes))
            current_heading = text_of(node)
            current_nodes = []
        elif current_heading:
            current_nodes.append(node)
    if current_heading:
        subsections.append((current_heading, current_nodes))

    for heading, nodes in subsections:
        body = "\n".join(text_of(node) for node in nodes)
        quote_numbers = set(re.findall(r"用户原文\s*([1-3])\s*[：:]", body))
        shortfall = re.search(r"原文不足[：:]?.{0,80}?(\d+)\s*条可用原文", body)
        if len(quote_numbers) == 3:
            continue
        if shortfall:
            declared = int(shortfall.group(1))
            if declared >= 3 or declared != len(quote_numbers):
                errors.append(
                    f"{heading} has an invalid original-quote shortfall disclosure: "
                    f"declared={declared}, labeled={len(quote_numbers)}."
                )
            continue
        errors.append(
            f"{heading} must show three labeled original quotes or the required shortfall disclosure."
        )


def validate_section8_heading(root: ET.Element, errors: list[str]) -> None:
    section_nodes = top_level_section_nodes(root, "8. 各渠道专项分析")
    if not section_nodes:
        return
    headings = [text_of(node) for node in section_nodes if node.tag == "h2"]
    if GMAIL_SECTION_HEADING not in headings:
        errors.append(f"Section 8.1 must be titled exactly: {GMAIL_SECTION_HEADING}.")


def validate_callout_placement(root: ET.Element, errors: list[str]) -> None:
    """Allow callouts only in the opening core conclusion and Section 2."""
    children = list(root)
    first_h1_index = next(
        (index for index, node in enumerate(children) if node.tag == "h1"),
        len(children),
    )
    opening_callouts = [
        descendant
        for node in children[:first_h1_index]
        for descendant in node.iter()
        if descendant.tag == "callout"
    ]
    if len(opening_callouts) != 1:
        errors.append("Report must contain exactly one highlighted opening core conclusion.")
    elif "核心结论" not in text_of(opening_callouts[0]):
        errors.append("The opening callout must be the 核心结论 block.")
    else:
        conclusion = text_of(opening_callouts[0])
        if not re.search(r"\d+\s*/\s*\d+", conclusion):
            errors.append("The opening core conclusion must include n/N evidence.")
        if not re.search(r"优先|建议|应当|应该|需要|需先|立即", conclusion):
            errors.append("The opening core conclusion must state an immediate priority action.")

    allowed_ids = {id(node) for node in opening_callouts}
    for node in top_level_section_nodes(root, "2. 一句话结论"):
        allowed_ids.update(id(descendant) for descendant in node.iter() if descendant.tag == "callout")

    disallowed = [node for node in root.iter("callout") if id(node) not in allowed_ids]
    if disallowed:
        errors.append(
            "Callout/highlight boxes are allowed only in the opening core conclusion and Section 2."
        )


def validate_ai_case_volume(
    backend: dict,
    detail_tables: list[ET.Element],
    errors: list[str],
) -> None:
    if len(detail_tables) < 2:
        return
    denominator = backend.get("denominator", {})
    for media, table, denominator_key in (
        ("image", detail_tables[0], "image_events"),
        ("video", detail_tables[1], "video_events"),
    ):
        media_denominator = denominator.get(denominator_key, 0)
        if not isinstance(media_denominator, int) or media_denominator <= 0:
            continue
        for tag, metadata in backend.get(media, {}).items():
            source_count = metadata.get("count", 0)
            if not isinstance(source_count, int) or source_count <= 0:
                continue
            high_frequency = source_count / media_denominator >= 0.10
            required_min, allowed_max = (4, 5) if high_frequency else (2, 3)
            usable = metadata.get("usable_text_count", source_count)
            if not isinstance(usable, int) or usable < 0:
                errors.append(f"Backend Tag {media}.{tag} has invalid usable_text_count.")
                continue
            required_min = min(required_min, usable)
            allowed_max = min(allowed_max, usable)
            actual = count_tag_cases(table, tag)
            if actual < required_min or actual > allowed_max:
                label = "high-frequency" if high_frequency else "other non-zero"
                errors.append(
                    f"AI {media} Tag {tag} is {label} and needs {required_min}-{allowed_max} "
                    f"displayed cases, but the report has {actual}."
                )


def validate_xml(
    xml_text: str,
    backend: dict | None,
    allow_placeholders: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    if not allow_placeholders and re.search(r"\{\{[A-Z0-9_]+\}\}", xml_text):
        errors.append("Final XML contains unresolved {{PLACEHOLDER}} values.")
    if re.search(r"不是.{0,80}而是", xml_text, flags=re.S):
        errors.append("Report contains a prohibited 不是……而是…… construction.")
    if "暂不进入 Executive Summary 的原因" in xml_text:
        errors.append("Section 4 still explains exclusion from the Executive Summary instead of the concrete issue.")
    if re.search(r"等待.{0,20}(后台|登录).{0,20}补充", xml_text):
        errors.append("Report still contains a backend-completion placeholder.")

    try:
        root = ET.fromstring(f"<root>{xml_text}</root>")
    except ET.ParseError as exc:
        errors.append(f"Report XML is not well formed: {exc}.")
        return

    headings = [text_of(node) for node in root.findall(".//h1")]
    for required in REQUIRED_H1:
        if required not in headings:
            errors.append(f"Missing required top-level heading: {required}.")

    validate_section5_presentation(root, errors)
    validate_section8_heading(root, errors)
    validate_callout_placement(root, errors)

    tables = root.findall(".//table")
    table_headers: list[tuple[ET.Element, list[str]]] = []
    for table in tables:
        first = table.find("./thead/tr")
        if first is not None:
            table_headers.append((table, [text_of(cell) for cell in list(first)]))
    header_rows = [headers for _, headers in table_headers]
    if EXECUTIVE_HEADERS not in header_rows:
        errors.append("Executive Summary table does not have the exact seven required headers.")
    detail_tables = [table for table, headers in table_headers if headers == AI_HEADERS]
    if len(detail_tables) < 2:
        errors.append("Image and video AI-quality detail tables must both have the exact ten required headers.")
    if sum(headers == AI_TAG_HEADERS for headers in header_rows) < 2:
        errors.append("Image and video Tag frequency tables must both use the exact three required headers.")

    for table, headers in table_headers:
        if headers == EXECUTIVE_HEADERS:
            for row in table.findall("./tbody/tr"):
                cells = list(row)
                if len(cells) >= 7 and text_of(cells[6]):
                    errors.append("Executive Summary Team Comment cells must remain blank.")
                    break
        elif headers == AI_TAG_HEADERS:
            for row in table.findall("./tbody/tr"):
                cells = list(row)
                if len(cells) >= 3 and re.search(r"反馈事件分母\s*\d+", text_of(cells[2])):
                    errors.append("AI Tag frequency tables repeat denominator prose in the Tag meaning column.")
                    break
        elif headers == AI_HEADERS:
            for row in table.findall("./tbody/tr"):
                cells = list(row)
                if len(cells) < 10:
                    continue
                status = text_of(cells[9])
                if "Prompt：" in status or "Prompt:" in status:
                    errors.append("Character Sheet status is inferred from a prompt name instead of direct Snap verification.")
                    break
                if status.startswith(("是", "否")) and "Snap 详情" not in status:
                    errors.append("Character Sheet yes/no status must state that it was verified from the Snap detail.")
                    break

    images = [node for node in root.findall(".//img") if node.get("href") or node.get("src")]
    links = [node.get("href", "") for node in root.findall(".//a")]
    if backend:
        validate_ai_case_volume(backend, detail_tables, errors)
        denominator = backend.get("denominator", {})
        if denominator.get("image_events", 0) > 0 and not images:
            warnings.append("Backend has image events, but final XML contains no embedded image blocks.")
        if denominator.get("video_events", 0) > 0 and not any(
            link.lower().endswith(".mp4") or "video" in link.lower() for link in links
        ):
            warnings.append("Backend has video events, but no direct or identifiable video link was found.")

    if "%" in xml_text:
        percent_blocks = [text_of(node) for node in root.iter() if node.tag in {"p", "td"} and "%" in text_of(node)]
        for block in percent_blocks:
            if "/" not in block and "pp" not in block and "均分" not in block:
                warnings.append(f"Percentage may lack a local numerator/denominator: {block[:100]}")


def main() -> None:
    args = parse_args()
    if not any((args.feedback_json, args.previous_feedback_json, args.analysis_json, args.backend_json, args.report_xml)):
        raise SystemExit(
            "Provide at least one of --feedback-json, --previous-feedback-json, --analysis-json, "
            "--backend-json, or --report-xml"
        )

    errors: list[str] = []
    warnings: list[str] = []
    backend = None
    feedback = None

    if args.feedback_json:
        feedback = load_json(args.feedback_json)
        validate_feedback(feedback, errors, warnings)
    if args.previous_feedback_json:
        previous_feedback = load_json(args.previous_feedback_json)
        validate_feedback(previous_feedback, errors, warnings)
        if feedback is not None:
            validate_period_pair(feedback, previous_feedback, errors)
    if args.analysis_json:
        if feedback is None:
            errors.append("--analysis-json requires --feedback-json for exact coverage validation.")
        else:
            validate_analysis_manifest(feedback, load_json(args.analysis_json), errors, warnings)
    if args.backend_json:
        backend = load_json(args.backend_json)
        validate_backend(backend, errors, warnings)
    if args.report_xml:
        if args.feedback_json and not args.previous_feedback_json and not args.skip_wow_reason:
            errors.append(
                "Final validation requires --previous-feedback-json for the default week-over-week check, "
                "or --skip-wow-reason with a concrete incompatibility."
            )
        if args.feedback_json and not args.analysis_json:
            errors.append("Final validation requires --analysis-json to prove full ordinary-feedback coverage.")
        xml_text = Path(args.report_xml).read_text(encoding="utf-8")
        validate_xml(xml_text, backend, args.allow_placeholders, errors, warnings)

    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": list(dict.fromkeys(warnings)),
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
