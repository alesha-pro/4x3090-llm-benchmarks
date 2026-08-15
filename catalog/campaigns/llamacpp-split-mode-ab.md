# llamacpp-split-mode-ab

9 measurements.

| date | run | model | quant | engine | layout | ctx | conc | primary metric |
|---|---|---|---|---|---|---:|---:|---:|
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-tensor_tp4x1_spec-none_pl220_tg128](../runs/llamacpp-split-mode-ab-qwen3-5-9b-b5555be54eb6.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=4 | 128 | 1 | 138.96 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-tensor_tp4x1_spec-none_pl220_pp512](../runs/llamacpp-split-mode-ab-qwen3-5-9b-c82e0368802f.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=4 | 512 | 1 | 2176.62 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-tensor_tp4x1_spec-none_pl220_pp2048](../runs/llamacpp-split-mode-ab-qwen3-5-9b-c34f75bc592e.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=4 | 2048 | 1 | 2112.96 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-none_tp1x1_spec-none_pl220_tg128](../runs/llamacpp-split-mode-ab-qwen3-5-9b-61341dd9d73c.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=1 | 128 | 1 | 54.24 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-none_tp1x1_spec-none_pl220_pp512](../runs/llamacpp-split-mode-ab-qwen3-5-9b-ca744f6ec7bc.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=1 | 512 | 1 | 2672.1 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-none_tp1x1_spec-none_pl220_pp2048](../runs/llamacpp-split-mode-ab-qwen3-5-9b-f203e92b941b.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=1 | 2048 | 1 | 2556.48 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-layer_tp4x1_spec-none_pl220_tg128](../runs/llamacpp-split-mode-ab-qwen3-5-9b-8d37ecb11b84.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=4 | 128 | 1 | 84.91 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-layer_tp4x1_spec-none_pl220_pp512](../runs/llamacpp-split-mode-ab-qwen3-5-9b-164ad07436de.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=4 | 512 | 1 | 4061.89 output tok/s |
| 2026-07-31 | [smab/Qwen3.5-9B/llamacpp_GGUF-Q8_0_sm-layer_tp4x1_spec-none_pl220_pp2048](../runs/llamacpp-split-mode-ab-qwen3-5-9b-f624d82465d2.md) | Qwen3.5-9B | gguf-q8_0 | llama.cpp 79ca732e1 | TP=4 | 2048 | 1 | 6349.11 output tok/s |

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
