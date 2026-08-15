# `inkling/Inkling-Small/llamacpp_IQ2_M_tp4x1_spec-none_d0_pl220_pp2048`

| field | value |
|---|---|
| Date | 2026-07-31 |
| Campaign | inkling-iq2m-llamacpp-pr25731 |
| Model | Inkling-Small |
| Checkpoint | unsloth/Inkling-Small-GGUF@UD-IQ2_M |
| Quant | gguf-ud-iq2_m |
| Quant method | gguf |
| Engine | llama.cpp |
| Engine version | 79ca732e1 |
| Objective | prefill |
| TPS kind | single_stream_wall |
| Layout | TP=4 |
| Context | 2048 |
| Concurrency | 1 |
| Prompt tokens | 2048 |
| KV cache | f16 |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 615.21 |
| `prefill_tok_s` | 615.21 |

## Launch command

```bash
'${ENGINE_ROOT}/llama.cpp-inkling/build/bin/llama-bench' -m '${MODEL_ROOT}/Inkling-Small-GGUF/UD-IQ2_M/Inkling-Small-UD-IQ2_M-00001-of-00003.gguf' -ngl 99 -t 32 -fa 1 -p 2048 -n 0 -r 2 -o md
```

## Engine knobs

```json
{
  "depth": 0,
  "engine_build": "llama.cpp PR#25731 @79ca732e1 (build 10181)",
  "flash_attn": true,
  "ngl": 99,
  "split_mode": "layer",
  "test": "pp2048",
  "threads": 32
}
```

## Samples

```json
{
  "repeats": 2,
  "stddev_tok_s": 0.44
}
```

## Provenance

- `repo:llm-bench/results/inkling-small-iq2m-4x3090-2026-07-31/bench-full.log`

## Notes

Inkling-Small (276B total / 12B active MoE, arch 'inkling') on 4x RTX 3090 at 220 W, layer split, llama.cpp built from the unmerged architecture PR #25731 at commit 79ca732e1 (build 10181); mainline master had no inkling support on this date. Weights 76.76 GiB, reported 2.7 bpw. Text only: the GGUF repo ships no mmproj, loader reports modalities=text. Context ceiling probe reached 131072 with about 240 MiB left on the two fullest cards. Rows at depth >= 65536 are single repeats, so their stddev is absent rather than zero. The pp8192 point at depth 0 was measured after the sweep so the prefill series uses one prompt size at every depth.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
