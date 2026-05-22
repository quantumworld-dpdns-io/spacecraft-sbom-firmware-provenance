from __future__ import annotations

import os

import weave


def setup_weave() -> None:
    project_name = os.getenv("WANDB_PROJECT", "spacecraft-sbom-provenance")
    api_key = os.getenv("WANDB_API_KEY")
    if api_key:
        weave.init(project_name)
