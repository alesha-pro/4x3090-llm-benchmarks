# `qwen38em/vllm-nvfp4/tp2-fp8-nomtp_d253952_c1`

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
| Layout | TP=2 |
| Context | 262144 |
| Concurrency | 1 |
| Prompt tokens | 253956 |
| Generated tokens | 128 |
| KV cache | fp8 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 52.84 |
| `decode_tok_s` | 52.84 |
| `prefill_tok_s` | 1001.8 |
| `total_tok_s` | 0.18 |
| `ttft_p50_ms` | 253509.3 |

## Launch command

```bash
'${ENGINE_ROOT_ALT}/vllm-cross-kv-env/bin/vllm' serve '${MODEL_ROOT_ALT}/Qwen3.8-27B-NVFP4' --served-model-name bench --quantization compressed-tensors --kernel-config '{"linear_backend":"marlin"}' --language-model-only --tensor-parallel-size 2 --disable-custom-all-reduce --attention-backend FLASHINFER --kv-cache-dtype fp8 --gpu-memory-utilization 0.9 --max-model-len 262144 --max-num-seqs 16 --max-num-batched-tokens 8192 --no-enable-prefix-caching --port 18081
```

## Engine knobs

```json
{
  "aggregate_active_decode_rate_sum": 52.84,
  "aggregate_decode_window_tok_s": 52.84,
  "attempts": 1,
  "config": "tp2-fp8-nomtp",
  "cuda_graphs": true,
  "custom_all_reduce": false,
  "depth_tokens": 253952,
  "enforce_eager": false,
  "gpu_memory_utilization": 0.91,
  "harness": "release-watch/run_vllm_depth_autonomous.py",
  "mtp": false,
  "prefill_tok_s_aggregate": 1001.8,
  "prefix_caching": false,
  "suite": "vllm-depth-autonomous-qwen38-nvfp4",
  "ttft_max_ms": 253509.3,
  "wall_s": 254.37
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Autonomous 288 point engine matrix on 4x RTX 3090, 320 W per card. Every server ran max_model_len 262144 with CUDA graphs and no eager mode, prefix caching off, 128 generated tokens per request. decode_tok_s is the per request steady rate after the first token; for concurrency > 1 the aggregate columns are in knobs. Failed points are not imported: they are capacity limits (FP8 weights with BF16 KV do not fit TP2 at 262144), not crashes, and they carry no numbers. MTP cells sit on short decode windows and are noisy, see source qwen38-verify-2026-08-15 for the long-generation recheck of the best cell.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
