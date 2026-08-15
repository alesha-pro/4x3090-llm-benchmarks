#!/usr/bin/env python3
"""Canonical schema v2 for the local speed benchmark database.

The source artifacts are intentionally heterogeneous.  This module is the one
place where their metadata is normalized.  Numeric measurements are copied as
is; normalization only changes labels, structure, paths/references, and IDs.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2

FIELDS = [
    "schema_version",
    "record_kind",
    "run_id",
    "date",
    "source",
    "source_path",
    "source_refs",
    "model",
    "model_variant",
    "checkpoint_ref",
    "quant",
    "quant_method",
    "weight_bits",
    "activation_bits",
    "weight_format",
    "group_size",
    "symmetric",
    "quant_recipe",
    "quant_raw",
    "weight_path",
    "engine",
    "engine_raw",
    "engine_version",
    "objective",
    "output_tps_kind",
    "tp",
    "pp",
    "dp",
    "instances",
    "context_len",
    "power_limit_w",
    "spec_decode",
    "kv_cache_dtype",
    "concurrency",
    "prompt_tokens",
    "gen_tokens",
    "output_tok_s",
    "req_s",
    "total_tok_s",
    "ttft_p50_ms",
    "ttft_p99_ms",
    "itl_p50_ms",
    "tpot_p50_ms",
    "e2e_p99_ms",
    "prefill_tok_s",
    "decode_tok_s",
    "vram_peak_mib",
    "avg_power_w",
    "max_temp_c",
    "quality",
    "curve",
    "samples",
    "knobs",
    "launch_argv",
    "launch_cmd",
    "normalization_status",
    "notes",
]

INTEGER_FIELDS = {
    "schema_version",
    "weight_bits",
    "activation_bits",
    "group_size",
    "symmetric",
    "tp",
    "pp",
    "dp",
    "instances",
    "context_len",
    "power_limit_w",
    "concurrency",
    "prompt_tokens",
    "gen_tokens",
    "vram_peak_mib",
}

REAL_FIELDS = {
    "output_tok_s",
    "req_s",
    "total_tok_s",
    "ttft_p50_ms",
    "ttft_p99_ms",
    "itl_p50_ms",
    "tpot_p50_ms",
    "e2e_p99_ms",
    "prefill_tok_s",
    "decode_tok_s",
    "avg_power_w",
    "max_temp_c",
}

JSON_FIELDS = {
    "source_refs",
    "spec_decode",
    "quality",
    "curve",
    "samples",
    "knobs",
    "launch_argv",
}

METRIC_FIELDS = {
    "output_tok_s",
    "req_s",
    "total_tok_s",
    "ttft_p50_ms",
    "ttft_p99_ms",
    "itl_p50_ms",
    "tpot_p50_ms",
    "e2e_p99_ms",
    "prefill_tok_s",
    "decode_tok_s",
    "vram_peak_mib",
    "avg_power_w",
    "max_temp_c",
}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _model_name(value: Any) -> Any:
    mapping = {
        "gemma-4-12b-it": "Gemma-4-12B-it",
        "gemma-4-e2b-it": "Gemma-4-E2B-it",
        "gemma-4-31b": "Gemma-4-31B",
    }
    raw = _clean(value)
    return mapping.get(raw.lower(), value)


def _checkpoint_ref(row: dict[str, Any]) -> str | None:
    current = _clean(row.get("checkpoint_ref"))
    if current:
        return current
    variant = _clean(row.get("model_variant"))
    if variant:
        return variant
    path = _clean(row.get("weight_path"))
    if path:
        return Path(path.rstrip("/*")).name or None
    return None


def _source_refs(value: Any) -> list[dict[str, str]]:
    if isinstance(value, list):
        return value
    raw = _clean(value)
    if not raw:
        return []

    refs: list[dict[str, str]] = []
    matches = list(re.finditer(r"(?:^|[ +(;,])(?P<scope>repo|rig):", raw))
    if matches:
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
            path = raw[match.end():end].strip(" +();,")
            if path:
                refs.append({"scope": match.group("scope"), "path": path})
        return refs
    if raw.startswith(("llm-bench/", "daily-papers/", "research/", "posts/")):
        return [{"scope": "repo", "path": raw}]
    return [{"scope": "derived", "path": raw}]


def _engine(value: Any) -> tuple[str | None, str | None, str]:
    raw = _clean(value)
    if not raw:
        return None, None, "unresolved"
    key = raw.lower().replace("_", "")
    if key in {"llamacpp", "llama.cpp"}:
        return "llama.cpp", raw, "exact"
    if key == "vllm":
        return "vllm", raw, "exact"
    if key == "exllamav3":
        return "exllamav3", raw, "exact"
    if key == "sglang":
        return "sglang", raw, "exact"
    return raw.lower(), raw, "unresolved"


def _quant(row: dict[str, Any]) -> tuple[dict[str, Any], str]:
    raw_value = row.get("quant_raw") if row.get("quant_raw") is not None else row.get("quant")
    raw = _clean(raw_value)
    key = raw.lower()
    context = " ".join(
        _clean(row.get(name)).lower()
        for name in ("model", "model_variant", "checkpoint_ref", "weight_path", "run_id")
    )
    result = {
        "quant": "unknown",
        "quant_method": None,
        "weight_bits": None,
        "activation_bits": None,
        "weight_format": None,
        "group_size": None,
        "symmetric": None,
        "quant_recipe": None,
        "quant_raw": raw_value,
    }
    status = "exact"

    def setq(
        quant: str,
        method: str | None,
        bits: int | None,
        fmt: str | None = "safetensors",
        *,
        activation_bits: int | None = None,
        group_size: int | None = None,
        symmetric: bool | None = None,
        recipe: str | None = None,
    ) -> None:
        result.update(
            quant=quant,
            quant_method=method,
            weight_bits=bits,
            activation_bits=activation_bits,
            weight_format=fmt,
            group_size=group_size,
            symmetric=symmetric,
            quant_recipe=recipe,
        )

    if "autoround" in key or (key in {"int4", ""} and "autoround" in context):
        setq("autoround-int4", "autoround", 4, recipe="AutoRound")
        status = "inferred" if key in {"int4", ""} else "exact"
    elif key in {"awq-4bit", "awq-int4", "cyankiwi-awq", "quanttrio-awq", "unknown"} or "-awq" in key:
        if key == "unknown" and "awq" not in context:
            status = "unresolved"
        else:
            setq("awq-int4", "awq", 4, recipe="AWQ")
            status = "inferred" if key in {"cyankiwi-awq", "quanttrio-awq", "unknown"} else "exact"
    elif key in {"int4-g32-symmetric"} or (key == "int4" and "laguna" in context):
        setq(
            "compressed-tensors-int4-g32-symmetric",
            "compressed-tensors",
            4,
            activation_bits=16,
            group_size=32,
            symmetric=True,
        )
        status = "inferred" if key == "int4" else "exact"
    elif key == "w4a16-g32-asym-rtn":
        setq(
            "compressed-tensors-w4a16-g32-asym-rtn",
            "compressed-tensors",
            4,
            activation_bits=16,
            group_size=32,
            symmetric=False,
            recipe="RTN",
        )
    elif key == "compressed-tensors-w4a16":
        setq("compressed-tensors-w4a16", "compressed-tensors", 4, activation_bits=16)
    elif key in {"bf16", "bf16-base"}:
        setq("bf16", "none", 16, recipe=None)
    elif key in {"fp8", "fp8-static"}:
        dynamic = "dynamic" in context and key == "fp8"
        setq("fp8-dynamic" if dynamic else "fp8-static", "fp8", 8)
        status = "inferred" if key == "fp8" else "exact"
    elif key == "int8-w8a8":
        setq("int8-w8a8", "w8a8", 8, activation_bits=8)
    elif "nvfp4" in key:
        setq("nvfp4", "nvfp4", 4, recipe="NVFP4")
    elif key.startswith("gguf-"):
        canonical = key.replace("gguf-", "gguf-", 1)
        bits_match = re.search(r"(?:ud-iq|ud-q|iq|q)(\d+)", key)
        setq(canonical, "gguf", int(bits_match.group(1)) if bits_match else None, "gguf")
    elif key == "ud-q4_k_xl".lower():
        setq("gguf-ud-q4_k_xl", "gguf", 4, "gguf")
    elif key.startswith("exl3-"):
        match = re.search(r"exl3-(\d+(?:\.\d+)?)bpw", key)
        setq(key, "exl3", int(float(match.group(1))) if match else None, "exl3")
    elif key == "qat-mobile-mixed-int2-4-8":
        setq("qat-mixed-int2-4-8", "qat", None, recipe="QAT")
    elif key == "dflash-quant":
        setq("dflash-quant", "dflash", None)
    elif key == "llama.cpp gguf (alesha-pro fork)":
        setq("gguf-custom", "gguf", None, "gguf")
    elif not raw:
        status = "unresolved"
    else:
        result["quant"] = key or "unknown"
        status = "unresolved"
    return result, status


def _spec_decode(value: Any) -> Any:
    if value in (None, "", "none"):
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("{"):
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError:
                pass
        else:
            match = re.fullmatch(r"(?i)mtp(?:-(\d+))?", stripped)
            if match:
                return {"method": "mtp", "draft_ref": None, "draft_path": None,
                        "k": int(match.group(1)) if match.group(1) else None}
            return {"method": stripped.lower(), "draft_ref": None, "draft_path": None, "k": None}
    if not isinstance(value, dict):
        return value

    method = _clean(value.get("method") or value.get("kind")).lower()
    method_map = {
        "draft_model(tli)": "draft_model_tli",
        "draft_model": "draft_model_tli" if "tli" in _clean(value.get("draft")).lower() else "draft_model",
    }
    method = method_map.get(method, method)
    # Accept already-normalized input too, otherwise re-importing any source
    # rewrites every other row and drops its draft reference.
    draft = (
        value.get("draft")
        or value.get("model")
        or value.get("draft_path")
        or value.get("draft_ref")
    )
    draft_path = draft if isinstance(draft, str) and draft.startswith("/") else None
    draft_ref = Path(draft).name if draft_path else draft
    normalized = {
        "method": method or None,
        "draft_ref": draft_ref,
        "draft_path": draft_path,
        "k": value.get("k", value.get("K", value.get("num_speculative_tokens"))),
    }
    for name in ("acceptance", "accepted_tokens_per_round"):
        if value.get(name) is not None:
            normalized[name] = value[name]
    return normalized


def _output_tps_kind(row: dict[str, Any]) -> str | None:
    current = _clean(row.get("output_tps_kind"))
    if current:
        return current
    if row.get("output_tok_s") is None:
        return None
    objective = _clean(row.get("objective")).lower()
    source = _clean(row.get("source")).lower()
    if objective in {"aggregate", "concurrency_sweep", "real_prompt_chat", "synthetic_prompt_continuation"}:
        return "aggregate_output"
    if source.startswith("laguna-"):
        return "aggregate_output"
    if objective in {"single_stream", "single_stream+aggregate"}:
        return "single_stream_wall"
    return "unknown"


def _record_kind(row: dict[str, Any]) -> str:
    current = _clean(row.get("record_kind"))
    if current:
        return current
    has_metric = any(row.get(name) is not None for name in METRIC_FIELDS)
    has_structured_measurement = bool(row.get("curve") or row.get("samples"))
    return "measurement" if has_metric or has_structured_measurement else "placeholder"


def _flag_value(argv: Any, flag: str) -> int | None:
    if not isinstance(argv, list) or flag not in argv:
        return None
    try:
        return int(argv[argv.index(flag) + 1])
    except (IndexError, TypeError, ValueError):
        return None


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    original = dict(row)
    normalized = {field: original.get(field) for field in FIELDS}
    normalized["schema_version"] = SCHEMA_VERSION
    normalized["record_kind"] = _record_kind(original)
    normalized["model"] = _model_name(original.get("model"))
    normalized["checkpoint_ref"] = _checkpoint_ref(original)
    normalized["source_refs"] = _source_refs(original.get("source_refs") or original.get("source_path"))

    engine, engine_raw, engine_status = _engine(original.get("engine_raw") or original.get("engine"))
    normalized["engine"] = engine
    normalized["engine_raw"] = engine_raw

    quant, quant_status = _quant({**original, "checkpoint_ref": normalized["checkpoint_ref"]})
    normalized.update(quant)
    normalized["spec_decode"] = _spec_decode(original.get("spec_decode"))
    normalized["output_tps_kind"] = _output_tps_kind(original)

    curve = original.get("curve")
    samples = original.get("samples")
    if isinstance(curve, dict):
        samples = curve if samples is None else samples
        curve = None
    normalized["curve"] = curve
    normalized["samples"] = samples

    normalized["dp"] = original.get("dp")
    knobs = original.get("knobs") if isinstance(original.get("knobs"), dict) else {}
    inferred_dp = knobs.get("data_parallel_size") or _flag_value(
        original.get("launch_argv"), "--data-parallel-size"
    )
    if normalized["dp"] is None and inferred_dp:
        normalized["dp"] = int(inferred_dp)
    if original.get("source") == "vllm026-qwen36-reduce-scatter":
        # v1 used instances=2 as a proxy for vLLM DP=2.  It is one server with
        # two DP ranks, not two independent service instances.
        normalized["dp"] = 2
        normalized["instances"] = 1
    # The v1 schema lost DP for two measured orchestrator rows.  These values
    # are recovered from the source results.jsonl on the rig.
    if original.get("source") == "orchestrator":
        if original.get("output_tok_s") == 3308.4 and original.get("tp") == 1:
            normalized["dp"] = 4
        elif original.get("output_tok_s") == 2432.9 and original.get("tp") == 2:
            normalized["dp"] = 2

    statuses = {engine_status, quant_status}
    if "unresolved" in statuses:
        normalized["normalization_status"] = "unresolved"
    elif (
        "inferred" in statuses
        or normalized["dp"] != original.get("dp")
        or normalized["instances"] != original.get("instances")
    ):
        normalized["normalization_status"] = "inferred"
    else:
        normalized["normalization_status"] = "exact"
    return normalized


def _deduplicate_ids(rows: list[dict[str, Any]]) -> None:
    counts = Counter(row.get("run_id") for row in rows)
    for row in rows:
        run_id = row.get("run_id")
        if run_id and counts[run_id] > 1:
            topology = (
                f"topo-tp{row.get('tp') or 1}-pp{row.get('pp') or 1}-"
                f"dp{row.get('dp') or 1}-i{row.get('instances') or 1}"
            )
            row["run_id"] = f"{run_id}/{topology}"


def normalize_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [normalize_row(row) for row in rows]
    _deduplicate_ids(normalized)
    return normalized


def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    if not rows:
        errors.append("database has no rows")
    for index, row in enumerate(rows, 1):
        if list(row) != FIELDS:
            errors.append(f"row {index}: schema/order mismatch")
        if row.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"row {index}: schema_version is not {SCHEMA_VERSION}")
        if row.get("record_kind") == "measurement" and not any(
            row.get(name) is not None for name in METRIC_FIELDS
        ) and not row.get("curve") and not row.get("samples"):
            errors.append(f"row {index}: measurement has no metrics")
        if row.get("curve") is not None and not isinstance(row.get("curve"), list):
            errors.append(f"row {index}: curve is not an array")
        if row.get("samples") is not None and not isinstance(row.get("samples"), dict):
            errors.append(f"row {index}: samples is not an object")
    ids = [row.get("run_id") for row in rows]
    duplicates = sorted(key for key, count in Counter(ids).items() if key and count > 1)
    if duplicates:
        errors.append(f"duplicate run_id: {duplicates}")
    if any(not run_id for run_id in ids):
        errors.append("missing run_id")
    if errors:
        raise ValueError("\n".join(errors[:30]))
    return {
        "records": len(rows),
        "measurements": sum(row["record_kind"] == "measurement" for row in rows),
        "placeholders": sum(row["record_kind"] == "placeholder" for row in rows),
        "unique_run_ids": len(set(ids)),
        "normalization_status": dict(Counter(row["normalization_status"] for row in rows)),
        "engines": dict(Counter(row["engine"] for row in rows)),
        "quants": len({row["quant"] for row in rows}),
    }


def column_definition(column: str) -> str:
    if column in INTEGER_FIELDS:
        return f'"{column}" INTEGER'
    if column in REAL_FIELDS:
        return f'"{column}" REAL'
    return f'"{column}" TEXT'


def write_artifacts(
    rows: Iterable[dict[str, Any]],
    json_path: Path,
    db_path: Path,
    *,
    normalize: bool = True,
) -> dict[str, Any]:
    materialized = normalize_rows(rows) if normalize else list(rows)
    stats = validate_rows(materialized)
    json_tmp = json_path.with_suffix(json_path.suffix + ".tmp")
    db_tmp = db_path.with_suffix(db_path.suffix + ".tmp")
    db_tmp.unlink(missing_ok=True)

    with json_tmp.open("w") as handle:
        for row in materialized:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    connection = sqlite3.connect(db_tmp)
    connection.execute(
        f'CREATE TABLE runs ({", ".join(column_definition(field) for field in FIELDS)})'
    )
    quoted = ", ".join(f'"{field}"' for field in FIELDS)
    placeholders = ", ".join("?" for _ in FIELDS)
    for row in materialized:
        values = []
        for field in FIELDS:
            value = row[field]
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            values.append(value)
        connection.execute(f"INSERT INTO runs ({quoted}) VALUES ({placeholders})", values)
    connection.execute("CREATE UNIQUE INDEX runs_run_id_uq ON runs(run_id)")
    connection.execute("CREATE INDEX runs_model_idx ON runs(model)")
    connection.execute("CREATE INDEX runs_source_idx ON runs(source)")
    connection.execute("CREATE INDEX runs_quant_idx ON runs(quant)")
    connection.commit()
    quick_check = connection.execute("PRAGMA quick_check").fetchone()[0]
    count = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    connection.close()
    if quick_check != "ok" or count != len(materialized):
        raise ValueError(f"SQLite verification failed: quick_check={quick_check}, rows={count}")

    os.replace(json_tmp, json_path)
    os.replace(db_tmp, db_path)
    return stats


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
