# Feishu publishing runbook

## Before writing

1. Confirm that the user approved the proposed plan.
2. Read the `lark-doc` and `lark-shared` Skills available in the current environment.
3. Fetch the approved reference outline and Sections 2–3 when access is available.
4. Copy `assets/report-template.xml` into the new weekly work directory.
5. Replace every `{{PLACEHOLDER}}`; do not upload a template containing unresolved placeholders.

## Create a new document

- Always create a new Feishu document for the reporting week.
- Use user identity and the current v2 document API.
- Use XML unless the user explicitly requests Markdown.
- Title pattern: `Furever 用户反馈周报｜YYYY.MM.DD–MM.DD`.
- Do not overwrite or recycle the prior-week document.

## Images and video

- Embed a remote image with `<img href="https://..." caption="..."/>`.
- Put user input and AI output images directly in the AI-quality detail row.
- Keep the direct media and backend record links in the link cell even when images are embedded.
- Use a clickable `<a href="...">播放生成视频</a>` for video.
- If Feishu cannot fetch a remote image, download it into the current work directory and use the document media insertion workflow. Record the failed URL in the audit.

## Tables

- Use explicit `colgroup` widths.
- Use gray table headers and top-aligned cells.
- Keep the seven Executive Summary columns unchanged.
- Keep the ten AI-quality detail columns unchanged.
- For wide AI-quality tables, use compact text and small image widths; do not remove required columns to make the table fit.

## Comments and revisions

- Never delete reviewer comments.
- When asked to address a comment, change the underlying content while leaving the comment intact.
- Create or update only after explicit authorization.
- If asked only to inspect comments or data, remain read-only.

## Final verification

1. Fetch the new document outline and confirm all eight top-level sections.
2. Fetch Sections 2, 3, and 6 with IDs and inspect their actual rendered block structure.
3. Confirm image blocks exist in Section 6 and video links are clickable.
4. Confirm all percentages show or trace to `n/N` denominators.
5. Confirm Gmail ordinary feedback includes only in-period user-authored messages and is not being used as backend AI-quality evidence.
6. Confirm Section 4 is titled `补充观察与趋势信号`, contains concrete issues, and does not duplicate the P1/P2 analysis.
7. Confirm both AI Tag frequency tables use exactly three columns: `后台原始 Tag`, `记录数 / 占比`, and `Tag 含义`.
8. Confirm no `不是……而是……` summary sentence remains.
9. Confirm every eligible ordinary-feedback record appears in the analysis manifest and every distinct issue has a concrete summary.
10. Confirm every high-frequency AI Tag has 4–5 displayed cases and every other non-zero Tag has 2–3, or a visible source-shortfall disclosure.
11. Omit the Discord subsection when its period cannot be verified; do not publish an empty or out-of-period Discord section.
12. Confirm Section 5 contains no callout/highlight boxes and every P1/P2 issue shows exactly three labeled original quotes, or all available quotes plus the required shortfall disclosure.
13. Confirm Section 8.1 is titled `8.1 Gmail｜主要反馈主题与代表原文`.
14. Confirm the opening highlighted `核心结论` identifies one primary weekly priority with `n/N` evidence, impact, and an immediate action.
15. Confirm all callout/highlight boxes are confined to the opening core conclusion and Section 2; use plain text in Sections 1 and 3–8.
16. Send the document link to the reviewer; do not send it to the boss or another recipient.
