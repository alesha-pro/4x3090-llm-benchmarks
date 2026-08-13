# Changelog

## 2026-08-09

- Required explicit aggregate-throughput acknowledgement for the archive upload path before any production validation or submission begins.
- Added Pro-account pacing at 13 seconds per submission while preserving the 121-second free-account default for other submit commands.
- Resolved the remaining Qwen3-4B and Qwen3.5-122B artifact aliases to source-verified Hugging Face repositories.
- Added an agent-discoverable upload runbook with explicit preflight, validation, public-write authorization, resume, and ambiguous-timeout recovery sequences.
- Updated the CLI transport and agent instructions for localmaxxing-cli v0.1.33's `lmx speed-test` command group after removal of `lmx benchmark`.

## 2026-07-28

- Added the resumable LocalMaxxing importer with offline planning, model resolution, local and remote validation, and guarded public submission.
- Added append-only receipts, bounded CLI error capture, submission pacing, and a hard failure when executable actions select no ready rows.
- Added artifact-matched or owner-confirmed repository mappings for all 265 archive rows that lacked Hugging Face IDs, and prevented family mappings from masking unresolved artifact aliases.
- Added an explicit `--allow-partial-metrics` opt-in for throughput-only payloads while keeping unknown metric semantics excluded by default.
- Documented the production rate-limit contract and added a configurable per-request timeout for both CLI and direct API transports.
- Added `./upload-localmaxxing` to production-validate, pace, receipt, and resumably publish the reviewed archive with one command.

## 2026-07-27

- Published the first normalized snapshot.
- Added 638 measurements from 20 benchmark campaigns.
- Added SQLite, per-run pages, and indexes by model, campaign, and engine.
- Kept exllamav3 labeled as a small experimental slice.
