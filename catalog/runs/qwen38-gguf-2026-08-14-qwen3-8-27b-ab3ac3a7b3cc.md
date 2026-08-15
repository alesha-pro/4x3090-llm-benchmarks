# `qwen38gguf/Qwen3.8-27B/llamacpp_Q6_K_4gpu_mtp-off`

| field | value |
|---|---|
| Date | 2026-08-14 |
| Campaign | qwen38-gguf-2026-08-14 |
| Model | Qwen3.8-27B |
| Checkpoint | Qwen/Qwen3.8-27B |
| Quant | gguf-q6_k |
| Quant method | gguf |
| Engine | llama.cpp |
| Engine version | b10428 (885c5bbe8) |
| Objective | single_stream |
| TPS kind | single_stream_decode |
| Layout | TP=4 |
| Context | 8192 |
| Concurrency | 1 |
| Prompt tokens | 58 |
| Generated tokens | 256 |
| KV cache | f16 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 33.73 |
| `decode_tok_s` | 33.73 |
| `prefill_tok_s` | 204.7 |
| `ttft_p50_ms` | 283.3 |

## Launch command

```bash
'${ENGINE_ROOT}/llama.cpp-rw/build/bin/llama-server' --model '${MODEL_ROOT}/Qwen3.8-27B-GGUF/Qwen3.8-27B-Q6_K.gguf' --host 127.0.0.1 --port 18000 --alias bench --n-gpu-layers 999 --ctx-size 8192 --parallel 1 --flash-attn on
```

## Engine knobs

```json
{
  "aggregate_tok_s": 32.64,
  "harness": "release-watch/bench_mtp.sh (llama-server)",
  "mtp": false,
  "temperature": 0.7,
  "wall_s": 7.84
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Release day llama.cpp run: weights were on disk 8 minutes after the HF upload and the sweeps started right after. prefill is pp4096 on top of the stated depth, decode is tg128, three repetitions per point through llama-bench. MTP rows come from llama-server instead, because llama-bench cannot do speculative decoding: there prefill means time to first token on a cold prompt, so the two prefill columns are not the same measurement. The MTP head ships inside the quant (blk.64.nextn) and only loads with --spec-type draft-mtp; without the flag llama.cpp drops it as an unused tensor. 320 W per card, single stream.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
