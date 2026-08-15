# `qwen38gguf/Qwen3.8-27B/llamacpp_Q5_K_M_1gpu_d16384`

| field | value |
|---|---|
| Date | 2026-08-14 |
| Campaign | qwen38-gguf-2026-08-14 |
| Model | Qwen3.8-27B |
| Checkpoint | Qwen/Qwen3.8-27B |
| Quant | gguf-q5_k_m |
| Quant method | gguf |
| Engine | llama.cpp |
| Engine version | b10428 (885c5bbe8) |
| Objective | context_depth |
| TPS kind | single_stream_decode |
| Layout | TP=1 |
| Context | 262144 |
| Concurrency | 1 |
| Prompt tokens | 4096 |
| Generated tokens | 128 |
| KV cache | f16 |
| Power limit | 320 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 33.855786 |
| `decode_tok_s` | 33.855786 |
| `prefill_tok_s` | 1019.276136 |

## Launch command

```bash
'${ENGINE_ROOT}/llama.cpp-rw/build/bin/llama-bench' --model '${MODEL_ROOT}/Qwen3.8-27B-GGUF/Qwen3.8-27B-Q5_K_M.gguf' --n-gpu-layers 999 --flash-attn on --n-prompt 4096 --n-gen 128 --n-depth 16384 --repetitions 3 -o json
```

## Engine knobs

```json
{
  "decode_stddev_ts": 0.116052,
  "depth_tokens": 16384,
  "flash_attn": true,
  "harness": "release-watch/bench_depth.sh (llama-bench)",
  "n_gpu_layers": 999,
  "prefill_stddev_ts": 0.903962,
  "repetitions": 3,
  "split_mode": "none"
}
```

## Provenance

- `repo:llm-bench/results/qwen38-full-2026-08-14`

## Notes

Release day llama.cpp run: weights were on disk 8 minutes after the HF upload and the sweeps started right after. prefill is pp4096 on top of the stated depth, decode is tg128, three repetitions per point through llama-bench. MTP rows come from llama-server instead, because llama-bench cannot do speculative decoding: there prefill means time to first token on a cold prompt, so the two prefill columns are not the same measurement. The MTP head ships inside the quant (blk.64.nextn) and only loads with --spec-type draft-mtp; without the flag llama.cpp drops it as an unused tensor. 320 W per card, single stream.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
