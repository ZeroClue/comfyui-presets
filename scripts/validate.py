#!/usr/bin/env python3
"""
Preset validation script
Validates preset YAML files against schema
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Installing jsonschema...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema"])
    import jsonschema
    from jsonschema import validate, ValidationError


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load JSON Schema from YAML file"""
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def load_preset(preset_path: Path) -> Dict[str, Any]:
    """Load preset YAML file"""
    with open(preset_path, 'r') as f:
        return yaml.safe_load(f)


def validate_preset(preset: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate preset against schema, return list of errors"""
    errors = []

    try:
        jsonschema.validate(instance=preset, schema=schema)
    except ValidationError as e:
        errors.append(f"Schema validation: {e.message}")

    # Additional validations
    if 'files' in preset:
        for i, file in enumerate(preset['files']):
            if 'url' in file and 'huggingface.co' in file['url']:
                if 'source' not in file or 'revision' not in file.get('source', {}):
                    errors.append(f"File {i}: HuggingFace URLs should have revision pinning")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate preset YAML files")
    parser.add_argument("--preset", type=Path, help="Validate specific preset file")
    parser.add_argument("--all", action="store_true", help="Validate all presets")
    parser.add_argument("--schema", type=Path, default=Path("schema.yaml"), help="Schema file path")
    parser.add_argument("--presets-dir", type=Path, default=Path("presets"), help="Presets directory")
    args = parser.parse_args()

    # Load schema
    if not args.schema.exists():
        print(f"ERROR: Schema file not found: {args.schema}")
        sys.exit(1)

    schema = load_schema(args.schema)
    print(f"Loaded schema from {args.schema}")

    errors_found = 0
    presets_validated = 0

    if args.preset:
        # Validate single preset
        if not args.preset.exists():
            print(f"ERROR: Preset file not found: {args.preset}")
            sys.exit(1)

        preset = load_preset(args.preset)
        errors = validate_preset(preset, schema)

        if errors:
            print(f"  {args.preset}:")
            for error in errors:
                print(f"  - {error}")
            errors_found += 1
        else:
            print(f"  {args.preset}: Valid")
            presets_validated += 1

    elif args.all:
        # Validate all presets
        for category_dir in args.presets_dir.iterdir():
            if not category_dir.is_dir():
                continue

            for preset_dir in category_dir.iterdir():
                if not preset_dir.is_dir():
                    continue

                preset_file = preset_dir / "preset.yaml"
                if not preset_file.exists():
                    print(f"   {preset_dir}: No preset.yaml found")
                    continue

                preset = load_preset(preset_file)
                errors = validate_preset(preset, schema)

                if errors:
                    print(f"  {preset_file}:")
                    for error in errors:
                        print(f"  - {error}")
                    errors_found += 1
                else:
                    presets_validated += 1

        print(f"\nValidated {presets_validated} presets, {errors_found} errors")

    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(1 if errors_found else 0)


if __name__ == "__main__":
    main()
