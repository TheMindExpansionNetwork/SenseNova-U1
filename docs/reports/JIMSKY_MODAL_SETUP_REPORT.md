# SenseNova-U1 Jimsky/Modal Setup Report

Date: 2026-04-28

## What was set up

- Fork/workbench repo: `https://github.com/TheMindExpansionNetwork/SenseNova-U1`
- Upstream remote preserved: `https://github.com/OpenSenseNova/SenseNova-U1`
- Local path: `/opt/data/workspace/projects/SenseNova-U1`
- Added `AGENTS.md` with fork/safety rules.
- Added `docs/JIMSKY_MODAL_SETUP.md` with usage and next-stage inference plan.
- Added `modal/sensenova_u1_modal_app.py` for a CPU FastAPI shell and dry-run route.
- Added `modal/sensenova_u1_modal_jobs.py` for deployable no-web Modal jobs.

## Verification performed

Local syntax checks:

```text
python3 -m py_compile modal/sensenova_u1_modal_app.py modal/sensenova_u1_modal_jobs.py
```

Modal CPU readiness run succeeded:

```text
app: jimsky-sensenova-u1-jobs
mode: modal-jobs-no-web-endpoint
project_name: sensenova-u1
project_version: 0.1.0
requires_python: >=3.11,<3.12
HF model exists: sensenova/SenseNova-U1-8B-MoT-SFT
HF model exists: sensenova/SenseNova-U1-8B-MoT
safety: No model weights downloaded; no GPU used by default.
```

Modal deploy succeeded for the no-web jobs app:

```text
https://modal.com/apps/m1ndb0t-2045/main/deployed/jimsky-sensenova-u1-jobs
```

Modal app state after verification:

```text
jimsky-sensenova-u1-jobs deployed Tasks=0
jimsky-sensenova-u1-jobs stopped Tasks=0
jimsky-sensenova-u1 stopped Tasks=0
```

## Web endpoint note

Deploying the web shell app `jimsky-sensenova-u1` was blocked by Modal workspace endpoint quota:

```text
Deployment failed: reached limit of 8 web endpoints
```

So the working deployed path is currently the no-web jobs app. The FastAPI shell code is present and can be deployed later after retiring an older endpoint.

## Cost/safety

- No full model weights were downloaded.
- No GPU inference was run.
- No image/text generation was run.
- The CPU readiness test cost row observed for `jimsky-sensenova-u1` was approximately `$0.00032113` for today.
- Deployed jobs app is idle with `Tasks=0`.

## Next approval gate

To move from readiness to real SenseNova-U1 inference on Modal, ask for approval to run a bounded GPU setup:

1. Build CUDA 12.8 / torch 2.8 / transformers 4.57.1 image.
2. Mount `huggingface-cache`.
3. Download one model snapshot into the Modal cache volume.
4. Run the smallest VQA smoke test first.
5. Only after VQA works, test text-to-image or editing.

Recommended first model:

```text
sensenova/SenseNova-U1-8B-MoT-SFT
```
