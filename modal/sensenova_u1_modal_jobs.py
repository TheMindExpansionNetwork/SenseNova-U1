from __future__ import annotations

# Deployable no-web wrapper for workspaces that have hit Modal's web endpoint cap.
# It reuses the readiness/gpu probes from sensenova_u1_modal_app.py without
# registering a FastAPI web endpoint.

import json
import pathlib
from typing import Any

import modal

APP_NAME = "jimsky-sensenova-u1-jobs"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
REMOTE_REPO = pathlib.Path("/workspace/SenseNova-U1")

app = modal.App(APP_NAME)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "curl", "ca-certificates")
    .pip_install("huggingface_hub==0.36.2", "requests")
    .add_local_dir(str(REPO_ROOT), remote_path=str(REMOTE_REPO), copy=True)
)
outputs = modal.Volume.from_name("sensenova-u1-outputs", create_if_missing=True)


def _repo_summary() -> dict[str, Any]:
    import tomllib

    pyproject = REMOTE_REPO / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text()) if pyproject.exists() else {}
    project = data.get("project", {})
    return {
        "repo_path": str(REMOTE_REPO),
        "pyproject_exists": pyproject.exists(),
        "readme_exists": (REMOTE_REPO / "README.md").exists(),
        "installation_doc": (REMOTE_REPO / "docs/installation.md").exists(),
        "deployment_doc": (REMOTE_REPO / "docs/deployment.md").exists(),
        "examples_doc": (REMOTE_REPO / "examples/README.md").exists(),
        "project_name": project.get("name"),
        "project_version": project.get("version"),
        "requires_python": project.get("requires-python"),
        "dependencies_head": project.get("dependencies", [])[:8],
    }


@app.function(image=image, cpu=0.25, memory=512, timeout=180, volumes={"/outputs": outputs})
def readiness_probe() -> str:
    import datetime
    import platform
    from huggingface_hub import HfApi

    api = HfApi()
    payload: dict[str, Any] = {
        "ok": True,
        "app": APP_NAME,
        "mode": "modal-jobs-no-web-endpoint",
        "utc": datetime.datetime.utcnow().isoformat() + "Z",
        "python": platform.python_version(),
        "repo": _repo_summary(),
        "hf_models": {},
        "safety": "No model weights downloaded; no GPU used by default.",
    }
    for model_id in ["sensenova/SenseNova-U1-8B-MoT-SFT", "sensenova/SenseNova-U1-8B-MoT"]:
        try:
            info = api.model_info(model_id, files_metadata=False)
            payload["hf_models"][model_id] = {
                "exists": True,
                "private": getattr(info, "private", None),
                "sha": getattr(info, "sha", None),
                "siblings_count": len(getattr(info, "siblings", []) or []),
            }
        except Exception as exc:
            payload["hf_models"][model_id] = {"exists": False, "error": type(exc).__name__, "message": str(exc)[:300]}
    pathlib.Path("/outputs/sensenova-u1-readiness-jobs.json").write_text(json.dumps(payload, indent=2))
    outputs.commit()
    return json.dumps(payload)


@app.function(image=image, gpu="L4", timeout=300, volumes={"/outputs": outputs})
def gpu_dependency_probe() -> str:
    import platform
    import subprocess

    smi = subprocess.check_output(
        "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader",
        shell=True,
        text=True,
        timeout=30,
    ).strip()
    payload = {
        "ok": True,
        "app": APP_NAME,
        "python": platform.python_version(),
        "gpu_probe": smi,
        "note": "No model download/inference was run.",
    }
    pathlib.Path("/outputs/sensenova-u1-gpu-probe-jobs.json").write_text(json.dumps(payload, indent=2))
    outputs.commit()
    return json.dumps(payload)


@app.local_entrypoint()
def main(run_gpu_probe: bool = False):
    print(json.dumps(json.loads(readiness_probe.remote()), indent=2))
    if run_gpu_probe:
        print(json.dumps(json.loads(gpu_dependency_probe.remote()), indent=2))
