# Approved report requirements

## Reference precedence

1. The user's latest explicit instruction.
2. Overall structure and Sections 2–3: [corrected approved Feishu report](https://jcnreneadm7i.feishu.cn/docx/Yz4Md3VrmoPlbexGmlRc5u4Bnag).
3. General formatting: `Furever 每周用户反馈周报 (06.29-07.05).pdf` when supplied.
4. AI image/video presentation: `Furever用户反馈周报（6.01-6.07）.pdf` when supplied.

Do not require historical PDFs when their formatting rules are already captured below.

## Opening core conclusion

- Keep one highlighted `核心结论` block at the very beginning of the document, before Section 1.
- Name the single feedback issue or opportunity that deserves the most attention that week. Support it with an `n/N` evidence point, state why it matters to the user or business, and give the immediate priority action.
- Do not use the opening conclusion merely to list total feedback, the top three risks, or the leading backend Tags. A reader should understand the week's primary priority at a glance.
- Outside this opening block, callout/highlight boxes are allowed only inside Section 2. Use plain paragraphs, lists, or tables in Sections 1 and 3–8.

## Required document outline

1. 数据来源与样本概览
2. 一句话结论
3. Executive Summary
4. 补充观察与趋势信号
5. P1–P2 深度问题分析
6. AI 生成质量专项分析
7. 功能诉求与机会点
8. 各渠道专项分析

Add temporary subsections under Section 4 only when the user requests a special focus for that reporting week or the proposed plan explicitly includes one. Do not preserve a prior week's special-focus section by default.

## Section 1 — Sources and sample

- Show reporting dates, timezone, included channels, exclusions, raw records, deduplicated records, and unique users when available.
- State the unit used in each downstream metric.
- Keep ordinary-feedback totals separate from backend AI-quality event totals.
- Pull the immediately preceding week by default. Show week-over-week change only for compatible metrics; do not compare changed questions, options, channel scope, or denominator definitions.

## Section 2 — 一句话结论

Use this order:

1. Yellow warning callout containing one evidence-led sentence.
2. Three metric cards: valid feedback count, App Store mean, and the most decision-relevant comparable experience metric.
3. A short `综合判断` paragraph.

Every percentage in the sentence or cards must be backed by a numerator and denominator elsewhere in the same section or an immediately adjacent note. Use one decimal place.

Do not use `本周不是……而是……` or similar contrast rhetoric.

## Section 3 — Executive Summary

Use exactly seven columns:

| 优先级 | 严重度 | 具体问题 / 机会 | 去重数 / 占比 | 证据 | 影响 | Team Comment |
|---|---|---|---|---|---|---|

Rules:

- Sort by priority and decision value.
- Use P1/P2 and S1/S2/S3 consistently.
- Put exact counts, denominators, percentages, sources, and overlap notes in `去重数 / 占比`.
- Use `证据` for strength such as 强/中强/中; do not use it for unsupported adjectives.
- Describe concrete product or emotional impact.
- Leave `Team Comment` blank.

Priority and severity are separate judgments:

- `P1`: action is required this week because the issue threatens the core experience, payment/entitlement, trust, or is a severe/high-frequency failure.
- `P2`: important improvement or opportunity, but immediate action is not required.
- `S1`: high severity; the core promise or paid entitlement fails, the product becomes unusable, or emotional harm is substantial.
- `S2`: medium severity; there is clear user impact, but the product remains usable or a workaround exists.
- `S3`: low severity; preference, minor friction, or isolated low-impact issue.
- Frequency alone never upgrades an issue to `S1`.

## Section 4 — Supplementary observations and trend signals

- Use this section for valuable signals that were not selected as P1/P2 issues.
- For each item, state the concrete product or experience problem and show its evidence/sample.
- Include a representative original quote when available.
- Do not fill the section with explanations of why an item did not enter the Executive Summary.
- Do not repeat the full frequency, impact, and action analysis from Section 5.
- When there is no suitable supplementary signal, keep the heading and state this briefly instead of inventing content.

## Section 5 — P1/P2 deep analysis

For each issue include:

- What happened.
- Frequency and denominator.
- Exactly three distinct representative original quotes when at least three usable quotes exist.
- When fewer than three usable quotes exist, show every available quote and state `原文不足：本周期仅找到 n 条可用原文。` in the same issue.
- Affected workflow or user promise.
- User and business impact.
- Evidence-backed priority.
- A concrete next investigation or product action.

Label the quotes `用户原文 1：`, `用户原文 2：`, and `用户原文 3：` so the final report can be checked automatically. Use plain paragraphs or lists for the entire section. Do not use callout/highlight boxes inside Section 5.

Avoid generic root causes such as “AI is unstable” unless technical evidence supports them.

## Section 6 — AI quality

Begin with a plain-text data-boundary paragraph. Then show:

1. Image original-Tag frequency table.
2. Video original-Tag frequency table.
3. Image detail table with 4–5 original-text cases for each high-frequency Tag and 2–3 for every other non-zero Tag.
4. Video detail table with 4–5 original-text cases for each high-frequency Tag and 2–3 for every other non-zero Tag.

Use exactly three columns in both Tag frequency tables: `后台原始 Tag`, `记录数 / 占比`, and `Tag 含义`. Put each image/video denominator in the data-boundary text and in the `n/N` values; do not repeat a denominator description in every row.

Include the exact ten fields from the data contract. Embed input/output images directly inside cells. Keep backend and media links clickable. Verify Character Sheet from the Snap detail rather than a prompt name, and state the direct-verification result.

Define a high-frequency Tag as `n/N >= 10.0%` inside the image or video denominator. When a Tag has fewer usable original-text records than the required display count, show all available records and state the source limitation. One multi-tag record may support each Tag it contains, but it must remain one visible record.

## Sections 7–8

- Section 7: consolidate product opportunities without repeating all evidence. Link each opportunity to a finding and expected user outcome.
- Section 8: summarize Gmail, Typeform, App Store, and Discord separately when the channel has period-verifiable data. Title the Gmail subsection exactly `8.1 Gmail｜主要反馈主题与代表原文`. Keep backend AI-quality analysis in Section 6. Adjust channel depth to the current week's approved plan.

## Tone and language

- Write in concise Chinese; preserve English user quotes verbatim.
- Prefer concrete nouns and counts over dramatic phrasing.
- Avoid `不是……而是……` constructions.
- Avoid asserting causality from week-over-week movement in small, different samples.
- Call a limitation a limitation; do not conceal it in a footnote.
