# qwen38-release-320w

8 measurements.

| date | run | model | quant | engine | layout | ctx | conc | primary metric |
|---|---|---|---|---|---|---:|---:|---:|
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass2_c4](../runs/qwen38-release-320w-qwen3-6-27b-41bbd99137fa.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 4 | 164.83 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass2_c32](../runs/qwen38-release-320w-qwen3-6-27b-efb6245682eb.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 32 | 538.82 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass2_c16](../runs/qwen38-release-320w-qwen3-6-27b-93512e2ee099.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 16 | 317.8 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass2_c1](../runs/qwen38-release-320w-qwen3-6-27b-bb469472318d.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 1 | 62.23 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass1_c4](../runs/qwen38-release-320w-qwen3-6-27b-684ccd44d7bb.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 4 | 138.27 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass1_c32](../runs/qwen38-release-320w-qwen3-6-27b-6e707edf2229.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 32 | 536.71 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass1_c16](../runs/qwen38-release-320w-qwen3-6-27b-f3cf6d6a985f.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 16 | 197.5 output tok/s |
| 2026-08-12 | [qwen38rw/Qwen3.6-27B/fp8-static_tp4_320W_pass1_c1](../runs/qwen38-release-320w-qwen3-6-27b-25bbfca2c0b8.md) | Qwen3.6-27B | fp8-static | vllm 0.23.0 | TP=4 | 32768 | 1 | 63.42 output tok/s |

Generated from `data/benchmarks.jsonl`. Do not edit by hand.
