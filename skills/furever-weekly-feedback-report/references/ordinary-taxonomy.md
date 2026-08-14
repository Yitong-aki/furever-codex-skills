# Ordinary-feedback taxonomy and coverage manifest

Use these stable top-level categories across weeks. The category is a retrieval and counting aid, not the final issue title. Preserve every concrete issue as its own object in `issues` so that all problems are visible even when several belong to one broad category.

## Stable top-level categories

1. `AI 生成质量` — identity/appearance mismatch, anatomy, fur/color/markings, scene/style fit, image artifacts, video motion or behavior.
2. `核心流程与稳定性` — login/account, loading, crashes, lost data, notifications, media generation/download, and broken primary flows.
3. `付费、订阅与权益` — charges, cancellation, renewal, Treat/token balance, refunds, paywall, or paid entitlement mismatch.
4. `功能与交互需求` — Snap, Gift, Companion Mode, Living Space, navigation, customization, multi-pet, sharing, or another requested capability.
5. `内容与情感体验` — grief sensitivity, pet-memory tone, emotional comfort or distress, repetitive/inappropriate content, and relationship expectations.
6. `正向体验` — praise or confirmed satisfaction without an actionable problem. If praise and a problem coexist, assign both this category and the relevant problem category.
7. `其他` — a real issue that cannot yet be placed above. Always give it a concrete issue summary; never use `其他` to hide an unclear record.

## Full-coverage rules

- Review every row with `_analysis_eligible=true`.
- Split a record into every distinct issue it contains. Each issue has its own `summary` and one or more `categories`; one record may therefore contain several issue objects.
- Do not merge different issues just because they came from one person or thread.
- Keep low-frequency issues in the manifest even if they are not promoted to Sections 3–5.
- A record with no problem may still contain one positive-experience issue object using `正向体验`; `issues` can never be empty.
- Section 3 contains prioritized findings, Section 4 contains valuable non-P1/P2 signals, and Section 8 contains channel-specific context. The manifest is the audit that ensures none of the underlying feedback disappeared.

## Manifest schema

Create one JSON file per reporting week:

```json
{
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "records": [
    {
      "record_id": "Gmail:thread-id",
      "issues": [
        {
          "categories": ["付费、订阅与权益"],
          "summary": "已付费用户未收到承诺的 Treat"
        },
        {
          "categories": ["核心流程与稳定性", "付费、订阅与权益"],
          "summary": "多个登录方式造成账户与权益错位"
        }
      ],
      "report_placement": ["Executive Summary", "Section 5", "Section 8"]
    }
  ]
}
```

Run the report validator with `--analysis-json` and the current-week `--feedback-json`. It must find exact ID coverage: no eligible record missing, no unknown record added, and no issue without a valid category and concrete summary.
