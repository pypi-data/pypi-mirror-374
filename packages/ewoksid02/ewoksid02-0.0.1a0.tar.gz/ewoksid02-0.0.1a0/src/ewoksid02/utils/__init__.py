#
from pathlib import Path

from ..resources import TEMPLATE_SAXS

AVAILABLE_TEMPLATES = {
    "saxs": {
        "path": str(TEMPLATE_SAXS),
        "usage": "Loop SAXS integration",
        "directory": Path.home() / "ewoksid02_templates",
        "future_path": Path.home()
        / "ewoksid02_templates"
        / "ewoksid02_template_saxs.yaml",
    },
}


TEMPLATE_MESSAGE = "Available templates:\n"
for key, value in AVAILABLE_TEMPLATES.items():
    TEMPLATE_MESSAGE += (
        f"\t* {key}: {value['usage']}\n\t Copied to: {value['future_path']}\n"
    )
