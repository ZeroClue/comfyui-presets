#!/usr/bin/env python3
"""
Fetch actual file sizes from HuggingFace and update preset YAML files.

Usage:
    python3 scripts/fetch_sizes.py [--presets-dir presets] [--dry-run]

Uses HEAD requests to get Content-Length from HF LFS. One request per file.
Updates size, download_size, and disk_gb fields in preset YAML files.
"""

import sys
import yaml
import urllib.request
import urllib.error
import argparse
from pathlib import Path
from collections import defaultdict


def parse_size_to_bytes(size_str: str) -> int:
    """Convert size string like '19GB' to bytes"""
    size_str = size_str.upper().strip()
    if "GB" in size_str:
        return int(float(size_str.replace("GB", "").strip()) * 1024**3)
    elif "MB" in size_str:
        return int(float(size_str.replace("MB", "").strip()) * 1024**2)
    return 0


def format_size(bytes_val: int) -> str:
    """Format bytes to human-readable size string matching preset schema (GB/MB)"""
    if bytes_val >= 1024**3:
        gb = bytes_val / 1024**3
        if gb >= 10:
            return f"{round(gb)}GB"
        if gb >= 1.0:
            return f"{gb:.1f}GB".replace('.0GB', 'GB')
        return f"{round(gb * 10) / 10}GB"
    elif bytes_val >= 1024**2:
        mb = bytes_val / 1024**2
        return f"{round(mb)}MB"
    return f"{bytes_val}B"


def fetch_file_size(url: str) -> int | None:
    """Fetch file size via HEAD request. Returns bytes or None."""
    try:
        req = urllib.request.Request(url, method='HEAD', headers={"User-Agent": "comfyui-presets/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_length = resp.headers.get('Content-Length')
            if content_length:
                return int(content_length)
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code}: {url.split('huggingface.co/')[-1][:60]}")
    except Exception as e:
        print(f"    Error: {url.split('huggingface.co/')[-1][:60]} - {e}")
    return None


class PresetDumper(yaml.SafeDumper):
    """Custom dumper that quotes numeric-looking strings"""
    pass


def _str_representer(dumper, data):
    try:
        int(data)
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
    except (ValueError, TypeError):
        pass
    try:
        float(data)
        if data != data:  # nan check
            raise ValueError
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
    except (ValueError, TypeError):
        pass
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

PresetDumper.add_representer(str, _str_representer)


def fetch_and_update_sizes(presets_dir: Path, dry_run: bool = False) -> int:
    """Fetch actual sizes from HF and update preset YAML files.

    Returns the number of presets updated.
    """
    # Phase 1: Collect all preset files with their file URLs
    # preset_path -> [(file_index, url)]
    preset_files = defaultdict(list)
    total_urls = 0

    for category_dir in sorted(presets_dir.iterdir()):
        if not category_dir.is_dir():
            continue
        for preset_dir in sorted(category_dir.iterdir()):
            if not preset_dir.is_dir():
                continue
            preset_file = preset_dir / "preset.yaml"
            if not preset_file.exists():
                continue
            with open(preset_file, 'r') as f:
                preset = yaml.safe_load(f)
            for i, file_info in enumerate(preset.get('files', [])):
                url = file_info.get('url', '')
                if 'huggingface.co' in url:
                    preset_files[preset_file].append((i, url))
                    total_urls += 1

    print(f"Found {total_urls} files across {len(preset_files)} presets")

    # Phase 2: Fetch sizes via HEAD requests
    url_to_size = {}
    fetched = 0
    for preset_path, entries in sorted(preset_files.items()):
        print(f"Checking {preset_path.parent.parent.name}/{preset_path.parent.name}...")
        for file_index, url in entries:
            if url not in url_to_size:
                size = fetch_file_size(url)
                if size:
                    url_to_size[url] = size
                    fetched += 1
    print(f"Fetched {fetched}/{total_urls} file sizes\n")

    # Phase 3: Update preset files
    updated_count = 0
    for preset_path, entries in sorted(preset_files.items()):
        with open(preset_path, 'r') as f:
            preset = yaml.safe_load(f)

        changed = False
        for file_index, url in entries:
            actual_bytes = url_to_size.get(url)
            if not actual_bytes:
                continue

            old_size = preset['files'][file_index].get('size', '')
            old_bytes = parse_size_to_bytes(old_size)

            # Sanity check: if actual size is <1MB but old was >100MB,
            # this is likely a redirect/login page from a gated repo — skip
            if actual_bytes < 1024**2 and old_bytes > 100 * 1024**2:
                filename = preset['files'][file_index].get('path', '').split('/')[-1]
                print(f"  SKIP {filename}: {old_size} -> {format_size(actual_bytes)} (suspiciously small, likely gated)")
                continue

            new_size = format_size(actual_bytes)
            if old_size != new_size:
                filename = preset['files'][file_index].get('path', '').split('/')[-1]
                print(f"  {filename}: {old_size} -> {new_size}")
                preset['files'][file_index]['size'] = new_size
                changed = True

        if not changed:
            continue

        # Recalculate download_size and disk_gb from all files (including non-HF)
        total_bytes = 0
        for f in preset.get('files', []):
            size_str = f.get('size', '0')
            total_bytes += parse_size_to_bytes(size_str)

        preset['download_size'] = format_size(total_bytes)
        if 'requirements' not in preset:
            preset['requirements'] = {}
        preset['requirements']['disk_gb'] = round(total_bytes / 1024**3, 1)

        if dry_run:
            print(f"  [DRY RUN] {preset.get('id', '?')}: "
                  f"download_size={preset['download_size']}, "
                  f"disk_gb={preset['requirements']['disk_gb']}")
        else:
            with open(preset_path, 'w') as f:
                yaml.dump(preset, f, Dumper=PresetDumper,
                         default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"  Updated {preset.get('id', '?')}")

        updated_count += 1

    return updated_count


def main():
    parser = argparse.ArgumentParser(description="Fetch actual file sizes from HuggingFace")
    parser.add_argument("--presets-dir", type=Path, default=Path("presets"))
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()

    if not args.presets_dir.exists():
        print(f"ERROR: {args.presets_dir} not found")
        sys.exit(1)

    print(f"Scanning presets in {args.presets_dir}...\n")
    updated = fetch_and_update_sizes(args.presets_dir, dry_run=args.dry_run)
    print(f"\n{'Would update' if args.dry_run else 'Updated'} {updated} preset(s)")


if __name__ == "__main__":
    main()
