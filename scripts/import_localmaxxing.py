#!/usr/bin/env python3
"""Convert and optionally validate or submit archive rows to LocalMaxxing.

Planning is entirely offline. Network writes only happen for the ``submit``
action, which requires both an exact row-count confirmation and, when selected,
an explicit aggregate-throughput acknowledgement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "benchmarks.jsonl"
DEFAULT_MODEL_MAP = ROOT / "model-map.json"
DEFAULT_OUTPUT = ROOT / ".localmaxxing-import"
DEFAULT_API_BASE = "https://www.localmaxxing.com"
DEFAULT_HF_API_BASE = "https://huggingface.co"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60.0
DEFAULT_FREE_SUBMISSION_INTERVAL_SECONDS = 121.0
DEFAULT_PRO_SUBMISSION_INTERVAL_SECONDS = 13.0
SUPPORTED_ENGINES = {"vllm", "llama.cpp", "exllamav3"}
KNOWN_METRIC_KINDS = {"single_stream_wall", "aggregate_output"}
KV_CACHE_DTYPES = {"q8_0", "q4_0", "fp8", "fp16", "auto"}
SOURCE_URL = "https://github.com/alesha-pro/4x3090-llm-benchmarks"


class ImporterError(RuntimeError):
    """A user-actionable importer failure."""

class AmbiguousSubmissionError(ImporterError):
    """A submit request timed out after it may have committed remotely."""


def positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ImporterError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ImporterError(f"{path}:{line_number}: expected a JSON object")
        rows.append(value)
    return rows


def load_model_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ImporterError("--model-map must contain a JSON object")
    result: dict[str, str] = {}
    for alias, hf_id in value.items():
        if not isinstance(alias, str) or not isinstance(hf_id, str) or "/" not in hf_id:
            raise ImporterError(
                "--model-map entries must be string aliases mapped to org/repository IDs"
            )
        result[alias] = hf_id
    return result


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "4x3090-localmaxxing-importer/1"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise ImporterError(f"model search returned HTTP {exc.code}: {body[-2000:]}") from exc
    except urllib.error.URLError as exc:
        raise ImporterError(f"model search failed: {exc.reason}") from exc


def normalized_model_name(value: str) -> str:
    name = value.rsplit("/", 1)[-1].lower()
    if name.endswith(".gguf"):
        name = name[:-5]
    return "".join(character for character in name if character.isalnum())


def candidate_confidence(alias: str, hf_id: str, display_name: str | None) -> str:
    expected = normalized_model_name(alias)
    values = {
        normalized_model_name(hf_id),
        normalized_model_name(display_name or ""),
    }
    if expected in values:
        return "exact_name"
    if any(expected in value or value in expected for value in values if value):
        return "partial_name"
    return "search_result"


def search_model_candidates(
    alias: str,
    resolver_source: str,
    api_base: str,
    hf_api_base: str,
    fetch: Callable[[str], Any] = fetch_json,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    searches: list[tuple[str, str]] = []
    if resolver_source in {"localmaxxing", "both"}:
        query = urllib.parse.urlencode({"q": alias, "limit": 10})
        searches.append(("localmaxxing", f"{api_base.rstrip('/')}/api/models/search?{query}"))
    if resolver_source in {"huggingface", "both"}:
        query = urllib.parse.urlencode({"search": alias, "limit": 10, "full": "false"})
        searches.append(("huggingface", f"{hf_api_base.rstrip('/')}/api/models?{query}"))
    for source, url in searches:
        try:
            result = fetch(url)
        except ImporterError as exc:
            errors.append({"source": source, "error": str(exc)})
            continue
        if not isinstance(result, list):
            errors.append({"source": source, "error": "search response was not an array"})
            continue
        for item in result:
            if not isinstance(item, dict):
                continue
            hf_id = item.get("hfId") if source == "localmaxxing" else item.get("id")
            if not isinstance(hf_id, str) or "/" not in hf_id:
                continue
            display_name = item.get("displayName")
            candidates.append(
                {
                    "source": source,
                    "hfId": hf_id,
                    "displayName": display_name if isinstance(display_name, str) else None,
                    "confidence": candidate_confidence(
                        alias,
                        hf_id,
                        display_name if isinstance(display_name, str) else None,
                    ),
                    "benchmarkCount": item.get("benchmarkCount"),
                    "downloads": item.get("downloads"),
                    "likes": item.get("likes"),
                }
            )
    confidence_order = {"exact_name": 0, "partial_name": 1, "search_result": 2}
    candidates.sort(
        key=lambda item: (
            confidence_order[item["confidence"]],
            0 if item["source"] == "localmaxxing" else 1,
            -(item.get("benchmarkCount") or 0),
            -(item.get("downloads") or 0),
            item["hfId"].lower(),
        )
    )
    deduplicated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate["hfId"] in seen:
            continue
        seen.add(candidate["hfId"])
        deduplicated.append(candidate)
    return {"alias": alias, "candidates": deduplicated, "errors": errors}


def resolve_manifest_aliases(
    manifest: list[dict[str, Any]],
    resolver_source: str,
    api_base: str,
    hf_api_base: str,
    fetch: Callable[[str], Any] = fetch_json,
) -> list[dict[str, Any]]:
    aliases: dict[str, dict[str, Any]] = {}
    for entry in manifest:
        if entry.get("reason") != "unresolved_model":
            continue
        alias = str(
            entry.get("checkpointRef") or entry.get("modelVariant") or entry.get("model")
        )
        record = aliases.setdefault(alias, {"count": 0, "exampleRunIds": []})
        record["count"] += 1
        if len(record["exampleRunIds"]) < 5:
            record["exampleRunIds"].append(entry["runId"])
    report: list[dict[str, Any]] = []
    for alias, details in sorted(
        aliases.items(), key=lambda item: (-item[1]["count"], item[0].lower())
    ):
        result = search_model_candidates(
            alias, resolver_source, api_base, hf_api_base, fetch
        )
        result.update(details)
        report.append(result)
    return report


def resolve_hf_id(row: dict[str, Any], model_map: dict[str, str]) -> str | None:
    run_id = row.get("run_id")
    checkpoint = row.get("checkpoint_ref")
    model_variant = row.get("model_variant")
    model = row.get("model")
    if isinstance(run_id, str) and run_id in model_map:
        return model_map[run_id]
    if isinstance(checkpoint, str):
        if checkpoint in model_map:
            return model_map[checkpoint]
        if "/" in checkpoint:
            return checkpoint
        return None
    if isinstance(model_variant, str):
        return model_map.get(model_variant)
    if isinstance(model, str):
        return model_map.get(model)
    return None


def gpu_count(row: dict[str, Any]) -> int:
    count = 1
    for field in ("tp", "pp", "dp", "instances"):
        value = row.get(field)
        if value is None:
            continue
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ImporterError(f"{row.get('run_id')}: invalid {field}={value!r}")
        count *= value
    if count > 16:
        raise ImporterError(
            f"{row.get('run_id')}: derived GPU count {count} exceeds LocalMaxxing's limit"
        )
    return count


def command_snippet(row: dict[str, Any]) -> str | None:
    argv = row.get("launch_argv")
    if isinstance(argv, list) and argv:
        return shlex.join(str(item) for item in argv)
    command = row.get("launch_cmd")
    if isinstance(command, str) and command.strip():
        return command.strip()
    return None


def hardware_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "hwClass": "DISCRETE_GPU",
        "gpuName": "NVIDIA GeForce RTX 3090",
        "gpuCount": gpu_count(row),
        "vramGb": 24,
        "cpu": "AMD EPYC 7642",
        "ramGb": 125,
        "os": "Linux",
    }


def engine_flags(row: dict[str, Any]) -> dict[str, Any] | None:
    command = command_snippet(row)
    if command is None:
        return None
    flags: dict[str, Any] = {
        "commandSnippet": command,
        "tensorParallel": row.get("tp") or 1,
        "pipelineParallel": row.get("pp") or 1,
        "concurrency": row.get("concurrency") or 1,
    }
    kv_dtype = row.get("kv_cache_dtype")
    if kv_dtype in KV_CACHE_DTYPES:
        flags["kvCacheDtype"] = kv_dtype
    knobs = row.get("knobs")
    if isinstance(knobs, dict):
        if positive(knobs.get("gpu_memory_utilization")):
            flags["gpuMemUtil"] = knobs["gpu_memory_utilization"]
        if isinstance(knobs.get("enable_prefix_caching"), bool):
            flags["prefixCaching"] = knobs["enable_prefix_caching"]
        if isinstance(knobs.get("enable_chunked_prefill"), bool):
            flags["chunkedPrefill"] = knobs["enable_chunked_prefill"]
        if positive(knobs.get("max_num_seqs")):
            flags["maxRunningSeqs"] = knobs["max_num_seqs"]
        attention = knobs.get("_env_VLLM_ATTENTION_BACKEND")
        if isinstance(attention, str) and attention:
            flags["attentionBackend"] = attention.lower()
    speculative = row.get("spec_decode")
    if isinstance(speculative, dict):
        flags["specDecoding"] = True
        if speculative.get("method"):
            flags["specMethod"] = str(speculative["method"])
        if speculative.get("draft_ref"):
            flags["specModel"] = str(speculative["draft_ref"])
        if positive(speculative.get("k")):
            flags["specNumTokens"] = speculative["k"]
    return flags


def secondary_metrics(row: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    mappings = (
        ("ttft_p50_ms", "ttftMs", 1.0),
        ("prefill_tok_s", "tokSPrefill", 1.0),
        ("total_tok_s", "tokSTotal", 1.0),
        ("vram_peak_mib", "peakVramGb", 1.0 / 1024.0),
    )
    for source, destination, scale in mappings:
        value = row.get(source)
        if positive(value):
            metrics[destination] = float(value) * scale
    return metrics


def row_skip_reason(
    row: dict[str, Any],
    model_map: dict[str, str],
    include_unknown: bool,
    allow_partial_metrics: bool = False,
) -> str | None:
    if not positive(row.get("output_tok_s")):
        return "missing_output_tps"
    if not secondary_metrics(row) and not allow_partial_metrics:
        return "missing_secondary_metric"
    if row.get("engine") not in SUPPORTED_ENGINES:
        return "unsupported_engine"
    metric_kind = row.get("output_tps_kind")
    if metric_kind not in KNOWN_METRIC_KINDS and not include_unknown:
        return "unknown_metric_semantics"
    if resolve_hf_id(row, model_map) is None:
        return "unresolved_model"
    return None


def notes_for(row: dict[str, Any]) -> str:
    parts = [
        f"Imported from {SOURCE_URL}",
        f"source run {row.get('run_id')}",
        f"measured {row.get('date')}",
        f"campaign {row.get('source')}",
        f"objective {row.get('objective')}",
        f"metric semantics {row.get('output_tps_kind')}",
        f"normalization {row.get('normalization_status')}",
    ]
    if row.get("notes"):
        parts.append(str(row["notes"]))
    rendered = "; ".join(parts) + "."
    if len(rendered) > 2000:
        raise ImporterError(f"{row.get('run_id')}: generated notes exceed 2000 characters")
    return rendered


def convert_row(row: dict[str, Any], model_map: dict[str, str]) -> dict[str, Any]:
    hf_id = resolve_hf_id(row, model_map)
    if hf_id is None:
        raise ImporterError(f"{row.get('run_id')}: unresolved Hugging Face model ID")
    payload: dict[str, Any] = {
        "hfId": hf_id,
        "hardware": hardware_payload(row),
        "engineName": row["engine"],
        "quantization": row.get("quant_raw") or row.get("quant"),
        "promptTokens": row.get("prompt_tokens") or 0,
        "outputTokens": row.get("gen_tokens") or 0,
        "contextLength": row.get("context_len") or 2048,
        "batchSize": row.get("concurrency") or 1,
        "tokSOut": row["output_tok_s"],
        "notes": notes_for(row),
    }
    if row.get("engine_version"):
        payload["engineVersion"] = str(row["engine_version"])
    payload.update(secondary_metrics(row))
    flags = engine_flags(row)
    if flags is not None:
        payload["engineFlags"] = flags
    return payload


def selected_rows(rows: Iterable[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = list(rows)
    filters = (
        ("run_id", args.run_id),
        ("source", args.campaign),
        ("model", args.model),
    )
    for field, expected in filters:
        if expected:
            selected = [
                row
                for row in selected
                if str(row.get(field, "")).lower() == expected.lower()
            ]
    if args.max_runs is not None:
        selected = selected[: args.max_runs]
    return selected


def payload_filename(run_id: str) -> str:
    digest = hashlib.sha256(run_id.encode()).hexdigest()[:16]
    return f"{digest}.json"


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def create_plan(
    rows: list[dict[str, Any]],
    model_map: dict[str, str],
    output_dir: Path,
    include_unknown: bool,
    allow_partial_metrics: bool = False,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    payload_dir = output_dir / "payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    unresolved_counts: Counter[str] = Counter()
    unresolved_examples: dict[str, list[str]] = {}
    for row in rows:
        run_id = str(row.get("run_id") or "")
        reason = row_skip_reason(row, model_map, include_unknown, allow_partial_metrics)
        entry: dict[str, Any] = {
            "runId": run_id,
            "campaign": row.get("source"),
            "model": row.get("model"),
            "checkpointRef": row.get("checkpoint_ref"),
            "modelVariant": row.get("model_variant"),
            "metricKind": row.get("output_tps_kind"),
        }
        if reason is not None:
            entry.update({"status": "skipped", "reason": reason})
            reasons[reason] += 1
            if reason == "unresolved_model":
                alias = str(row.get("checkpoint_ref") or row.get("model_variant") or row.get("model"))
                unresolved_counts[alias] += 1
                examples = unresolved_examples.setdefault(alias, [])
                if len(examples) < 5:
                    examples.append(run_id)
        else:
            path = payload_dir / payload_filename(run_id)
            atomic_write_json(path, convert_row(row, model_map))
            entry.update(
                {
                    "status": "ready",
                    "payloadPath": str(path.resolve()),
                    "hfId": resolve_hf_id(row, model_map),
                }
            )
            reasons["ready"] += 1
        manifest.append(entry)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.jsonl"
    temporary = manifest_path.with_suffix(".jsonl.tmp")
    temporary.write_text(
        "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in manifest)
    )
    temporary.replace(manifest_path)
    unresolved_path = output_dir / "unresolved-models.json"
    unresolved_report = [
        {
            "alias": alias,
            "count": count,
            "exampleRunIds": unresolved_examples[alias],
        }
        for alias, count in sorted(
            unresolved_counts.items(), key=lambda item: (-item[1], item[0].lower())
        )
    ]
    atomic_write_json(unresolved_path, unresolved_report)
    atomic_write_json(
        output_dir / "model-map.template.json",
        {item["alias"]: "" for item in unresolved_report},
    )
    summary = {
        "sourceRows": len(rows),
        "counts": dict(sorted(reasons.items())),
        "manifest": str(manifest_path.resolve()),
        "payloadDirectory": str(payload_dir.resolve()),
        "unresolvedModels": str(unresolved_path.resolve()),
        "modelMapTemplate": str((output_dir / "model-map.template.json").resolve()),
    }
    atomic_write_json(output_dir / "summary.json", summary)
    return manifest, reasons


def receipt_run_ids(receipts_path: Path, action: str, status: str) -> set[str]:
    if not receipts_path.exists():
        return set()
    return {
        str(item.get("runId"))
        for item in load_jsonl(receipts_path)
        if item.get("action") == action and item.get("status") == status
    }


def completed_run_ids(receipts_path: Path, action: str) -> set[str]:
    return receipt_run_ids(receipts_path, action, "success")


def last_attempt_epoch(receipts_path: Path, action: str) -> float | None:
    if not receipts_path.exists():
        return None
    latest: float | None = None
    for item in load_jsonl(receipts_path):
        if item.get("action") != action:
            continue
        timestamp = item.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        try:
            epoch = datetime.fromisoformat(timestamp).timestamp()
        except ValueError:
            continue
        latest = epoch if latest is None else max(latest, epoch)
    return latest


def append_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def parse_response(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text[-4000:]}


def run_cli(
    lmx: str,
    action: str,
    payload_path: Path,
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> Any:
    command = [
        lmx,
        "speed-test",
        action,
        str(payload_path),
        "--json",
        "--quiet",
    ]
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=request_timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise ImporterError(
            f"CLI {action} timed out after {request_timeout_seconds:g} seconds"
        ) from exc
    if process.returncode != 0:
        detail = (process.stderr.strip() or process.stdout.strip())[-4000:]
        raise ImporterError(f"CLI {action} failed: {detail}")
    return parse_response(process.stdout)


def api_request(
    base_url: str,
    action: str,
    payload: dict[str, Any],
    api_key: str,
    sleep: Callable[[float], None] = time.sleep,
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> Any:
    endpoint = "/api/speed-tests/dry-run" if action == "dry-run" else "/api/speed-tests"
    request = urllib.request.Request(
        base_url.rstrip("/") + endpoint,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "4x3090-localmaxxing-importer/1",
        },
        method="POST",
    )
    while True:
        try:
            with urllib.request.urlopen(request, timeout=request_timeout_seconds) as response:
                return parse_response(response.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = max(float(retry_after or 0), 1.0)
                except ValueError:
                    delay = 60.0
                sleep(delay)
                continue
            raise ImporterError(f"API returned HTTP {exc.code}: {body[-4000:]}") from exc
        except TimeoutError as exc:
            message = f"API request timed out after {request_timeout_seconds:g} seconds"
            error_type = AmbiguousSubmissionError if action == "submit" else ImporterError
            raise error_type(message) from exc
        except urllib.error.URLError as exc:
            message = f"API request failed: {exc.reason}"
            if action == "submit" and isinstance(exc.reason, TimeoutError):
                raise AmbiguousSubmissionError(message) from exc
            raise ImporterError(message) from exc


def configured_api_key() -> str:
    key = os.environ.get("LMX_API_KEY", "")
    if key:
        return key
    config_path = Path.home() / ".config" / "localmaxxing" / "config.json"
    if not config_path.exists():
        return ""
    config = json.loads(config_path.read_text())
    for field in ("apiKey", "api_key", "key"):
        value = config.get(field)
        if isinstance(value, str) and value:
            return value
    return ""


def execute_plan(
    manifest: list[dict[str, Any]],
    action: str,
    transport: str,
    receipts_path: Path,
    lmx: str,
    api_base: str,
    interval_seconds: float,
    continue_on_error: bool,
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
) -> Counter[str]:
    completed = completed_run_ids(receipts_path, action)
    counts: Counter[str] = Counter()
    api_key = configured_api_key()
    if transport == "api" and not api_key:
        raise ImporterError("LMX_API_KEY is required for --transport api")
    ready = [entry for entry in manifest if entry["status"] == "ready"]
    last_attempt = last_attempt_epoch(receipts_path, action) if action == "submit" else None
    total = len(ready)
    for index, entry in enumerate(ready, start=1):
        run_id = entry["runId"]
        if run_id in completed:
            counts["resumed_skip"] += 1
            continue
        if action == "submit" and last_attempt is not None:
            remaining = interval_seconds - (time.time() - last_attempt)
            if remaining > 0:
                time.sleep(remaining)
        payload_path = Path(entry["payloadPath"])
        try:
            if transport == "cli":
                response = run_cli(lmx, action, payload_path, request_timeout_seconds)
            else:
                payload = json.loads(payload_path.read_text())
                response = api_request(
                    api_base,
                    action,
                    payload,
                    api_key,
                    request_timeout_seconds=request_timeout_seconds,
                )
            status = "success"
            counts["success"] += 1
        except AmbiguousSubmissionError as exc:
            response = {"error": str(exc)}
            status = "ambiguous"
            counts["ambiguous"] += 1
        except (ImporterError, OSError, json.JSONDecodeError) as exc:
            response = {"error": str(exc)}
            status = "error"
            counts["error"] += 1
        finally:
            if action == "submit":
                last_attempt = time.time()
        append_receipt(
            receipts_path,
            {
                "action": action,
                "runId": run_id,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response": response,
            },
        )
        print(f"[{index}/{total}] {status}: {run_id}", file=sys.stderr)
        if status in {"error", "ambiguous"} and not continue_on_error:
            raise ImporterError(f"stopped after {run_id}; inspect {receipts_path}")
    return counts


def submission_interval(action: str, requested: float | None) -> float:
    if requested is not None:
        return requested
    if action == "upload":
        return DEFAULT_PRO_SUBMISSION_INTERVAL_SECONDS
    return DEFAULT_FREE_SUBMISSION_INTERVAL_SECONDS


def require_aggregate_acknowledgement(
    entries: list[dict[str, Any]],
    allowed: bool,
) -> None:
    aggregate = sum(
        entry.get("metricKind") == "aggregate_output" for entry in entries
    )
    if aggregate and not allowed:
        raise ImporterError(
            f"{aggregate} pending rows are aggregate throughput; review them and pass "
            "--allow-aggregate-submit to acknowledge leaderboard mixing"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely plan, validate, or submit the benchmark archive to LocalMaxxing."
    )
    parser.add_argument(
        "action",
        choices=("plan", "resolve-models", "validate-local", "dry-run", "submit", "upload"),
        help=(
            "plan is offline; resolve-models performs read-only catalog searches; "
            "dry-run validates remotely without writing; submit writes selected rows; "
            "upload plans, production-validates, and resumably publishes the reviewed archive"
        ),
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--model-map",
        type=Path,
        help="JSON object mapping run IDs/checkpoint aliases/model variants to exact HF IDs",
    )
    parser.add_argument("--run-id")
    parser.add_argument("--campaign")
    parser.add_argument("--model")
    parser.add_argument("--max-runs", type=int)
    parser.add_argument(
        "--include-unknown-metrics",
        action="store_true",
        help="include rows whose output TPS semantics are unknown (not recommended)",
    )
    parser.add_argument(
        "--allow-partial-metrics",
        action="store_true",
        help="include rows with output TPS but no TTFT, prefill, total TPS, or VRAM metric",
    )
    parser.add_argument("--transport", choices=("cli", "api"), default="cli")
    parser.add_argument("--lmx", default="lmx", help="LocalMaxxing CLI executable")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--hf-api-base", default=DEFAULT_HF_API_BASE)
    parser.add_argument(
        "--resolver-source",
        choices=("localmaxxing", "huggingface", "both"),
        default="both",
        help="catalogs queried by resolve-models",
    )
    parser.add_argument(
        "--receipts",
        type=Path,
        help="append-only receipt path; defaults to <output-dir>/<action>-receipts.jsonl",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=None,
        help=(
            "delay between public submissions; defaults to 13 seconds for the Pro "
            "archive upload and 121 seconds for other submission commands"
        ),
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=DEFAULT_REQUEST_TIMEOUT_SECONDS,
        help="per-request client timeout; LocalMaxxing publishes no fixed request deadline",
    )
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--retry-ambiguous",
        action="store_true",
        help="retry timed-out submissions only after confirming they were not created remotely",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="allow submit when otherwise eligible rows have unresolved model aliases",
    )
    parser.add_argument(
        "--allow-aggregate-submit",
        action="store_true",
        help="acknowledge that aggregate throughput will enter a tok/s leaderboard",
    )
    parser.add_argument(
        "--confirm-count",
        type=int,
        help="submit only: must exactly equal the number of ready, unsubmitted rows",
    )
    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    if args.max_runs is not None and args.max_runs < 1:
        raise ImporterError("--max-runs must be positive")
    if args.interval_seconds < 0:
        raise ImporterError("--interval-seconds cannot be negative")
    if args.request_timeout_seconds <= 0:
        raise ImporterError("--request-timeout-seconds must be positive")
    if args.action == "validate-local" and args.transport != "cli":
        raise ImporterError("validate-local requires --transport cli")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.action == "upload":
            args.transport = "api"
            args.allow_partial_metrics = True
            if args.model_map is None:
                args.model_map = DEFAULT_MODEL_MAP
        args.interval_seconds = submission_interval(args.action, args.interval_seconds)
        validate_arguments(args)
        rows = selected_rows(load_jsonl(args.source), args)
        model_map = load_model_map(args.model_map)
        manifest, reasons = create_plan(
            rows,
            model_map,
            args.output_dir,
            args.include_unknown_metrics,
            args.allow_partial_metrics,
        )
        ready = [entry for entry in manifest if entry["status"] == "ready"]
        summary: dict[str, Any] = {
            "action": args.action,
            "selected": len(rows),
            "ready": len(ready),
            "counts": dict(sorted(reasons.items())),
            "outputDir": str(args.output_dir.resolve()),
        }
        if args.action == "resolve-models":
            report = resolve_manifest_aliases(
                manifest,
                args.resolver_source,
                args.api_base,
                args.hf_api_base,
            )
            candidates_path = args.output_dir / "model-candidates.json"
            atomic_write_json(candidates_path, report)
            summary["candidateReport"] = str(candidates_path.resolve())
            summary["unresolvedAliases"] = len(report)
            summary["aliasesWithExactNameCandidate"] = sum(
                any(
                    candidate["confidence"] == "exact_name"
                    for candidate in item["candidates"]
                )
                for item in report
            )
            print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
            return
        if args.action == "plan":
            print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
            return
        if args.action == "upload":
            if not ready:
                raise ImporterError(
                    f"no rows are ready for upload; inspect {args.output_dir / 'summary.json'}"
                )
            require_aggregate_acknowledgement(
                ready,
                args.allow_aggregate_submit,
            )
            submit_receipts = args.output_dir / "submit-receipts.jsonl"
            submitted = completed_run_ids(submit_receipts, "submit")
            ambiguous = receipt_run_ids(submit_receipts, "submit", "ambiguous") - submitted
            if ambiguous and not args.retry_ambiguous:
                raise ImporterError(
                    f"{len(ambiguous)} prior submissions have ambiguous timeout outcomes; "
                    "check LocalMaxxing for duplicates, then pass --retry-ambiguous only for absent runs"
                )
            dry_run_receipts = args.output_dir / "dry-run-receipts.jsonl"
            dry_run_execution = execute_plan(
                manifest=manifest,
                action="dry-run",
                transport="api",
                receipts_path=dry_run_receipts,
                lmx=args.lmx,
                api_base=args.api_base,
                interval_seconds=0,
                continue_on_error=False,
                request_timeout_seconds=args.request_timeout_seconds,
            )
            validated = completed_run_ids(dry_run_receipts, "dry-run")
            ready_ids = {entry["runId"] for entry in ready}
            if not ready_ids <= validated:
                raise ImporterError(
                    f"production dry-run did not validate all {len(ready)} ready rows; "
                    f"inspect {dry_run_receipts}"
                )
            submit_execution = execute_plan(
                manifest=manifest,
                action="submit",
                transport="api",
                receipts_path=submit_receipts,
                lmx=args.lmx,
                api_base=args.api_base,
                interval_seconds=args.interval_seconds,
                continue_on_error=False,
                request_timeout_seconds=args.request_timeout_seconds,
            )
            summary["dryRunExecution"] = dict(sorted(dry_run_execution.items()))
            summary["submitExecution"] = dict(sorted(submit_execution.items()))
            summary["dryRunReceipts"] = str(dry_run_receipts.resolve())
            summary["submitReceipts"] = str(submit_receipts.resolve())
            print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
            return
        if not ready:
            raise ImporterError(
                f"no rows are ready for {args.action}; inspect {args.output_dir / 'summary.json'}"
            )
        receipts = args.receipts or args.output_dir / f"{args.action}-receipts.jsonl"
        already_completed = completed_run_ids(receipts, args.action)
        pending = [entry for entry in ready if entry["runId"] not in already_completed]
        ambiguous = (
            receipt_run_ids(receipts, args.action, "ambiguous") - already_completed
        )
        if args.action == "submit" and ambiguous and not args.retry_ambiguous:
            raise ImporterError(
                f"{len(ambiguous)} prior submissions have ambiguous timeout outcomes; "
                "check LocalMaxxing for duplicates, then pass --retry-ambiguous only for absent runs"
            )
        if args.action == "submit":
            if not pending:
                raise ImporterError("no pending rows are ready for public submission")
            unresolved = reasons.get("unresolved_model", 0)
            if unresolved and not args.allow_partial:
                raise ImporterError(
                    f"{unresolved} rows have unresolved model IDs; provide --model-map or "
                    "explicitly use --allow-partial"
                )
            require_aggregate_acknowledgement(
                pending,
                args.allow_aggregate_submit,
            )
            if args.confirm_count != len(pending):
                raise ImporterError(
                    f"refusing public submission: --confirm-count must equal {len(pending)}"
                )
        execution = execute_plan(
            manifest=manifest,
            action=args.action,
            transport=args.transport,
            receipts_path=receipts,
            lmx=args.lmx,
            api_base=args.api_base,
            interval_seconds=args.interval_seconds,
            continue_on_error=args.continue_on_error,
            request_timeout_seconds=args.request_timeout_seconds,
        )
        summary["execution"] = dict(sorted(execution.items()))
        summary["receipts"] = str(receipts.resolve())
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    except (ImporterError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
