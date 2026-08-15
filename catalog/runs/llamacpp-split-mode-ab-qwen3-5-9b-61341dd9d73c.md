# `smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-none_tp1x1_spec-none_pl220_tg128`

| field | value |
|---|---|
| Date | 2026-07-31 |
| Campaign | llamacpp-split-mode-ab |
| Model | Qwen3.5-9B |
| Checkpoint | Qwen3.5-9B-Q8_0.gguf |
| Quant | gguf-q8_0 |
| Quant method | gguf |
| Engine | llama.cpp |
| Engine version | 79ca732e1 |
| Objective | decode |
| TPS kind | single_stream_wall |
| Layout | TP=1 |
| Context | 128 |
| Concurrency | 1 |
| Generated tokens | 128 |
| KV cache | f16 |
| Power limit | 220 W/GPU |
| Normalization | exact |

## Metrics

| metric | value |
|---|---:|
| `output_tok_s` | 54.24 |
| `decode_tok_s` | 54.24 |

## Launch command

```bash
'${ENGINE_ROOT}/llama.cpp-inkling/build/bin/llama-bench' -m '${MODEL_ROOT}/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q8_0.gguf' -ngl 99 -t 32 -fa 1 -sm none -mg 0 -p 0 -n 128 -r 3 -o md
```

## Engine knobs

```json
{
  "engine_build": "llama.cpp PR#25731 @79ca732e1 (build 10181)",
  "flash_attn": true,
  "gpus": 1,
  "ngl": 99,
  "split_mode": "none",
  "test": "tg128",
  "threads": 32
}
```

## Samples

```json
{
  "repeats": 3,
  "stddev_tok_s": 0.56
}
```

## Provenance

- `repo:llm-bench/results/inkling-small-iq2m-4x3090-2026-07-31/tp-ab-qwen9b.log`

## Notes

Split-mode A/B on 4x RTX 3090 at 220 W, PCIe 3.0 x16, no NVLink. Same 8.86 GiB model in all arms, so the single-GPU arm is a real baseline rather than a smaller configuration. '-sm tensor' is llama.cpp's tensor parallelism (PR #19378 plus the CUDA AllReduce kernel in #22299), marked experimental. '-sm row' could not be measured: this build reports 'device CUDA0 does not support split buffers' for every model tried. Run was the control for the Inkling session, where '-sm tensor' is refused outright because llm_arch_supports_sm_tensor() excludes LLM_ARCH_INKLING. The layer arm beating the single-GPU arm on decode is unexplained here and is plausibly the 220 W cap rather than parallelism.

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
