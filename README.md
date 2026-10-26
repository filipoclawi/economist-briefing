# Economist Briefing

Weekly, lightly filtered previews of newsletters from the exact Gmail label `Economist`.

Public URL: <https://filipoclawi.github.io/economist-briefing/>

- Saturday–Friday editions with navigation across the archive
- One concise, original preview per substantive newsletter title
- Clean direct `economist.com` links; contextual destinations clearly labelled `Related analysis`
- Read/watch time before every click, or an explicit “not supplied” label
- Red-dot Insider and Inside-series videos are visually distinct and explicitly flagged
- No email addresses, Gmail identifiers, tracking redirects, recipient data or private attribution

## Coverage and safe rollover

`editions.json` is the archive inventory. Recent editions also have a public,
privacy-safe `coverage.json`: a source-count reconciliation, actual source cutoff,
publication status and reusable editorial card records. It contains no mailbox
identifiers or account details. Account/service mail is counted separately and
never turned into an editorial card.

An incomplete edition is explicitly **week to date**, through the latest received
source timestamp—not through a future Friday or the time publication was checked.
The stable root mirrors the newest dated archive.

On later runs, including Friday finalisation:

1. Verify live authentication to required source/publishing services before new
   editorial work. Stop on an authentication failure; do not use cached fallback.
2. Read the existing archive, `editions.json` and any `coverage.json` first. Freeze
   the exact eligible source set privately. Include historical recoveries.
3. **Union existing published cards with newly covered sources**. Dedupe using
   the normalised newsletter title plus clean canonical destination; a shared
   related-analysis URL alone does not make two daily newsletters duplicates.
   Never rebuild an edition from only the messages still in Inbox. Previously
   covered current-week sources must survive finalisation even if archived.
4. Preserve previous previews, durations and archives unless correcting a
   specifically evidenced error. Do not use a promoted older episode's runtime
   as the duration of a different new episode.
5. Recompute source/card counts without double-counting already reviewed mail,
   update the actual cutoff and status, retain all edition tabs, and run tests.
6. Publish and verify the exact deployed commit and live bytes before any
   separately authorised mailbox handling. Source dispositions and mailbox
   action ledgers remain private, outside this repository.

Full newsletter text is the editorial basis. Publisher paywalls/HTTP 403 do not
block publication when email content is substantive; article access limits are
disclosed. No full-article access is implied.

## Verification

Run `python3 tests/catchup_contract.py` and `python3 tests/ui_smoke.py` with
Playwright installed. The UI test checks every edition on desktop/mobile, all
filters, video presentation, privacy, destinations/times and console errors.
Set `BASE_URL` to the public URL to run the same assertions against deployment.
