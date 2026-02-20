#!/usr/bin/env python3
"""
Migrate presets from old monolithic YAML to new structure
"""

import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
import re


def sanitize_id(old_id: str) -> str:
    """Convert old preset ID to new format (lowercase, hyphens)"""
    # Convert SNAKE_CASE to kebab-case
    return old_id.lower().replace('_', '-')


def convert_preset(old_preset: Dict[str, Any], preset_id: str, category: str) -> Dict[str, Any]:
    """Convert old preset format to new format"""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Map category to directory
    category_map = {
        "Video Generation": "video",
        "Image Generation": "image",
        "Audio Generation": "audio"
    }
    category_dir = category_map.get(category, "other")

    new_preset = {
        "id": preset_id,
        "version": "1.0.0",
        "name": old_preset.get("name", preset_id),
        "category": category,
        "type": old_preset.get("type", category_dir),
        "description": old_preset.get("description", ""),
        "download_size": old_preset.get("download_size", "0GB"),
        "files": [],
        "tags": old_preset.get("tags", []),
        "use_case": old_preset.get("use_case", ""),
        "created": now,
        "updated": now
    }

    # Add requirements if we can infer them
    requirements = {}
    if "download_size" in old_preset:
        size_str = old_preset["download_size"]
        if "GB" in size_str:
            # Handle sizes like "~15GB", "14.5GB", "15GB"
            size_num = size_str.replace("GB", "").replace("~", "").strip()
            try:
                requirements["disk_gb"] = float(size_num)
            except ValueError:
                pass  # Skip if can't parse
    if requirements:
        new_preset["requirements"] = requirements

    # Convert files
    for old_file in old_preset.get("files", []):
        new_file = {
            "path": old_file["path"],
            "url": old_file["url"],
            "size": old_file.get("size", "0GB"),
            "optional": old_file.get("optional", False)
        }

        # Detect source type from URL
        if "huggingface.co" in old_file["url"]:
            new_file["source"] = {
                "type": "huggingface",
                "repo": extract_hf_repo(old_file["url"]),
                "revision": None  # Will be filled by version scanner
            }

        new_preset["files"].append(new_file)

    return new_preset


def extract_hf_repo(url: str) -> str:
    """Extract HuggingFace repo from URL"""
    # URL format: https://huggingface.co/{repo}/resolve/main/{file}
    match = re.search(r'huggingface\.co/([^/]+/[^/]+)', url)
    if match:
        return match.group(1)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Migrate presets from old format")
    parser.add_argument("--source", type=Path, required=True, help="Source presets.yaml file")
    parser.add_argument("--output", type=Path, default=Path("presets"), help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"ERROR: Source file not found: {args.source}")
        sys.exit(1)

    with open(args.source, 'r') as f:
        old_config = yaml.safe_load(f)

    presets = old_config.get("presets", {})
    categories = old_config.get("categories", {})

    print(f"Found {len(presets)} presets to migrate")

    # Create output directories
    for category in ["video", "image", "audio"]:
        category_dir = args.output / category
        if not args.dry_run:
            category_dir.mkdir(parents=True, exist_ok=True)

    # Convert each preset
    for old_id, old_preset in presets.items():
        new_id = sanitize_id(old_id)
        category = old_preset.get("category", "Other")

        # Determine category directory
        category_map = {
            "Video Generation": "video",
            "Image Generation": "image",
            "Audio Generation": "audio"
        }
        category_dir = category_map.get(category, "other")

        new_preset = convert_preset(old_preset, new_id, category)

        # Write preset file
        preset_dir = args.output / category_dir / new_id
        preset_file = preset_dir / "preset.yaml"

        print(f"  {old_id} -> {category_dir}/{new_id}")

        if not args.dry_run:
            preset_dir.mkdir(parents=True, exist_ok=True)
            with open(preset_file, 'w') as f:
                yaml.dump(new_preset, f, default_flow_style=False, sort_keys=False)

    print(f"\nMigration {'previewed' if args.dry_run else 'complete'}!")


if __name__ == "__main__":
    main()
