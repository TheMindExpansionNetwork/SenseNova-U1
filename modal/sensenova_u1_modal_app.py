from __future__ import annotations

import json
import pathlib
import sys
import time
from typing import Any

import modal

APP_NAME = "jimsky-sensenova-u1"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
REMOTE_REPO = pathlib.Path("/workspace/SenseNova-U1")

app = modal.App(APP_NAME)

base_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "curl", "ca-certificates")
    .pip_install("fastapi", "huggingface_hub==0.36.2", "requests")
    .add_local_dir(str(REPO_ROOT), remote_path=str(REMOTE_REPO), copy=True)
)

outputs = modal.Volume.from_name("sensenova-u1-outputs", create_if_missing=True)
model_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)


def _repo_summary() -> dict[str, Any]:
    pyproject = REMOTE_REPO / "pyproject.toml"
    readme = REMOTE_REPO / "README.md"
    docs = ["docs/installation.md", "docs/deployment.md", "examples/README.md"]
    summary: dict[str, Any] = {
        "repo_path": str(REMOTE_REPO),
        "pyproject_exists": pyproject.exists(),
        "readme_exists": readme.exists(),
        "docs_present": {name: (REMOTE_REPO / name).exists() for name in docs},
        "modal_wrapper": "cpu health/probe only by default; no model download and no GPU unless a separate gated function is called",
    }
    if pyproject.exists():
        import tomllib

        data = tomllib.loads(pyproject.read_text())
        project = data.get("project", {})
        summary.update(
            {
                "project_name": project.get("name"),
                "project_version": project.get("version"),
                "requires_python": project.get("requires-python"),
                "dependency_count": len(project.get("dependencies", [])),
                "dependencies_head": project.get("dependencies", [])[:8],
            }
        )
    return summary


@app.function(image=base_image, cpu=0.25, memory=512, timeout=180, volumes={"/outputs": outputs})
def readiness_probe() -> str:
    """Cheap CPU readiness probe. Does not download model weights or start GPU."""
    import datetime
    import os
    import platform
    from huggingface_hub import HfApi

    payload: dict[str, Any] = {
        "ok": True,
        "app": APP_NAME,
        "utc": datetime.datetime.utcnow().isoformat() + "Z",
        "python": platform.python_version(),
        "cwd": str(pathlib.Path.cwd()),
        "repo": _repo_summary(),
        "hf_models": {},
        "notes": [
            "SenseNova-U1 is cloned and mounted into Modal.",
            "This probe intentionally avoids full torch/transformers install and model download.",
            "Real inference likely needs CUDA 12.8, torch 2.8, transformers 4.57.1, and large HF weights.",
        ],
    }
    api = HfApi()
    for model_id in ["sensenova/SenseNova-U1-8B-MoT-SFT", "sensenova/SenseNova-U1-8B-MoT"]:
        try:
            info = api.model_info(model_id, files_metadata=False)
            payload["hf_models"][model_id] = {
                "exists": True,
                "private": getattr(info, "private", None),
                "sha": getattr(info, "sha", None),
                "siblings_count": len(getattr(info, "siblings", []) or []),
            }
        except Exception as exc:  # keep the probe informative rather than failing on transient HF issues
            payload["hf_models"][model_id] = {"exists": False, "error": type(exc).__name__, "message": str(exc)[:300]}

    out = pathlib.Path("/outputs/sensenova-u1-readiness.json")
    out.write_text(json.dumps(payload, indent=2))
    outputs.commit()
    return json.dumps(payload)


@app.function(image=base_image, gpu="L4", timeout=300, volumes={"/outputs": outputs})
def gpu_dependency_probe() -> str:
    """Bounded GPU probe: checks CUDA visibility only. No model download or inference."""
    import subprocess
    import platform

    try:
        smi = subprocess.check_output(
            "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader",
            shell=True,
            text=True,
            timeout=30,
        ).strip()
    except Exception as exc:
        smi = f"ERROR: {type(exc).__name__}: {exc}"
    payload = {
        "ok": True,
        "app": APP_NAME,
        "python": platform.python_version(),
        "gpu_probe": smi,
        "note": "No model download/inference was run.",
    }
    pathlib.Path("/outputs/sensenova-u1-gpu-probe.json").write_text(json.dumps(payload, indent=2))
    outputs.commit()
    return json.dumps(payload)


@app.function(image=base_image, cpu=0.25, memory=512, timeout=180)
@modal.asgi_app()
def api():
    from fastapi import Body, FastAPI

    web = FastAPI(title="Jimsky SenseNova-U1 Modal shell", version="0.1.0")

    @web.get("/health")
    def health():
        return {"ok": True, "app": APP_NAME, "mode": "cpu-shell", "repo": _repo_summary()}

    @web.post("/v1/dry-run")
    def dry_run(req: dict[str, Any] = Body(default_factory=dict)):
        return {
            "ok": True,
            "dry_run": True,
            "received_keys": sorted(req.keys()),
            "message": "SenseNova-U1 Modal shell is wired. Real GPU/model inference is intentionally gated.",
        }

    return web


@app.local_entrypoint()
def main(run_gpu_probe: bool = False):
    print(json.dumps(json.loads(readiness_probe.remote()), indent=2))
    if run_gpu_probe:
        print(json.dumps(json.loads(gpu_dependency_probe.remote()), indent=2))
