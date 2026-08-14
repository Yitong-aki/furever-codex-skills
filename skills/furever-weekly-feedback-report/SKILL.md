---
name: furever-weekly-feedback-report
description: Create, audit, test, or hand off Furever's weekly user-feedback report using Gmail, Typeform, App Store, and Discord records from Feedback Collection plus Furever backend AI-quality feedback. Use when Codex is asked to plan or produce the previous Monday-Sunday report, reproduce the approved Feishu structure, build image/video Tag tables, verify weekly metrics, address reviewer comments, check access prerequisites, or prepare the workflow for a new intern.
---

# Furever Weekly Feedback Report

Produce a review-ready internal Feishu report whose claims are traceable to raw records. Treat the reporting process as evidence work: collect, validate, count, interpret, publish, and audit.

## End-to-end workflow

### Scope and access

1. Determine the reporting week as the previous Monday 00:00:00 through Sunday 23:59:59 in `Asia/Shanghai`, unless the user gives another range.
2. On first use or handoff, read [references/access-setup.md](references/access-setup.md) and verify access before promising delivery.
3. Read [references/data-contract.md](references/data-contract.md) before collecting data.

### Collect and validate

4. Collect read-only ordinary-feedback data for both the reporting week and the immediately preceding week, plus reporting-week backend AI-quality data, into a new weekly work directory. Never overwrite a prior week's raw export.
5. Run `scripts/validate_weekly_report.py` in input-only mode for both ordinary-feedback exports and the backend export before analysis.
6. Read [references/report-requirements.md](references/report-requirements.md) and [references/ordinary-taxonomy.md](references/ordinary-taxonomy.md), then run `scripts/create_analysis_manifest.py` for the current week. Fill every manifest record before calculating metrics or drafting claims, and run the validator with `--analysis-json` to prove exact coverage.

### Plan and analyze

7. Present a concise proposed outline, data scope, and analysis plan. Include any special focus requested for that week. Wait for the user's explicit approval before creating or editing a Feishu document, unless the user explicitly waived this checkpoint in the same request.
8. Analyze from frequency to examples to priority. Treat weekly special-focus questions as temporary instructions; do not turn them into permanent recurring sections.

### Publish and hand off

9. Read [references/lark-publishing.md](references/lark-publishing.md) before creating the document. Start from [assets/report-template.xml](assets/report-template.xml), and create a new Feishu document.
10. Embed AI input and output images directly in the document. Keep video URLs clickable.
11. Run `scripts/validate_weekly_report.py` again with the final XML before handing the document to the reviewer.
12. Send only the new document link and a short note on scope, unresolved data gaps, and checks performed. The user reviews and decides whether to forward it.

## Data boundaries and evidence standards

### Source boundary

- Use the `Feedback Collection` Base for Gmail, Typeform, App Store, and Discord records.
- Treat Gmail records in Feedback Collection as ordinary user feedback. Within a synchronized thread, count only user-authored messages dated inside the reporting period; support replies and older user messages are context only. Direct access to the Gmail mailbox is not required.
- Use `https://admin.fureverworld.com/dashboard/feedback` as the canonical backend source and the only source for the AI image/video quality section.
- Never substitute Gmail or other ordinary feedback for inaccessible backend AI-quality data. State the limitation and request a backend export with the required fields.
- Preserve backend original Tags exactly. Add a Chinese interpretation only in a separate column or sentence.

### Quantitative evidence

- Show numerator and denominator for every percentage: `11/17 (64.7%)`.
- Distinguish records, unique users, and responses. Do not combine them into one count.
- Deduplicate using the source-native identifier specified in the data contract.
- For multi-select Tags, state that one event can enter multiple Tags and that percentages do not sum to 100%.
- Pull the immediately preceding week by default. Compare week over week only when question wording, response options, source scope, and denominator definition match; otherwise show the current value and name the incompatibility.
- Treat small samples as directional. Include the exact sample size.

### Examples and priority evidence

- Use verbatim user text for examples, with email addresses and direct personal identifiers removed. Do not invent or translate text as though it were original.
- Make priority judgments from frequency, severity, emotional harm, payment/trust risk, and recurrence. Do not rank from intuition alone.
- Use the approved definitions: `P1` requires action this week because the issue threatens the core experience, payment/entitlement, trust, or causes a severe/high-frequency failure; `P2` is an important improvement or opportunity that does not require immediate action. Severity is independent: `S1` is high severity (core promise or paid entitlement fails, the product becomes unusable, or emotional harm is substantial), `S2` is medium severity (clear user impact but the product remains usable or a workaround exists), and `S3` is low severity (preference, minor friction, or isolated low-impact issue). High frequency alone does not make an issue `S1`.

## Ordinary-feedback analysis

### Coverage and classification

