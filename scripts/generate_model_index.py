#!/usr/bin/env python3
"""
Generate model_index.json from preset files.

Maps model file paths (e.g. "diffusion_models/flux1-schnell.safetensors") to preset IDs.
Consumed by ComfyUI-docker's WorkflowScanner to suggest presets for missing models in user workflows.
"""

import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any


def generate_model_index(presets_dir: Path) -> Dict[str, Any]:
    """Generate model_index.json from all presets."""
    mappings: Dict[str, str] = {}

    for category_dir in presets_dir.iterdir():
        if not category_dir.is_dir():
            continue

        for preset_dir in category_dir.iterdir():
            if not preset_dir.is_dir():
                continue

            preset_file = preset_dir / "preset.yaml"
            if not preset_file.exists():
                continue

            with open(preset_file, "r") as f:
                preset = yaml.safe_load(f)

            preset_id = preset.get("id", preset_dir.name)

            for file_entry in preset.get("files", []):
                path = file_entry.get("path", "")
                if path:
                    mappings[path] = preset_id

    return {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mappings": mappings,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate model_index.json")
    parser.add_argument("--presets-dir", type=Path, default=Path("presets"), help="Presets directory")
    parser.add_argument("--output", type=Path, default=Path("model_index.json"), help="Output file")
    args = parser.parse_args()

    if not args.presets_dir.exists():
        print(f"ERROR: Presets directory not found: {args.presets_dir}")
        sys.exit(1)

    index = generate_model_index(args.presets_dir)

    with open(args.output, "w") as f:
        json.dump(index, f, indent=2)

    print(f"Generated model_index.json with {len(index['mappings'])} mappings")


if __name__ == "__main__":
    main()
