# Access setup for a new operator

Use individual accounts. Do not share the manager's Feishu session, backend password, cookies, access tokens, or API secrets with an intern.

## Feishu access

Grant the intern or their automation identity:

1. Viewer access to the `Feedback Collection` Base and its Gmail, Typeform, App Store, and Discord tables.
2. Viewer access to the approved reference report and historical reports needed for comparison.
3. Editor or creator access to the designated weekly-report folder so they can create a new document, edit it, and embed images.
4. Permission to open media URLs used in the report.
5. User authorization for `lark-cli` on their own Feishu account.

The Feishu application used by Codex needs least-privilege capabilities for:

- Reading Base metadata, fields, and records.
- Reading Feishu documents.
- Creating and updating Feishu documents.
- Creating files in the designated Drive folder and uploading document media.

Do not hardcode OAuth scope names because they can change with the installed `lark-cli` version and tenant configuration. Run the command with user identity; if Feishu returns `permission_violations`, grant only one of the listed acceptable scopes and repeat the user authorization flow.

Comments access is optional. Grant it only when the intern must read or reply to document comments. The workflow never requires permission to delete comments.

## Furever backend access

The approved instance is `https://admin.fureverworld.com/dashboard/feedback`. Treat this as the canonical report source; the hostname does not need to contain the word `staging`.

Provide a read-only backend role that can:

1. Open `/dashboard/feedback`.
2. Filter feedback by date, media type, Snap Type, and original Tag.
3. Open `/dashboard/snaps/{id}` detail pages.
4. View or export Feedback ID, creation time, User ID, Snap/Generation ID, Snap Type, original Tags, and user text.
5. View the user's input image, AI-generated image, and AI-generated video.
6. Verify whether a character sheet exists and see the evidence used for that status.
7. Open the storage/media domains referenced by backend records.

Prefer a separate read-only account. Production mutation, refunds, user edits, and record deletion are not required for the report.

If browser login is the only available backend access, ensure Codex can use the logged-in browser session. If an API or CSV export is available, grant read/export permission and document the field mapping.

## Not required by default

- Direct Gmail mailbox access. The report uses the Gmail table already synchronized into Feedback Collection.
- Permission to send the report to the boss.
- Backend write, delete, refund, subscription, or user-management rights.
- Permission to delete Feishu comments.

## Access smoke test

Before the first weekly run, verify all of the following:

1. Fetch the approved Feishu reference document outline.
2. Read one day of Gmail, Typeform, and App Store records from Feedback Collection with pagination handled.
3. Open one image-feedback record and one video-feedback record at the approved backend URL.
4. Confirm the input image, output image, video link, original Tag, and character-sheet status are visible.
5. After explicit authorization, create a disposable Feishu test document in the target folder and embed one remote image.

Report every failed check with the missing resource or permission. Do not silently omit a source.
