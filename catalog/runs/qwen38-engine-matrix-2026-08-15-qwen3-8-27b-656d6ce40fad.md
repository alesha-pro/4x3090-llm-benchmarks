# `qwen38em/sglang-nvfp4/tp4-bf16-nomtp_d253952_c1`

| field | value |
|---|---|
| Date | 2026-08-15 |
| Campaign | qwen38-engine-matrix-2026-08-15 |
| Model | Qwen3.8-27B |
| Checkpoint | Qwen/Qwen3.8-27B |
| Quant | nvfp4 |
| Quant method | nvfp4 |
| Engine | sglang |
| Engine version | 0.0.0.dev501+g22dde1dd5 |
| Objective | context_depth |
| TPS kind | single_stream_decode |
| Layout | TP=4 |
| Context | 262144 |
| Concurrency | 1 |
| Prompt tokens | 253956 |
| Generated tokens | 128 |
| KV cache | bf16 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 54.44 |
| `decode_tok_s` | 54.44 |
| `prefill_tok_s` | 853.1 |
| `total_tok_s` | 0.43 |
| `ttft_p50_ms` | 297695.4 |

## Launch command

```bash
'${ENGINE_ROOT_ALT}/sglang-nvfp4-env/bin/sglang' serve --model-path '${MODEL_ROOT_ALT}/Qwen3.8-27B-NVFP4' --served-model-name bench --host 127.0.0.1 --port 18081 --tp-size 4 --context-length 262144 --mem-fraction-static 0.9 --max-running-requests 16 --chunked-prefill-size 8192 --cuda-graph-max-bs-prefill 256 --disable-radix-cache --disable-custom-all-reduce --language-only --quantization compressed-tensors --kv-cache-dtype bf16 --reasoning-parser qwen3 --fp4-gemm-backend marlin
```

## Engine knobs

```json
{
  "aggregate_active_decode_rate_sum": 54.44,
  "aggregate_decode_window_tok_s": 54.44,
  "attempts": 1,
  "config": "tp4-bf16-nomtp",
  "cuda_graphs": true,
  "custom_all_reduce": false,
  "depth_tokens": 253952,
  "enforce_eager": false,
  "gpu_memory_utilization": 0.9,
  "harness": "release-watch/run_vllm_depth_autonomous.py",
  "mtp": false,
  "prefill_tok_s_aggregate": 853.1,
  "prefix_caching": false,
  "suite": "sglang-depth-autonomous-qwen38-nvfp4",
  "ttft_max_ms": 297695.4,
  "wall_s": 300.04
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Autonomous 288 point engine matrix on 4x RTX 3090, 320 W per card. Every server ran max_model_len 262144 with CUDA graphs and no eager mode, prefix caching off, 128 generated tokens per request. decode_tok_s is the per request steady rate after the first token; for concurrency > 1 the aggregate columns are in knobs. Failed points are not imported: they are capacity limits (FP8 weights with BF16 KV do not fit TP2 at 262144), not crashes, and they carry no numbers. MTP cells sit on short decode windows and are noisy, see source qwen38-verify-2026-08-15 for the long-generation recheck of the best cell.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
