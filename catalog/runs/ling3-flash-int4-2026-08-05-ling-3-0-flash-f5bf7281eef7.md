# `ling3-flash/baseline/depth-131072x256-c1`

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
| Prompt tokens | 131072 |
| Generated tokens | 256 |
| KV cache | auto |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 88.98636841081402 |
| `decode_tok_s` | 88.98636841081402 |
| `prefill_tok_s` | 1260.365164764781 |
| `total_tok_s` | 10132.921364399068 |
| `req_s` | 0.07715735688047537 |
| `ttft_p50_ms` | 10082.751244000974 |
| `ttft_p99_ms` | 10082.751244000974 |
| `itl_p50_ms` | 11.072772002080455 |
| `tpot_p50_ms` | 11.237676262766506 |

## Launch command

```bash
'${ENGINE_ROOT}/sglang-ling3-env/bin/python' -m sglang.launch_server --model-path '${MODEL_ROOT}/Ling-3.0-flash-int4' --dist-init-addr 127.0.0.1:2347 --host 0.0.0.0 --port 18130 --nnodes 1 --tp-size 4 --mem-fraction-static 0.94 --max-running-requests 8 --chunked-prefill-size 8192 --tool-call-parser ling3 --reasoning-parser ling3 --context-length 262144 --max-mamba-cache-size 64 --enable-fp32-lm-head --disable-shared-experts-fusion
```

## Engine knobs

```json
{
  "accept_length": null,
  "chunked_prefill_size": 8192,
  "label": "depth-131072x256-c1",
  "max_mamba_cache_size": 64,
  "max_running_requests": 8,
  "mem_fraction_static": 0.94
}
```

## Samples

```json
{
  "cold_prefill_boundary_uncertainty_seconds": 0.5621864795684814,
  "cold_prefill_seconds": 103.99525761604309,
  "completed": 1,
  "exact_lengths": true
}
```

## Provenance

- `repo:llm-bench/results/daily-papers/2026-08-05/ling3-flash-int4-4x3090-saturation/exact/baseline/depth-131072x256-c1.jsonl`

## Notes

exact token lengths; ignore_eos; randomized synthetic tokens; fixed 220 W/GPU

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
