# `qwen38em/vllm-fp8/tp4-bf16-nomtp_d8192_c1`

| field | value |
|---|---|
| Date | 2026-08-15 |
| Campaign | qwen38-engine-matrix-2026-08-15 |
| Model | Qwen3.8-27B |
| Checkpoint | Qwen/Qwen3.8-27B |
| Quant | fp8-static |
| Quant method | fp8 |
| Engine | vllm |
| Engine version | 0.26.0 |
| Objective | context_depth |
| TPS kind | single_stream_decode |
| Layout | TP=4 |
| Context | 262144 |
| Concurrency | 1 |
| Prompt tokens | 8222 |
| Generated tokens | 128 |
| KV cache | bf16 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 63.84 |
| `decode_tok_s` | 63.84 |
| `prefill_tok_s` | 805.0 |
| `total_tok_s` | 4.64 |
| `ttft_p50_ms` | 10213.2 |

## Launch command

```bash
'${ENGINE_ROOT_ALT}/vllm-cross-kv-env/bin/vllm' serve '${MODEL_ROOT_ALT}/Qwen3.8-27B-FP8' --served-model-name bench --quantization fp8 --kernel-config '{"linear_backend":"marlin"}' --language-model-only --tensor-parallel-size 4 --disable-custom-all-reduce --attention-backend TRITON_ATTN --kv-cache-dtype bfloat16 --gpu-memory-utilization 0.91 --max-model-len 262144 --max-num-seqs 16 --max-num-batched-tokens 8192 --no-enable-prefix-caching --port 18081
```

## Engine knobs

```json
{
  "aggregate_active_decode_rate_sum": 63.84,
  "aggregate_decode_window_tok_s": 63.84,
  "attempts": 1,
  "config": "tp4-bf16-nomtp",
  "cuda_graphs": true,
  "custom_all_reduce": false,
  "depth_tokens": 8192,
  "enforce_eager": false,
  "gpu_memory_utilization": 0.91,
  "harness": "release-watch/run_vllm_depth_autonomous.py",
  "mtp": false,
  "prefill_tok_s_aggregate": 805.0,
  "prefix_caching": false,
  "suite": "vllm-depth-autonomous-qwen38-fp8",
  "ttft_max_ms": 10213.2,
  "wall_s": 11.0
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Autonomous 288 point engine matrix on 4x RTX 3090, 320 W per card. Every server ran max_model_len 262144 with CUDA graphs and no eager mode, prefix caching off, 128 generated tokens per request. decode_tok_s is the per request steady rate after the first token; for concurrency > 1 the aggregate columns are in knobs. Failed points are not imported: they are capacity limits (FP8 weights with BF16 KV do not fit TP2 at 262144), not crashes, and they carry no numbers. MTP cells sit on short decode windows and are noisy, see source qwen38-verify-2026-08-15 for the long-generation recheck of the best cell.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
