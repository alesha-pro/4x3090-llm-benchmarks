# `qwen38em/sglang-nvfp4/tp4-fp8-mtp4_d8192_c1`

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
| Prompt tokens | 8221 |
| Generated tokens | 128 |
| KV cache | fp8 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 82.55 |
| `decode_tok_s` | 82.55 |
| `prefill_tok_s` | 857.7 |
| `total_tok_s` | 11.51 |
| `ttft_p50_ms` | 9584.5 |

## Launch command

```bash
'${ENGINE_ROOT_ALT}/sglang-nvfp4-env/bin/sglang' serve --model-path '${MODEL_ROOT_ALT}/Qwen3.8-27B-NVFP4' --served-model-name bench --host 127.0.0.1 --port 18081 --tp-size 4 --context-length 262144 --mem-fraction-static 0.9 --max-running-requests 16 --chunked-prefill-size 8192 --cuda-graph-max-bs-prefill 256 --disable-radix-cache --disable-custom-all-reduce --language-only --quantization compressed-tensors --kv-cache-dtype fp8_e4m3 --reasoning-parser qwen3 --fp4-gemm-backend marlin --max-total-tokens 262144 --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

## Speculative decoding

```json
{
  "draft_path": null,
  "draft_ref": null,
  "k": null,
  "method": "eagle steps=3 topk=1 draft=4"
}
```

## Engine knobs

```json
{
  "aggregate_active_decode_rate_sum": 82.55,
  "aggregate_decode_window_tok_s": 82.55,
  "attempts": 1,
  "config": "tp4-fp8-mtp4",
  "cuda_graphs": true,
  "custom_all_reduce": false,
  "depth_tokens": 8192,
  "enforce_eager": false,
  "gpu_memory_utilization": 0.9,
  "harness": "release-watch/run_vllm_depth_autonomous.py",
  "mtp": true,
  "prefill_tok_s_aggregate": 857.7,
  "prefix_caching": false,
  "suite": "sglang-depth-autonomous-qwen38-nvfp4",
  "ttft_max_ms": 9584.5,
  "wall_s": 11.12
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Autonomous 288 point engine matrix on 4x RTX 3090, 320 W per card. Every server ran max_model_len 262144 with CUDA graphs and no eager mode, prefix caching off, 128 generated tokens per request. decode_tok_s is the per request steady rate after the first token; for concurrency > 1 the aggregate columns are in knobs. Failed points are not imported: they are capacity limits (FP8 weights with BF16 KV do not fit TP2 at 262144), not crashes, and they carry no numbers. MTP cells sit on short decode windows and are noisy, see source qwen38-verify-2026-08-15 for the long-generation recheck of the best cell.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
