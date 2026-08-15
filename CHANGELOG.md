# Changelog

## 2026-08-15

- Added the Qwen3.8-27B release campaign: llama.cpp GGUF depth and MTP sweeps
  (Q4_K_M, Q5_K_M, Q6_K on 1, 2 and 4 cards), the 288 point vLLM vs SGLang
  matrix over NVFP4 and FP8 weights, and the long-generation recheck that
  retired one headline cell.
- Added the campaigns that had accumulated locally since the last refresh:
  depth curves, Inkling IQ2_M, llama.cpp split-mode A/B, Qwen3.6-27B at 320 W.
- The archive now holds 1064 measurements from 28 campaigns and 18 model
  families.
- Every Qwen3.8 row was measured at 320 W per card. Do not compare those rows
  with the 220 W ones without filtering `power_limit_w`.

## 2026-07-27

- Published the first normalized snapshot.
- Added 638 measurements from 20 benchmark campaigns.
- Added SQLite, per-run pages, and indexes by model, campaign, and engine.
- Kept exllamav3 labeled as a small experimental slice.
