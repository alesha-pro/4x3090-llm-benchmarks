# `ling3-flash/baseline/saturation-1024x256-c2`

| field | value |
|---|---|
| Date | 2026-08-05 |
| Campaign | ling3-flash-int4-2026-08-05 |
| Model | Ling-3.0-flash |
| Checkpoint | inclusionAI/Ling-3.0-flash-int4@ca3ea63b0255d212c4fe6020db9e0a51ce136006 |
| Quant | compressed-tensors-int4-g32-symmetric |
| Quant method | compressed-tensors |
| Engine | sglang |
| Engine version | 0.0.0.dev1+g3f475ee2c |
| Objective | concurrency_sweep |
| TPS kind | aggregate |
| Layout | TP=4 |
| Context | 262144 |
| Concurrency | 2 |
| Prompt tokens | 1024 |
| Generated tokens | 256 |
| KV cache | auto |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 149.07516173187582 |
| `total_tok_s` | 745.3758086593791 |
| `req_s` | 0.5823248505151399 |
| `ttft_p50_ms` | 898.3391450019553 |
| `ttft_p99_ms` | 936.4326034270925 |
| `itl_p50_ms` | 9.908561994961929 |
| `tpot_p50_ms` | 9.920692454918525 |

## Launch command

```bash
'${ENGINE_ROOT}/sglang-ling3-env/bin/python' -m sglang.launch_server --model-path '${MODEL_ROOT}/Ling-3.0-flash-int4' --dist-init-addr 127.0.0.1:2347 --host 0.0.0.0 --port 18130 --nnodes 1 --tp-size 4 --mem-fraction-static 0.94 --max-running-requests 8 --chunked-prefill-size 8192 --tool-call-parser ling3 --reasoning-parser ling3 --context-length 262144 --max-mamba-cache-size 64 --enable-fp32-lm-head --disable-shared-experts-fusion
```

## Engine knobs

```json
{
  "accept_length": null,
  "chunked_prefill_size": 8192,
  "label": "saturation-1024x256-c2",
  "max_mamba_cache_size": 64,
  "max_running_requests": 8,
  "mem_fraction_static": 0.94
}
```

## Samples

```json
{
  "cold_prefill_boundary_uncertainty_seconds": null,
  "cold_prefill_seconds": null,
  "completed": 4,
  "exact_lengths": true
}
```

## Provenance

- `repo:llm-bench/results/daily-papers/2026-08-05/ling3-flash-int4-4x3090-saturation/exact/baseline/saturation-1024x256-c2.jsonl`

## Notes

exact token lengths; ignore_eos; randomized synthetic tokens; fixed 220 W/GPU

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
