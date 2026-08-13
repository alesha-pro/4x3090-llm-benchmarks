# Agent runbook: LocalMaxxing archive upload

This repository contains a guarded importer for publishing the benchmark archive to LocalMaxxing. Agents working here must follow this sequence for an upload. The public-write step must never be inferred from a request to inspect, plan, validate, or document the archive.

## Invariants

- `plan`, `resolve-models`, and `dry-run` do not publish benchmark rows.
- `./upload-localmaxxing --allow-aggregate-submit` is a public-write operation.
- Never print, commit, or pass a LocalMaxxing API key as a command-line argument. Use `LMX_API_KEY` or the saved `lmx` configuration.
- Never include rows with unknown throughput semantics.
- Never invent missing metrics or map a quantized checkpoint to a merely similar base model.
- Never retry an ambiguous timed-out submission until the source run ID has been checked on LocalMaxxing and confirmed absent.
- Keep `.localmaxxing-import/` uncommitted. It contains generated payloads and local append-only receipts.
- Upload pacing assumes the authenticated user has a LocalMaxxing Pro account: 13 seconds between submissions, below the 300-per-rolling-hour limit.

## Current reviewed selection

For the 638-row snapshot committed with this runbook, the expected plan is:

| Decision | Rows |
|---|---:|
| Ready | 552 |
| Ready: single-stream | 137 |
| Ready: aggregate throughput | 415 |
| Excluded: unknown metric semantics | 64 |
| Excluded: missing output tok/s | 22 |

If these counts change, stop before public submission. Inspect the changed archive or mappings and report the new counts; do not assume the prior upload authorization covers a different selection.

## Sequence 1: preflight

Run from the repository root.

1. Install or update to `localmaxxing-cli` v0.1.33 or newer, then confirm `lmx version --json` succeeds.
2. Confirm the current CLI exposes `lmx speed-test validate-local`, `dry-run`, and `submit`; the removed `lmx benchmark ...` command group is incompatible.
3. Confirm the operator has explicitly authorized public upload of both single-stream and aggregate-throughput rows.
4. Confirm the authenticated LocalMaxxing account is Pro.
5. Confirm authentication exists through `LMX_API_KEY` or the saved `lmx` config. Do not display the key.
6. Confirm `model-map.json`, `data/benchmarks.jsonl`, and `upload-localmaxxing` are present.

If `lmx` is not installed, use the release instructions linked from `README.md`. To save an environment-provided key without exposing it in process arguments:

```bash
printf '%s\n' "$LMX_API_KEY" | lmx auth --key-stdin
```

The importer CLI transport uses the current command contract:

```bash
lmx speed-test validate-local <payload.json>
lmx speed-test dry-run <payload.json>
lmx speed-test submit <payload.json>
```

Use `lmx update` when an older release is installed. Do not substitute the
obsolete `lmx benchmark ...` commands.

## Sequence 2: offline plan

Generate the exact selection without network writes:

```bash
python3 scripts/import_localmaxxing.py plan \
  --model-map model-map.json \
  --allow-partial-metrics
```

Proceed only when the result is 638 selected, 552 ready, 64 `unknown_metric_semantics`, 22 `missing_output_tps`, and no unresolved models. Inspect `.localmaxxing-import/unresolved-models.json` if unresolved models appear.

## Sequence 3: production validation without publishing

Validate every ready payload against LocalMaxxing:

```bash
python3 scripts/import_localmaxxing.py dry-run \
  --transport api \
  --model-map model-map.json \
  --allow-partial-metrics
```

Proceed only if all 552 ready rows have successful dry-run receipts. The uploader will reuse `.localmaxxing-import/dry-run-receipts.jsonl`, so this validation is not repeated unnecessarily.

## Sequence 4: guarded public upload

Only after explicit public-write authorization and successful validation, run:

```bash
./upload-localmaxxing --allow-aggregate-submit
```

The acknowledgement is mandatory because 415 selected rows are aggregate throughput, not single-user decode rates. The uploader checks the plan, verifies every ready row has a successful production dry-run, submits at 13-second intervals, honors `Retry-After`, and records results in `.localmaxxing-import/submit-receipts.jsonl`.

Keep the process running until it finishes or reports an actionable error. A complete 552-row upload takes about two hours before retries.

## Sequence 5: resume safely

After an ordinary interruption, rerun the same command:

```bash
./upload-localmaxxing --allow-aggregate-submit
```

Successful source run IDs are skipped from the append-only receipts. Do not delete or edit receipt files to force retries.

If the uploader reports an ambiguous submission timeout:

1. Read the ambiguous source run ID from `.localmaxxing-import/submit-receipts.jsonl`.
2. Check the authenticated user's LocalMaxxing runs for that source run ID.
3. If the row exists, do not retry it; reconcile the receipt before continuing.
4. If the row is confirmed absent, resume explicitly:

```bash
./upload-localmaxxing \
  --allow-aggregate-submit \
  --retry-ambiguous
```

## Completion report

Report the selected, validated, submitted, skipped/resumed, excluded, failed, and ambiguous counts. Include receipt paths and source run IDs for failures or ambiguous outcomes. Never include API keys or authorization headers.
