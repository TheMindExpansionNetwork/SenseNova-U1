# AGENTS.md — Jimsky Fork Context

## Repository role

This is a Jimsky/The Mind Expansion Network workbench fork of OpenSenseNova SenseNova-U1.

- Upstream: https://github.com/OpenSenseNova/SenseNova-U1
- Jimsky fork: https://github.com/TheMindExpansionNetwork/SenseNova-U1
- Local path: /opt/data/workspace/projects/SenseNova-U1

## Rules for agent work

- Preserve upstream attribution and Apache-2.0 license notices.
- Keep upstream-compatible changes small and clearly labeled under Jimsky docs/scripts/modal wrappers.
- Do not commit model weights, Hugging Face caches, generated media batches, `.env`, tokens, API keys, SSH keys, private wallet data, or deployment secrets.
- Use `jimsky/*` branches for custom work and `vendor-sync/*` branches for upstream sync/merge tests.
- Do not reset or rewrite upstream history destructively.
- Real GPU inference/model download is approval-gated; CPU readiness probes and dry-run HTTP shells are safe defaults.

## Modal lane

The safe Modal entrypoint is:

```text
modal/sensenova_u1_modal_app.py
```

Default behavior is CPU-only readiness/dry-run. The GPU probe checks CUDA visibility only and does not download weights or run inference.
