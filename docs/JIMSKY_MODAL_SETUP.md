# SenseNova-U1 Jimsky Modal Setup

This fork/workbench is wired for a safe Jimsky/Hermes Modal lane around OpenSenseNova SenseNova-U1.

## Current integration state

- Upstream repo: `https://github.com/OpenSenseNova/SenseNova-U1`
- Jimsky fork remote: `https://github.com/TheMindExpansionNetwork/SenseNova-U1`
- Local path: `/opt/data/workspace/projects/SenseNova-U1`
- Modal CPU/web shell wrapper: `modal/sensenova_u1_modal_app.py`
- Modal no-web jobs wrapper: `modal/sensenova_u1_modal_jobs.py`
- Modal web-shell app name: `jimsky-sensenova-u1`
- Modal jobs app name: `jimsky-sensenova-u1-jobs`
- Output volume: `sensenova-u1-outputs`
- HF cache volume: `huggingface-cache`

## Safety posture

The default Modal path is CPU-only and cheap:

- `/health` checks repo wiring and metadata.
- `/v1/dry-run` validates API plumbing.
- `readiness_probe()` validates repo files and Hugging Face model metadata.

It does **not** download 8B weights, run image generation, or start GPU inference by default.

A bounded `gpu_dependency_probe()` exists for CUDA visibility only. It runs `nvidia-smi` on an L4 and writes a small JSON result. It does not download model weights or perform inference.

Real inference should be approval-gated because SenseNova-U1 expects a CUDA 12.8 / torch 2.8 stack and large HF model weights.

## Run commands

```bash
cd /opt/data/workspace/projects/SenseNova-U1
set -a; source /opt/data/.env; set +a
/opt/data/hermes-agent/venv/bin/modal run modal/sensenova_u1_modal_jobs.py
```

The web shell is also available for dev/serve runs:

```bash
/opt/data/hermes-agent/venv/bin/modal run modal/sensenova_u1_modal_app.py
```

Optional bounded GPU dependency check:

```bash
/opt/data/hermes-agent/venv/bin/modal run modal/sensenova_u1_modal_jobs.py --run-gpu-probe
```

Deploy the no-web jobs app:

```bash
/opt/data/hermes-agent/venv/bin/modal deploy modal/sensenova_u1_modal_jobs.py
```

Deploying the public CPU web shell requires an available Modal web endpoint slot:

```bash
/opt/data/hermes-agent/venv/bin/modal deploy modal/sensenova_u1_modal_app.py
```

If Modal reports the workspace has reached the web endpoint limit, use the no-web jobs app until an old endpoint is retired.

## Next inference lane

1. Build a GPU image matching repo pins:
   - Python 3.11
   - torch 2.8.0 / torchvision 0.23.0 CUDA 12.8
   - transformers 4.57.1
   - tokenizers 0.22.1
   - accelerate 1.10.1
2. Mount `huggingface-cache` so model downloads persist.
3. Add a separate GPU class/function for:
   - VQA smoke test first.
   - Text-to-image after VQA loads.
   - Image editing/interleave after basic generation is stable.
4. Keep public HTTP routes dry-run by default; require an explicit private token/flag for GPU inference.

## Notes from upstream docs

SenseNova-U1 supports:

- text-to-image,
- image editing,
- interleaved text/image generation,
- VQA/visual understanding,
- LightLLM + LightX2V deployment.

The released models listed in README are:

- `sensenova/SenseNova-U1-8B-MoT-SFT`
- `sensenova/SenseNova-U1-8B-MoT`

The upstream deployment doc also describes LightLLM + LightX2V Docker serving, but Modal should start with the simpler Transformers readiness lane before production serving.
