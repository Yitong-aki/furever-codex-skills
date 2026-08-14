# Data contract

## Reporting calendar

- Timezone: `Asia/Shanghai`.
- Default period: previous Monday 00:00:00 through Sunday 23:59:59.
- Store the inclusive start/end timestamps in every raw export and report.
- Also collect the immediately preceding period with the same number of days. Its end date must be exactly one day before the reporting period starts.

## Feedback Collection Base

- Wiki title: `Feedback Collection`
- Wiki token: `QB4hwPN8Ri5RCDkCuYVcivVBnPh`
- Base token: `PhntbXzNxaY6mSsIVIgc3tYMnDc`

Current table map:

| Channel | Table ID | Native unique ID | Time field | Required content |
|---|---|---|---|---|
| Gmail | `tblLWrYDT9Np0T8w` | `Thread ID` | `Time` / `fldQsX4PCY` | Thread ID, Feedback, Time, User ID, Link, App Version |
| Typeform | `tblAgndOBZEUqrG7` | `Submit ID` | `Time` / `fldMNjXoIO` | Questionnaire, Q&A, Submit ID, Time |
| App Store | `tbllD74urwkj0gkX` | `Review ID` | `Time` / `fldBenvv26` | Title, Content, Rating, Review ID, App Version, Time, Author, Region |
| Discord | `tblZ7lS9m0FJGL4j` | Base record ID | Verify current schema | Text, timestamp if available |

Field IDs used by the bundled collector are configuration, not analysis logic. If the Base schema changes, inspect the table fields and update the map before collecting.

### Deduplication

- Gmail: one record per `Thread ID`; fall back to Base `_record_id` only when Thread ID is missing.
- Typeform: one record per `Submit ID`.
- App Store: one record per `Review ID`.
- Discord: one record per Base `_record_id`, unless a message ID is available.
- Do not deduplicate unrelated users because their wording is similar.
- Report record count and unique-user count separately when both are used.

### Scope

- Include Gmail, Typeform, App Store, and Discord from Feedback Collection.
- Use the synchronized Gmail table; direct mailbox access is outside the default workflow.
- The Gmail row timestamp indicates thread synchronization activity, not necessarily a new user message. Split `Feedback` at either supported message-header form: `[8/3 12:36] Name <email>:` or `[8/3 12:36] email:`. Count and analyze only messages whose sender matches the row's `Gmail` address case-insensitively and whose header date falls inside the reporting period. Treat support-authored messages and user messages outside the period as context only. Exclude the synchronized marker `（仅包含系统模板或引用，无手写正文）`; if a thread also contains a real in-period user message, keep the real message. If no eligible user-authored message remains, keep the raw row for audit but set `_analysis_eligible=false` and exclude it from ordinary-feedback frequency and totals.
- If Discord has no reliable timestamp, disclose this and exclude unverified records from period totals.

### Analysis-ready fields

Every collected row must carry:

- `_analysis_record_id`: stable `Channel:native-id` identifier.
- `_analysis_eligible`: whether the row has period-verifiable, user-authored content for ordinary-feedback analysis.
- `_analysis_text`: only the text eligible for the reporting period; for Gmail this excludes support replies and historical messages.

Use `analysis_counts` and `ordinary_total` for report totals. Keep `counts` and `raw_counts` as collection-audit values. Before drafting, create the coverage manifest defined in `ordinary-taxonomy.md` and verify that every eligible `_analysis_record_id` is represented.

## Backend AI quality data

Canonical source: `https://admin.fureverworld.com/dashboard/feedback`, filtered to the reporting period. Do not switch to a different staging hostname unless the user explicitly changes the approved source.

Required event-level fields:

| Required field | Meaning |
|---|---|
| Feedback ID | Unique feedback event identifier |
| Created At | Event timestamp |
| User ID | Internal user identifier |
| Snap/Generation ID | Snap or generation identifier |
| Admin record link | Direct backend detail page |
| Media type | Image or video |
| Snap Type | Activity, Gift, Onboarding, or backend original value |
| Original Tags | Unmodified backend Tag list |
| User text | Original feedback text |
| User input image URL | Original pet/reference image |
| AI generated image URL | Generated still image |
| AI generated video URL | Generated video when present |
| Character sheet status | Verified yes/no/unknown plus evidence source |

### AI-quality counting

- Image denominator: unique image feedback events in the period.
- Video denominator: unique video feedback events in the period.
- Tag numerator: unique feedback events containing that original Tag.
- A multi-tag event contributes once to each selected Tag.
- Keep events with empty user text in Tag frequency totals; prefer records with original text as displayed examples.
- Keep image and video Tag tables separate.
- Preserve odd or mismatched Tags. Do not silently recategorize backend data.

### Detail table output fields

Use this exact order:

1. User ID
2. Snap/Generation ID
3. 图片或视频 link
4. Snap Type
5. 后台原始 Tag
6. 用户原文
7. 用户输入原图
8. AI 生成图片
9. AI 生成视频
10. 是否有 character sheet

## Privacy and traceability

- Internal IDs and Snap links may appear in the internal report.
- Remove email addresses and unnecessary direct personal identifiers from quoted text.
- Preserve source-native IDs in the working audit so every displayed example can be traced.
- Never place authentication tokens, cookies, passwords, or API secrets in the Skill or report.
