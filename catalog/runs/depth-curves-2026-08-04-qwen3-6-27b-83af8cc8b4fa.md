# `depth/Qwen3.6-27B/llamacpp_1x-350W-200k-ub512-q4_0-mtp2_d0`

| field | value |
|---|---|
| Date | 2026-08-04 |
| Campaign | depth-curves-2026-08-04 |
| Model | Qwen3.6-27B |
| Checkpoint | unsloth/Qwen3.6-27B-MTP-GGUF |
| Quant | gguf-q4_k_m |
| Quant method | gguf |
| Engine | llama.cpp |
| Engine version | b10013 (a4ce2595c) |
| Objective | single_stream |
| TPS kind | single_stream_wall |
| Layout | TP=1 |
| Context | 200000 |
| Concurrency | 1 |
| Prompt tokens | 11 |
| Generated tokens | 128 |
| KV cache | q4_0 |
| Power limit | 350 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 63.922845125933 |
| `decode_tok_s` | 63.922845125933 |
| `prefill_tok_s` | 26.357532743244082 |

## Launch command

```bash
'${ENGINE_ROOT}/llama.cpp/build/bin/llama-server' -m '${MODEL_ROOT}/Qwen3.6-27B-MTP-GGUF-unsloth/Qwen3.6-27B-Q4_K_M.gguf' -ngl 99 --flash-attn on -c 200000 -b 4096 -ub 512 --cache-type-k q4_0 --cache-type-v q4_0 -np 1 -t 16 --jinja --reasoning off --reasoning-format deepseek --spec-type draft-mtp --spec-draft-n-max 2
```

## Speculative decoding

```json
{
  "draft_path": null,
  "draft_ref": null,
  "k": null,
  "method": "draft-mtp n=2"
}
```

## Engine knobs

```json
{
  "batch": 4096,
  "depth_tokens": 0,
  "flash_attn": true,
  "np": 1,
  "split_mode": "none",
  "ubatch": 512
}
```

## Samples

```json
{
  "draft_n": 90,
  "draft_n_accepted": 81,
  "repeats": 1
}
```

## Provenance

- `repo:llm-bench/results/qwen36-27b-depth-2026-08-04/1x-350W-200k-ub512-q4_0-mtp2.json`

## Notes

depth curve; prefill and decode measured in one request at depth 0; harness llm-bench/results/*/depth_bench.py

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
