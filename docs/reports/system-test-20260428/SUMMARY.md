# SenseNova-U1 Full Bounded System Test — 2026-04-28

## Summary

SenseNova-U1 is now deployed as a Jimsky Modal CPU web shell and backend jobs app. The bounded system test passed for deployment, HTTP health, dry-run API, repo/HF metadata readiness, and GPU dependency visibility.

## Live endpoints

- Web health: `https://m1ndb0t-2045--jimsky-sensenova-u1-api.modal.run/health`
- Web dry-run: `https://m1ndb0t-2045--jimsky-sensenova-u1-api.modal.run/v1/dry-run`
- Modal web app: `jimsky-sensenova-u1`
- Modal jobs app: `jimsky-sensenova-u1-jobs`

## Results

| Test | Result | Notes |
|---|---:|---|
| Modal web deploy | PASS | Web endpoint deployed after freed slots. |
| `/health` | PASS | Repo metadata returned. |
| `/v1/dry-run` | PASS | JSON accepted; GPU-gated message returned. |
| Jobs readiness | PASS | HF model metadata checked; no weights downloaded. |
| GPU dependency probe | PASS | `NVIDIA L4, 23034 MiB, 580.95.05`. |
| Tasks check | PASS with note | Jobs app had `Tasks=0`; web app can hold a CPU task briefly after health checks and now has `scaledown_window=60` patched for redeploy. |
| Billing check | PASS | Only tiny CPU rows were visible for SenseNova; no full inference spend. |

## Capability evaluation

SenseNova-U1 is worth keeping in the MindBotz/Jimsky model hub as a high-potential unified multimodal framework:

- Native multimodal understanding + generation in one architecture.
- T2I, image editing, VQA, interleaved text/image examples.
- LightLLM + LightX2V deployment path for production serving.
- Good candidate for a future “creative/reasoning visual employee” lane.

## Current blockers / gates

- Real inference still needs a heavier CUDA 12.8 / torch 2.8 / transformers 4.57.1 image.
- Model snapshots have 200+ files; cache/download should be an explicit bounded run.
- Public web routes must stay dry-run unless we add private token gating.
- First real test should be VQA, not image generation, to prove model load and tokenizer/model wiring at lower risk.

## Next recommended step

Approval-gated GPU model readiness run:

1. Build a full dependency image matching upstream pins.
2. Cache `sensenova/SenseNova-U1-8B-MoT-SFT` to `huggingface-cache`.
3. Run one tiny VQA smoke test.
4. Verify tasks return to zero and record billing delta.
5. Only then test T2I or image editing.
