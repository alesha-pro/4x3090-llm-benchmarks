# `ling3-flash/nextn/saturation-1024x256-c8`

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
| Context | 33024 |
| Concurrency | 8 |
| Prompt tokens | 1024 |
| Generated tokens | 256 |
| KV cache | auto |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 205.1121446049035 |
| `total_tok_s` | 1025.5607230245175 |
| `req_s` | 0.8012193148629043 |
| `ttft_p50_ms` | 5287.446611000632 |
| `ttft_p99_ms` | 6589.045686102327 |
| `itl_p50_ms` | 12.049299664795399 |
| `tpot_p50_ms` | 15.904119347054372 |

## Launch command

```bash
'${ENGINE_ROOT}/sglang-ling3-env/bin/python' -m sglang.launch_server --model-path '${MODEL_ROOT}/Ling-3.0-flash-int4' --dist-init-addr 127.0.0.1:2347 --host 0.0.0.0 --port 18130 --nnodes 1 --tp-size 4 --mem-fraction-static 0.94 --max-running-requests 4 --chunked-prefill-size 8192 --tool-call-parser ling3 --reasoning-parser ling3 --context-length 33024 --max-mamba-cache-size 64 --enable-fp32-lm-head --disable-shared-experts-fusion --speculative-algorithm NEXTN
```

## Speculative decoding

```json
{
  "draft_path": null,
  "draft_ref": null,
  "k": null,
  "method": "nextn built-in"
}
```

## Engine knobs

```json
{
  "accept_length": 2.91312893081761,
  "chunked_prefill_size": 8192,
  "label": "saturation-1024x256-c8",
  "max_mamba_cache_size": 64,
  "max_running_requests": 4,
  "mem_fraction_static": 0.94
}
```

## Samples

```json
{
  "cold_prefill_boundary_uncertainty_seconds": null,
  "cold_prefill_seconds": null,
  "completed": 16,
  "exact_lengths": true
}
```

## Provenance

- `repo:llm-bench/results/daily-papers/2026-08-05/ling3-flash-int4-4x3090-saturation/nextn32k/nextn/saturation-1024x256-c8.jsonl`

## Notes

exact token lengths; ignore_eos; randomized synthetic tokens; fixed 220 W/GPU

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
