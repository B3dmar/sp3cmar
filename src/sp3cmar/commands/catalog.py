"""Export the Sp3cMar machine-readable catalog."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from sp3cmar.catalog import build_manifest
from sp3cmar.utils.files import safe_write_text


def run_catalog(output: Path | None, console: Console) -> None:
    """Render the machine-readable catalog as JSON."""

    payload = json.dumps(build_manifest(), indent=2) + "\n"
    if output is None:
        console.file.write(payload)
        console.file.flush()
        return

    safe_write_text(output, payload)
    console.print(f"Wrote catalog to {output}")
