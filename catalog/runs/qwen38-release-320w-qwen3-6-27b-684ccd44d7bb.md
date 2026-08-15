# `qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass1_c4`

| field | value |
|---|---|
| Date | 2026-08-12 |
| Campaign | qwen38-release-320w |
| Model | Qwen3.6-27B |
| Checkpoint | Qwen3.6-27B-fp8-static |
| Quant | fp8-static |
| Quant method | fp8 |
| Engine | vllm |
| Engine version | 0.23.0 |
| Objective | aggregate |
| TPS kind | aggregate_output |
| Layout | TP=4 |
| Context | 32768 |
| Concurrency | 4 |
| Prompt tokens | 43 |
| Generated tokens | 256 |
| KV cache | auto |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 138.27 |
| `decode_tok_s` | 43.58 |
| `ttft_p50_ms` | 1551.7 |
| `ttft_p99_ms` | 1551.9 |

## Launch command

```bash
vllm serve '${MODEL_ROOT}/Qwen3.6-27B-FP8' --host 127.0.0.1 --port 18000 --served-model-name bench --tensor-parallel-size 4 --max-model-len 32768 --gpu-memory-utilization 0.9 --trust-remote-code
```

## Engine knobs

```json
{
  "attention_backend": "FLASH_ATTN",
  "enable_chunked_prefill": "default",
  "enable_thinking": false,
  "flashinfer_sampler": false,
  "gpu_memory_utilization": 0.9,
  "harness": "release-watch/bench_matrix.py",
  "max_num_seqs": "default",
  "pass": 1,
  "reproduced": false,
  "temperature": 0.7
}
```

## Samples

```json
{
  "requests_ok": 4,
  "total_tokens": 1024,
  "wall_s": 7.41
}
```

## Provenance

- `repo:llm-bench/results/qwen38-release-2026-08-12/raw-pass1/matrix.json`

## Notes

Qwen3.6-27B-FP8 re-measured at the power limit actually set on the rig on 2026-08-12, which was 320 W, not the 220 W the rest of the DB is taken at. Run twice back to back to separate signal from warmup. c=1 and c=32 reproduced within 2%; c=4 and c=16 did not (aggregate 19% and 61% apart, TTFT p50 4x apart) and are kept only with reproduced=false. First pass server took 395 s to come up against 145 s for the second, so the compile cache was cold and warmup drifted through the first matrix. NOT comparable to source=tp-ab-p2p (220 W): that harness uses a 512-token prompt, temperature 0.0, a 20 s duration window per ladder point and separate server flags per objective (--max-num-seqs 1 for single stream, 256 + --enable-chunked-prefill for aggregate). This harness uses a 43-token prompt, temperature 0.7, fixed 256 output tokens x N requests and one default server for every level. Power limit is one of five differences.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
