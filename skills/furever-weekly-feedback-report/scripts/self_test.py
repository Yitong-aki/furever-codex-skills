#!/usr/bin/env python3
"""Dependency-free regression checks for the Furever weekly-report Skill."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from datetime import date

from collect_feedback_collection import extract_gmail_analysis_text
from validate_weekly_report import (
    validate_ai_case_volume,
    validate_analysis_manifest,
    validate_feedback,
    validate_callout_placement,
    validate_period_pair,
    validate_section5_presentation,
    validate_section8_heading,
)


class GmailFilteringTest(unittest.TestCase):
    def test_keeps_only_in_period_user_messages(self) -> None:
        row = {
            "Gmail": "user@example.com",
            "Feedback": (
                "[7/31 09:00] User <user@example.com>:\nold issue\n\n----------------------\n\n"
                "[8/3 10:00] Support <support@example.com>:\nreply\n\n----------------------\n\n"
                "[8/3 11:00] User <user@example.com>:\ncurrent issue"
            ),
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 8, 3), date(2026, 8, 9)
        )
        self.assertEqual(reason, None)
        self.assertEqual(text, "current issue")

    def test_support_only_update_is_ineligible(self) -> None:
        row = {
            "Gmail": "user@example.com",
            "Feedback": (
                "[7/31 09:00] User <user@example.com>:\nold issue\n\n----------------------\n\n"
                "[8/3 10:00] Support <support@example.com>:\nreply"
            ),
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 8, 3), date(2026, 8, 9)
        )
        self.assertEqual(text, "")
        self.assertEqual(reason, "no_in_period_user_message")

    def test_bare_email_header_is_supported(self) -> None:
        row = {
            "Gmail": "user@example.com",
            "Feedback": (
                "[8/5 07:08] user@example.com:\ncurrent issue\n\n----------------------\n\n"
                "[8/5 07:20] support@fureverworld.com:\nsupport reply"
            ),
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 8, 3), date(2026, 8, 9)
        )
        self.assertEqual(reason, None)
        self.assertEqual(text, "current issue")

    def test_bare_user_header_is_kept_when_support_uses_named_angle_header(self) -> None:
        row = {
            "Gmail": "user@example.com",
            "Feedback": (
                "[7/31 01:10] user@example.com:\ncurrent issue\n\n----------------------\n\n"
                "[7/31 15:47] Support <support@fureverworld.com>:\nsupport reply"
            ),
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 7, 27), date(2026, 8, 2)
        )
        self.assertEqual(reason, None)
        self.assertEqual(text, "current issue")

    def test_sender_comparison_is_case_insensitive(self) -> None:
        row = {
            "Gmail": "User@Example.com",
            "Feedback": "[8/7 12:30] user@example.com:\nCase-insensitive match.",
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 8, 3), date(2026, 8, 9)
        )
        self.assertEqual(reason, None)
        self.assertEqual(text, "Case-insensitive match.")

    def test_system_template_only_is_ineligible(self) -> None:
        row = {
            "Gmail": "user@example.com",
            "Feedback": "[8/7 12:30] user@example.com:\n（仅包含系统模板或引用，无手写正文）",
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 8, 3), date(2026, 8, 9)
        )
        self.assertEqual(text, "")
        self.assertEqual(reason, "system_template_or_quote_only")

    def test_template_marker_does_not_remove_real_message(self) -> None:
        row = {
            "Gmail": "user@example.com",
            "Feedback": (
                "[8/7 12:30] user@example.com:\n（仅包含系统模板或引用，无手写正文）\n\n"
                "----------------------\n\n"
                "[8/8 09:10] user@example.com:\nPlease fix my missing treats."
            ),
        }
        text, reason = extract_gmail_analysis_text(
            row, date(2026, 8, 3), date(2026, 8, 9)
        )
        self.assertEqual(reason, None)
        self.assertEqual(text, "Please fix my missing treats.")


class CoverageManifestTest(unittest.TestCase):
    def test_exact_coverage_passes(self) -> None:
        feedback = {
            "channels": {
                "Gmail": [
                    {"_analysis_record_id": "Gmail:1", "_analysis_eligible": True},
                    {"_analysis_record_id": "Gmail:2", "_analysis_eligible": False},
                ]
            }
        }
        analysis = {
            "records": [
                {
                    "record_id": "Gmail:1",
                    "issues": [
                        {
                            "categories": ["核心流程与稳定性"],
                            "summary": "生成结果一直停留在处理中",
                        }
                    ],
                }
            ]
        }
        errors: list[str] = []
        warnings: list[str] = []
        validate_analysis_manifest(feedback, analysis, errors, warnings)
        self.assertEqual(errors, [])

    def test_missing_record_fails(self) -> None:
        feedback = {
            "channels": {
                "Gmail": [
                    {"_analysis_record_id": "Gmail:1", "_analysis_eligible": True}
                ]
            }
        }
        errors: list[str] = []
        validate_analysis_manifest(feedback, {"records": []}, errors, [])
        self.assertTrue(any("missing" in error for error in errors))

    def test_validator_rejects_eligible_system_template(self) -> None:
        payload = {
            "source": {
                "period_start": "2026-08-03 00:00:00",
                "period_end": "2026-08-09 23:59:59",
            },
            "channels": {
                "Gmail": [
                    {
                        "_analysis_record_id": "Gmail:1",
                        "_analysis_eligible": True,
                        "_analysis_text": "（仅包含系统模板或引用，无手写正文）",
                        "_period_verified": True,
                    }
                ],
                "Typeform": [],
                "App Store": [],
                "Discord": [],
            },
            "counts": {"Gmail": 1, "Typeform": 0, "App Store": 0, "Discord": 0},
            "raw_counts": {"Gmail": 1, "Typeform": 0, "App Store": 0, "Discord": 0},
            "analysis_counts": {"Gmail": 1, "Typeform": 0, "App Store": 0, "Discord": 0},
            "ordinary_total": 1,
        }
        errors: list[str] = []
        validate_feedback(payload, errors, [])
        self.assertTrue(any("system-template-only" in error for error in errors))


class AiCaseVolumeTest(unittest.TestCase):
    @staticmethod
    def detail_table(tag: str, rows: int) -> ET.Element:
        body = "".join(
            "<tr>" + "".join(f"<td>{tag if column == 4 else 'x'}</td>" for column in range(10)) + "</tr>"
            for _ in range(rows)
        )
        return ET.fromstring(f"<table><tbody>{body}</tbody></table>")

    def test_high_frequency_tag_needs_four_cases(self) -> None:
        backend = {
            "denominator": {"image_events": 20, "video_events": 0},
            "image": {"Motion": {"count": 4, "usable_text_count": 4}},
            "video": {},
        }
        errors: list[str] = []
        validate_ai_case_volume(
            backend,
            [self.detail_table("Motion", 3), self.detail_table("unused", 0)],
            errors,
        )
        self.assertTrue(any("needs 4-4" in error for error in errors))

        errors = []
        validate_ai_case_volume(
            backend,
            [self.detail_table("Motion", 4), self.detail_table("unused", 0)],
            errors,
        )
        self.assertEqual(errors, [])


class PeriodPairTest(unittest.TestCase):
    def test_adjacent_equal_periods_pass(self) -> None:
        current = {"source": {"period_start": "2026-08-03 00:00:00", "period_end": "2026-08-09 23:59:59"}}
        previous = {"source": {"period_start": "2026-07-27 00:00:00", "period_end": "2026-08-02 23:59:59"}}
        errors: list[str] = []
        validate_period_pair(current, previous, errors)
        self.assertEqual(errors, [])


class ReportPresentationTest(unittest.TestCase):
    def test_section5_accepts_three_quotes_without_callout(self) -> None:
        root = ET.fromstring(
            "<root><h1>5. P1–P2 深度问题分析</h1><h2>5.1 P1｜问题</h2>"
            "<p>用户原文 1：one</p><p>用户原文 2：two</p><p>用户原文 3：three</p>"
            "<h1>6. AI 生成质量专项分析</h1></root>"
        )
        errors: list[str] = []
        validate_section5_presentation(root, errors)
        self.assertEqual(errors, [])

    def test_section5_rejects_callout_and_one_quote_without_shortfall(self) -> None:
        root = ET.fromstring(
            "<root><h1>5. P1–P2 深度问题分析</h1><h2>5.1 P1｜问题</h2>"
            "<callout><p>用户原文 1：one</p></callout>"
            "<h1>6. AI 生成质量专项分析</h1></root>"
        )
        errors: list[str] = []
        validate_section5_presentation(root, errors)
        self.assertTrue(any("callout" in error for error in errors))
        self.assertTrue(any("three labeled" in error for error in errors))

    def test_section5_accepts_declared_shortfall(self) -> None:
        root = ET.fromstring(
            "<root><h1>5. P1–P2 深度问题分析</h1><h2>5.1 P1｜问题</h2>"
            "<p>用户原文 1：one</p>"
            "<p>原文不足：本周期仅找到 1 条可用原文。</p>"
            "<h1>6. AI 生成质量专项分析</h1></root>"
        )
        errors: list[str] = []
        validate_section5_presentation(root, errors)
        self.assertEqual(errors, [])

    def test_section8_requires_approved_gmail_title(self) -> None:
        root = ET.fromstring(
            "<root><h1>8. 各渠道专项分析</h1>"
            "<h2>8.1 主动问题与高情绪反馈</h2></root>"
        )
        errors: list[str] = []
        validate_section8_heading(root, errors)
        self.assertTrue(any("Section 8.1" in error for error in errors))

    def test_callouts_are_allowed_only_at_opening_and_in_section2(self) -> None:
        root = ET.fromstring(
            "<root><callout><p>核心结论：首要问题 3/10，建议优先处理。</p></callout>"
            "<h1>1. 数据来源与样本概览</h1><p>范围</p>"
            "<h1>2. 一句话结论</h1><callout><p>一句话结论</p></callout>"
            "<grid><column><callout><p>指标卡</p></callout></column></grid>"
            "<h1>3. Executive Summary</h1><p>正文</p></root>"
        )
        errors: list[str] = []
        validate_callout_placement(root, errors)
        self.assertEqual(errors, [])

    def test_callout_outside_section2_is_rejected(self) -> None:
        root = ET.fromstring(
            "<root><callout><p>核心结论：首要问题 3/10，建议优先处理。</p></callout>"
            "<h1>1. 数据来源与样本概览</h1><callout><p>口径提醒</p></callout>"
            "<h1>2. 一句话结论</h1><callout><p>一句话结论</p></callout>"
            "<h1>3. Executive Summary</h1></root>"
        )
        errors: list[str] = []
        validate_callout_placement(root, errors)
        self.assertTrue(any("allowed only" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