First create an ordinary-feedback analysis manifest. Every eligible record must appear exactly once in the manifest, and every distinct issue inside a multi-issue record must be summarized and mapped to one or more stable top-level categories from the ordinary taxonomy. A record may enter multiple categories; do not discard lower-frequency issues merely because a more important issue is present.

### Important-issue analysis

For each important issue:

1. Count the frequency with a defined unit and denominator.
2. Select representative original examples.
3. Explain the observable pattern and user impact.
4. Assign P1/P2 only when evidence supports it.
5. Keep inferred causes explicitly labeled as hypotheses.

### Weekly special investigations

For any special investigation requested that week, define its evidence rule in the proposed plan and apply it only to that report. Keep the core report useful even when no special investigation is requested.

### Section 4 and Section 5 boundaries

Keep Sections 4 and 5 distinct:

- Section 4 is an observation area for valuable signals that are not selected as P1/P2. State the concrete issue and include a representative original quote when available. Do not explain why the item was excluded from the Executive Summary. If no suitable signal exists, keep the heading and state that no supplementary signal was identified; do not invent content.
- Section 5 contains only selected P1/P2 issues and expands frequency, evidence, affected user promise, impact, and next action. Do not duplicate the same analysis in Section 4.

## AI-quality analysis and presentation

### Count Tags and select records

1. Separate image and video feedback.
2. Count original backend Tags first, using image events and video events as separate denominators.
3. Use exactly three columns in each frequency table: `后台原始 Tag`, `记录数 / 占比`, and `Tag 含义`. State each media denominator once in the data-boundary text; do not repeat the same denominator sentence down the third column.
4. Define a high-frequency Tag as `n/N >= 10.0%` within its own media denominator. For every non-zero Tag with usable user text, show 4–5 representative records for a high-frequency Tag and 2–3 for every other Tag. If the source contains fewer usable text records than the target, show all available records and disclose the shortfall.

### Detail-table schema

5. Include exactly these fields in each detail table:
   - User ID
   - Snap/Generation ID
   - 图片或视频 link
   - Snap Type
   - 后台原始 Tag
   - 用户原文
   - 用户输入原图
   - AI 生成图片
   - AI 生成视频
   - 是否有 character sheet

### Media display and Character Sheet verification

6. Display `用户输入原图` and `AI 生成图片` as inline images. A text link alone does not satisfy this requirement.
7. Display the video as a clickable direct-media or backend link.
8. Mark character-sheet status only after opening the Snap detail and directly verifying whether Character Sheet appears as an identity reference. Do not infer it from prompt names or Snap Type. Write `是（Snap 详情显示 Character Sheet 作为 Identity Reference）`, `否（Snap 详情未显示 Character Sheet）`, or `unknown（说明无法核验的原因）`.

## Report writing and review constraints

- Follow the approved Feishu outline and exact Section 2/3 structures in the report requirements.
- Use `4. 补充观察与趋势信号` for Section 4 and apply the Section 4/5 separation defined above.
- Leave `Team Comment` cells blank for the company team.
- Keep prose concise, neutral, and evidence-led.
- Avoid the rhetorical construction `本周不是……而是……` and similar `不是……而是……` summary sentences.
- Do not write a conclusion that exceeds the evidence.
- Do not delete reviewer comments. Resolve the underlying issue and let the reviewer remove comments.
- Create a new weekly document; never recycle the prior week's document.

## Failure handling

- If access fails, exhaust read-only checks and report the exact missing source or field.
- If backend data cannot be obtained, do not fabricate Section 6. Provide the required export schema from the data contract.
- If an image cannot be embedded, retain the URL, mark the row as an embedding failure, and disclose it before handoff.
- If a metric cannot be compared, show the current period only and state why.
- If the user asks only to investigate, remain read-only and return findings without editing the report.

## Reusable resources

- `scripts/collect_feedback_collection.py`: parameterized, read-only collector for Gmail, Typeform, App Store, and Discord tables in Feedback Collection; it extracts only in-period user-authored Gmail messages for analysis.
- `scripts/create_analysis_manifest.py`: creates a non-overwriting, full-coverage classification scaffold from all analysis-eligible ordinary feedback.
- `scripts/validate_weekly_report.py`: input and final-XML quality gate.
- `scripts/self_test.py`: dependency-free parser and coverage regressions.
- `references/data-contract.md`: sources, identifiers, required fields, and deduplication rules.
- `references/ordinary-taxonomy.md`: stable ordinary-feedback categories and the full-coverage analysis manifest.
- `references/report-requirements.md`: approved structure, metric semantics, and analysis rules.
- `references/lark-publishing.md`: Feishu creation and media rules.
- `references/access-setup.md`: minimum Feishu and Furever backend access for a new operator.
- `references/acceptance-test.md`: fresh-session smoke test and full regression-test procedure.
- `assets/report-template.xml`: reusable Feishu XML skeleton.
