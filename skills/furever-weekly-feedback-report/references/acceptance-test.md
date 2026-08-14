# Skill acceptance test

Test in a fresh Codex task after restarting Codex. A fresh task prevents the agent from relying on the conversation that created the Skill.

## Stage 1 — Trigger and no-write smoke test

Send this prompt:

> 使用 $furever-weekly-feedback-report，以 2026-07-27 至 2026-08-02 作为回归测试周期。先完成权限检查、数据范围确认和写作方案，只给方案，不创建或修改任何飞书文档。不要依赖当前任务之外的对话信息。

Pass when Codex:

- Loads the Skill automatically.
- Uses the supplied date range and `Asia/Shanghai`.
- Names Feedback Collection and backend AI feedback as separate sources.
- Includes the Gmail table in Feedback Collection as ordinary feedback without requiring direct mailbox access.
- Pulls both the test week and the immediately preceding week for comparable metrics.
- Separates in-period Gmail user messages from support replies and historical messages inside the same thread.
- Checks Feishu and backend access.
- Presents a plan and stops before creating a document.
- Does not invent temporary special-focus sections that were not requested.

Known regression checkpoints for this historical week:

- Live Feedback Collection at the latest verification: Typeform 31 and App Store 19. The App Store sum is 86 rating points, so the mean is `86/19 = 4.53`.
- An earlier frozen local export contained 16 App Store reviews. Three later/backfilled five-star records dated August 2 were subsequently present in the live Base: Review IDs `14378228273`, `14378489091`, and `14379114480`.
- Discord has one collected row whose reporting-period timestamp is not verifiable; it must be disclosed, excluded from period totals, and omitted as a Section 8 subsection.
- Backend typed-media denominators: 125 image events and 149 video events. A prior all-events audit also contained one event without a media type.

Treat live sources as authoritative. If a historical count changes, reconcile it by source-native IDs and timestamps instead of forcing the frozen checkpoint. These checkpoints test collection and scope; they do not prescribe the wording of conclusions.

Gmail parser regression checkpoint: for the single-day range `2026-08-03`, the live Base snapshot verified on 2026-08-11 returned 18 deduplicated Gmail thread rows, but only 9 contained an August 3 user-authored message. The other 9 were support-only updates to older user messages and must remain audit rows with `_analysis_eligible=false`. If the live Base later changes, inspect the message headers and sender addresses rather than forcing these counts.

Flexible-header regression checkpoint: for `2026-08-03` through `2026-08-09`, the live Base snapshot verified on 2026-08-13 returned 70 deduplicated Gmail threads. The formal collector must support both named-angle and bare-email headers, exclude system-template-only markers, and produce 51 analysis-eligible Gmail records without a separate normalization script. Together with Typeform 3 and App Store 22, the ordinary-feedback total is 76; Discord remains excluded. Applying the same parser to `2026-07-27` through `2026-08-02` produces Gmail 37 and an ordinary-feedback total of 87. This corrects the temporary normalizer's earlier 36/86 result, which missed a thread containing bare user headers followed by a named-angle support header. Treat later live-source changes as reconcilable by source-native IDs rather than forcing these frozen counts.

## Stage 2 — Full document test

After reviewing Stage 1, send:

> 方案通过。请新建一份测试文档，标题以【Skill 回归测试】开头，不得修改任何历史周报。完成后返回文档链接、自动校验结果和仍未解决的数据限制。

Pass when the output:

1. Creates a new Feishu document.
2. Contains all eight required top-level sections.
3. Matches the approved structure for Sections 2 and 3.
4. Shows numerator and denominator for percentages.
5. Keeps ordinary feedback and backend AI-quality totals separate.
6. Uses backend data only for AI image/video quality.
7. Separates image and video original-Tag frequency tables.
8. Includes all ten required AI-detail fields.
9. Displays input and generated images directly in the document.
10. Keeps generated-video and backend-record links clickable.
11. Leaves `Team Comment` blank.
12. Includes Gmail ordinary feedback, while using backend records only for the AI image/video section.
13. Uses `补充观察与趋势信号` for Section 4 without duplicating Section 5.
14. Uses the three required AI Tag frequency columns and does not repeat denominator prose in every row.
15. Uses no unresolved placeholders and returns the new document link and validator result.
16. Uses the corrected approved report `Yz4Md3VrmoPlbexGmlRc5u4Bnag` as the canonical Section 2/3 reference.
17. Includes an analysis manifest with exact coverage of every eligible ordinary-feedback record and every issue in multi-issue records.
18. Applies the approved priority/severity definitions; high frequency alone does not create `S1`.
19. Shows 4–5 cases for each AI Tag at or above 10% of its media denominator and 2–3 for every other non-zero Tag, with explicit disclosure when too few usable user texts exist.
20. Uses `https://admin.fureverworld.com/dashboard/feedback` as the backend source.
21. Uses the exact Gmail subsection title `8.1 Gmail｜主要反馈主题与代表原文`.
22. Uses no callout/highlight boxes inside Section 5.
23. Shows exactly three labeled original quotes for each P1/P2 issue when available; otherwise shows every available quote and the required shortfall disclosure.
24. Keeps one highlighted opening core conclusion that identifies a single weekly priority with `n/N` evidence, impact, and an immediate action.
25. Uses callout/highlight boxes only in the opening core conclusion and Section 2; Sections 1 and 3–8 contain no callouts.

Do not require the test report's prose to match a historical report word for word. Judge evidence, structure, counts, media rendering, and traceability.

## Stage 3 — New-intern handoff test

Run Stages 1 and 2 from the intern's own account and device. This tests the handoff package plus permissions.

Classify failures:

- `Access failure`: the Skill identifies a missing Base, document, folder, backend page, media URL, or authorization scope.
- `Workflow failure`: the agent writes before approval, reuses an old document, or skips validation.
- `Data failure`: counts, dates, deduplication, denominators, or source boundaries are wrong.
- `Presentation failure`: Sections 2/3 differ from the approved structure, images are link-only, or required columns are missing.
- `Analysis failure`: claims are unsupported, examples cannot be traced, or limitations are hidden.

## Automated regression commands

Run the dependency-free regressions first:

```bash
python3 scripts/self_test.py
```

Create the current-week coverage scaffold, then fill every category and issue summary:

```bash
python3 scripts/create_analysis_manifest.py \
  --feedback-json current-feedback.json \
  --output ordinary-analysis.json
```

For current and previous ordinary-feedback exports plus the classification manifest:

```bash
python3 scripts/validate_weekly_report.py \
  --feedback-json current-feedback.json \
  --previous-feedback-json previous-feedback.json \
  --analysis-json ordinary-analysis.json \
  --backend-json backend-ai.json
```

For the completed document XML, rerun the same command and add `--report-xml final-report.xml`. The final run must return `"ok": true` before the document is handed to the reviewer.

Fix the Skill only for recurring workflow failures. Keep one-week content preferences in the weekly prompt or plan.
