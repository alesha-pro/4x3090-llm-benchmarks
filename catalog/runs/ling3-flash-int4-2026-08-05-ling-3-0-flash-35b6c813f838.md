# `ling3-flash/nextn/saturation-1024x256-c1`

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
| TPS kind | single_stream_wall |
| Layout | TP=4 |
| Context | 33024 |
| Concurrency | 1 |
| Prompt tokens | 1024 |
| Generated tokens | 256 |
| KV cache | auto |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 132.19864265608348 |
| `total_tok_s` | 660.9932132804174 |
| `req_s` | 0.5164009478753261 |
| `ttft_p50_ms` | 423.81159299839055 |
| `ttft_p99_ms` | 427.4189444447984 |
| `itl_p50_ms` | 4.805373002454871 |
| `tpot_p50_ms` | 5.8550618588353744 |

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
  "accept_length": 3.09,
  "chunked_prefill_size": 8192,
  "label": "saturation-1024x256-c1",
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
  "completed": 4,
  "exact_lengths": true
}
```

## Provenance

- `repo:llm-bench/results/daily-papers/2026-08-05/ling3-flash-int4-4x3090-saturation/nextn32k/nextn/saturation-1024x256-c1.jsonl`

## Notes

exact token lengths; ignore_eos; randomized synthetic tokens; fixed 220 W/GPU

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
