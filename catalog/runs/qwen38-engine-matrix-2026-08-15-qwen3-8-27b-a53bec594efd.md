# `qwen38em/sglang-fp8/tp4-bf16-nomtp_d8192_c4`

| field | value |
|---|---|
| Date | 2026-08-15 |
| Campaign | qwen38-engine-matrix-2026-08-15 |
| Model | Qwen3.8-27B |
| Checkpoint | Qwen/Qwen3.8-27B |
| Quant | fp8-static |
| Quant method | fp8 |
| Engine | sglang |
| Engine version | 0.0.0.dev501+g22dde1dd5 |
| Objective | concurrency_sweep |
| TPS kind | aggregate_output |
| Layout | TP=4 |
| Context | 262144 |
| Concurrency | 4 |
| Prompt tokens | 8224 |
| Generated tokens | 128 |
| KV cache | bf16 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 16.58 |
| `decode_tok_s` | 23.38 |
| `prefill_tok_s` | 273.4 |
| `total_tok_s` | 6.21 |
| `ttft_p50_ms` | 30144.8 |

## Launch command

```bash
'${ENGINE_ROOT_ALT}/sglang-nvfp4-env/bin/sglang' serve --model-path '${MODEL_ROOT_ALT}/Qwen3.8-27B-FP8' --served-model-name bench --host 127.0.0.1 --port 18081 --tp-size 4 --context-length 262144 --mem-fraction-static 0.9 --max-running-requests 16 --chunked-prefill-size 8192 --cuda-graph-max-bs-prefill 256 --disable-radix-cache --disable-custom-all-reduce --language-only --quantization fp8 --kv-cache-dtype bf16 --reasoning-parser qwen3
```

## Engine knobs

```json
{
  "aggregate_active_decode_rate_sum": 92.05,
  "aggregate_decode_window_tok_s": 16.58,
  "attempts": 1,
  "config": "tp4-bf16-nomtp",
  "cuda_graphs": true,
  "custom_all_reduce": false,
  "depth_tokens": 8192,
  "enforce_eager": false,
  "gpu_memory_utilization": 0.9,
  "harness": "release-watch/run_vllm_depth_autonomous.py",
  "mtp": false,
  "prefill_tok_s_aggregate": 1036.7,
  "prefix_caching": false,
  "suite": "sglang-depth-autonomous-qwen38-fp8",
  "ttft_max_ms": 31733.0,
  "wall_s": 33.04
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Autonomous 288 point engine matrix on 4x RTX 3090, 320 W per card. Every server ran max_model_len 262144 with CUDA graphs and no eager mode, prefix caching off, 128 generated tokens per request. decode_tok_s is the per request steady rate after the first token; for concurrency > 1 the aggregate columns are in knobs. Failed points are not imported: they are capacity limits (FP8 weights with BF16 KV do not fit TP2 at 262144), not crashes, and they carry no numbers. MTP cells sit on short decode windows and are noisy, see source qwen38-verify-2026-08-15 for the long-generation recheck of the best cell.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
