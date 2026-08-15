# `depth/DeepSeek-V4-Flash-0731/llamacpp-cchuter_ds4-0731-131k-ts1111_d65536`

| field | value |
|---|---|
| Date | 2026-08-04 |
| Campaign | depth-curves-2026-08-04 |
| Model | DeepSeek-V4-Flash-0731 |
| Checkpoint | unsloth/DeepSeek-V4-Flash-0731-GGUF |
| Quant | gguf-ud-iq2_xxs |
| Quant method | gguf |
| Engine | llama.cpp |
| Engine version | cchuter fork 7b09cda |
| Objective | single_stream |
| TPS kind | single_stream_wall |
| Layout | TP=4 |
| Context | 131072 |
| Concurrency | 1 |
| Prompt tokens | 65557 |
| Generated tokens | 128 |
| KV cache | f16 |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 36.10795715001022 |
| `decode_tok_s` | 36.10795715001022 |
| `prefill_tok_s` | 424.61264677779224 |

## Launch command

```bash
'${SSD_ROOT}/engines/llama.cpp-v4-cchuter/build-v4-cuda/bin/llama-server' -m '${RIG_MOUNT}/nvme/ds4-models/0731-UD-IQ2_XXS/UD-IQ2_XXS/DeepSeek-V4-Flash-0731-UD-IQ2_XXS-00001-of-00003.gguf' -ngl 999 --split-mode layer --flash-attn on --no-repack --ctx-size 131072 --batch-size 4096 --ubatch-size 512 -t 8 --poll 100 -ts 1,1,1,1 --parallel 1 --jinja --reasoning on --reasoning-format deepseek --reasoning-budget 2048
```

## Engine knobs

```json
{
  "batch": 4096,
  "depth_tokens": 65536,
  "env": {
    "DSV4_CONSTANT_SHAPE": "1",
    "DSV4_DECODE_FUSED_IDX": "1",
    "DSV4_DECODE_RADIX_TOPK": "1",
    "DSV4_FA_UNION": "1",
    "DSV4_GLU_FUSE": "1",
    "DSV4_IDX_SKIP": "1",
    "DSV4_MMVQ_SMALLK": "1",
    "DSV4_MOE_FUSE": "1",
    "DSV4_MOE_RESIDENT": "1",
    "DSV4_MOE_TILE": "1",
    "DSV4_PREFILL_RADIX_TOPK": "1",
    "DSV4_SPARSE_FA": "1",
    "GGML_CUDA_P2P": "1"
  },
  "flash_attn": true,
  "split_mode": "layer",
  "tensor_split": "1,1,1,1",
  "ubatch": 512
}
```

## Samples

```json
{
  "draft_n": null,
  "draft_n_accepted": null,
  "repeats": 1
}
```

## Provenance

- `repo:llm-bench/results/ds4-flash-0731-2026-08-04/ds4-0731-131k-ts1111.json`

## Notes

depth curve; prefill and decode measured in one request at depth 65536; harness llm-bench/results/*/depth_bench.py

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
