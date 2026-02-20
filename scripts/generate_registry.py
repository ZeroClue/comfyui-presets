#!/usr/bin/env python3
"""
Generate registry.json from preset files
"""

import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List


def parse_size_to_gb(size_str: str) -> float:
    """Convert size string to GB float"""
    size_str = size_str.upper().strip()
    if "GB" in size_str:
        return float(size_str.replace("GB", "").strip())
    elif "MB" in size_str:
        return float(size_str.replace("MB", "").strip()) / 1024
    return 0.0


def generate_registry(presets_dir: Path) -> Dict[str, Any]:
    """Generate registry.json from all presets"""
    registry = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "presets": {},
        "stats": {
            "total": 0,
            "by_category": {}
        }
    }

    for category_dir in presets_dir.iterdir():
        if not category_dir.is_dir():
            continue

        category = category_dir.name
        registry["stats"]["by_category"][category] = 0

        for preset_dir in category_dir.iterdir():
            if not preset_dir.is_dir():
                continue

            preset_file = preset_dir / "preset.yaml"
            if not preset_file.exists():
                continue

            with open(preset_file, 'r') as f:
                preset = yaml.safe_load(f)

            preset_id = preset.get("id", preset_dir.name)

            # Create registry entry (lightweight)
            registry["presets"][preset_id] = {
                "name": preset.get("name", preset_id),
                "category": preset.get("category", category),
                "type": preset.get("type", category),
                "download_size": preset.get("download_size", "0GB"),
                "vram_gb": preset.get("requirements", {}).get("vram_gb", 0),
                "disk_gb": preset.get("requirements", {}).get("disk_gb", 0),
                "tags": preset.get("tags", []),
                "update_available": False,
                "last_verified": preset.get("updated"),
                "file_count": len(preset.get("files", [])),
                "path": f"presets/{category}/{preset_id}/preset.yaml"
            }

            registry["stats"]["total"] += 1
            registry["stats"]["by_category"][category] += 1

    return registry


def main():
    parser = argparse.ArgumentParser(description="Generate registry.json")
    parser.add_argument("--presets-dir", type=Path, default=Path("presets"), help="Presets directory")
    parser.add_argument("--output", type=Path, default=Path("registry.json"), help="Output file")
    args = parser.parse_args()

    if not args.presets_dir.exists():
        print(f"ERROR: Presets directory not found: {args.presets_dir}")
        sys.exit(1)

    registry = generate_registry(args.presets_dir)

    with open(args.output, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"Generated registry.json with {registry['stats']['total']} presets")
    print(f"By category: {registry['stats']['by_category']}")


if __name__ == "__main__":
    main()
