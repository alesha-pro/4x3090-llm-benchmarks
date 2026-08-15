# `qwen38em/vllm-nvfp4/tp4-bf16-mtp2_d65536_c1`

| field | value |
|---|---|
| Date | 2026-08-15 |
| Campaign | qwen38-engine-matrix-2026-08-15 |
| Model | Qwen3.8-27B |
| Checkpoint | Qwen/Qwen3.8-27B |
| Quant | nvfp4 |
| Quant method | nvfp4 |
| Engine | vllm |
| Engine version | 0.26.0 |
| Objective | context_depth |
| TPS kind | single_stream_decode |
| Layout | TP=4 |
| Context | 262144 |
| Concurrency | 1 |
| Prompt tokens | 65541 |
| Generated tokens | 128 |
| KV cache | bf16 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 23.28 |
| `decode_tok_s` | 23.28 |
| `prefill_tok_s` | 788.9 |
| `total_tok_s` | 0.6 |
| `ttft_p50_ms` | 83075.8 |

## Launch command

```bash
'${ENGINE_ROOT_ALT}/vllm-cross-kv-env/bin/vllm' serve '${MODEL_ROOT_ALT}/Qwen3.8-27B-NVFP4' --served-model-name bench --quantization compressed-tensors --kernel-config '{"linear_backend":"marlin"}' --language-model-only --tensor-parallel-size 4 --disable-custom-all-reduce --attention-backend TRITON_ATTN --kv-cache-dtype bfloat16 --gpu-memory-utilization 0.9 --max-model-len 262144 --max-num-seqs 16 --max-num-batched-tokens 8192 --no-enable-prefix-caching --port 18081 --speculative-config '{"method":"mtp","num_speculative_tokens":2}'
```

## Speculative decoding

```json
{
  "draft_path": null,
  "draft_ref": null,
  "k": null,
  "method": "mtp n=2"
}
```

## Engine knobs

```json
{
  "aggregate_active_decode_rate_sum": 23.28,
  "aggregate_decode_window_tok_s": 23.28,
  "attempts": 1,
  "config": "tp4-bf16-mtp2",
  "cuda_graphs": true,
  "custom_all_reduce": false,
  "depth_tokens": 65536,
  "enforce_eager": false,
  "gpu_memory_utilization": 0.91,
  "harness": "release-watch/run_vllm_depth_autonomous.py",
  "mtp": true,
  "prefill_tok_s_aggregate": 788.9,
  "prefix_caching": false,
  "suite": "vllm-depth-autonomous-qwen38-nvfp4",
  "ttft_max_ms": 83075.8,
  "wall_s": 85.23
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Autonomous 288 point engine matrix on 4x RTX 3090, 320 W per card. Every server ran max_model_len 262144 with CUDA graphs and no eager mode, prefix caching off, 128 generated tokens per request. decode_tok_s is the per request steady rate after the first token; for concurrency > 1 the aggregate columns are in knobs. Failed points are not imported: they are capacity limits (FP8 weights with BF16 KV do not fit TP2 at 262144), not crashes, and they carry no numbers. MTP cells sit on short decode windows and are noisy, see source qwen38-verify-2026-08-15 for the long-generation recheck of the best cell.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
