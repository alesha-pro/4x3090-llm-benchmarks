# `ling3-flash/baseline/depth-65536x256-c1`

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
| Objective | context_depth |
| TPS kind | single_stream_decode |
| Layout | TP=4 |
| Context | 262144 |
| Concurrency | 1 |
| Prompt tokens | 65536 |
| Generated tokens | 256 |
| KV cache | auto |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 101.05184052418235 |
| `decode_tok_s` | 101.05184052418235 |
| `prefill_tok_s` | 1739.918041589852 |
| `total_tok_s` | 7362.123763219151 |
| `req_s` | 0.11189998424153623 |
| `ttft_p50_ms` | 6395.580305004842 |
| `ttft_p99_ms` | 6395.580305004842 |
| `itl_p50_ms` | 9.8990840051556 |
| `tpot_p50_ms` | 9.895910799968988 |

## Launch command

```bash
'${ENGINE_ROOT}/sglang-ling3-env/bin/python' -m sglang.launch_server --model-path '${MODEL_ROOT}/Ling-3.0-flash-int4' --dist-init-addr 127.0.0.1:2347 --host 0.0.0.0 --port 18130 --nnodes 1 --tp-size 4 --mem-fraction-static 0.94 --max-running-requests 8 --chunked-prefill-size 8192 --tool-call-parser ling3 --reasoning-parser ling3 --context-length 262144 --max-mamba-cache-size 64 --enable-fp32-lm-head --disable-shared-experts-fusion
```

## Engine knobs

```json
{
  "accept_length": null,
  "chunked_prefill_size": 8192,
  "label": "depth-65536x256-c1",
  "max_mamba_cache_size": 64,
  "max_running_requests": 8,
  "mem_fraction_static": 0.94
}
```

## Samples

```json
{
  "cold_prefill_boundary_uncertainty_seconds": 0.5603179931640625,
  "cold_prefill_seconds": 37.666141986846924,
  "completed": 1,
  "exact_lengths": true
}
```

## Provenance

- `repo:llm-bench/results/daily-papers/2026-08-05/ling3-flash-int4-4x3090-saturation/exact/baseline/depth-65536x256-c1.jsonl`

## Notes

exact token lengths; ignore_eos; randomized synthetic tokens; fixed 220 W/GPU

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
