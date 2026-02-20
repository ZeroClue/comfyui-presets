#!/usr/bin/env python3
"""
Scan HuggingFace repos for version updates
"""

import sys
import yaml
import json
import argparse
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class HuggingFaceScanner:
    """Scan HuggingFace repos for updates"""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.api_base = "https://huggingface.co/api"
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def check_for_updates(self, session: aiohttp.ClientSession, repo: str, tracked_revision: Optional[str]) -> Dict[str, Any]:
        """Check if repo has updates since tracked revision"""
        result = {
            "repo": repo,
            "tracked_revision": tracked_revision,
            "latest_revision": None,
            "update_available": False,
            "error": None
        }

        if not tracked_revision:
            result["error"] = "No revision tracked"
            result["update_available"] = True  # Needs to be pinned
            return result

        # For now, use a simple HEAD request to check if URL still works
        # Full implementation would compare commits
        try:
            url = f"https://huggingface.co/{repo}"
            async with session.head(url, headers=self.headers) as resp:
                if resp.status == 200:
                    result["latest_revision"] = "main"  # Placeholder
                    result["update_available"] = False
                else:
                    result["error"] = f"HTTP {resp.status}"
        except Exception as e:
            result["error"] = str(e)

        return result


async def scan_presets(presets_dir: Path, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Scan all presets for HuggingFace updates"""
    scanner = HuggingFaceScanner(token)
    results = []

    async with aiohttp.ClientSession() as session:
        for category_dir in presets_dir.iterdir():
            if not category_dir.is_dir():
                continue

            for preset_dir in category_dir.iterdir():
                if not preset_dir.is_dir():
                    continue

                preset_file = preset_dir / "preset.yaml"
                if not preset_file.exists():
                    continue

                with open(preset_file, 'r') as f:
                    preset = yaml.safe_load(f)

                # Check each file's HuggingFace source
                for file_info in preset.get("files", []):
                    source = file_info.get("source", {})
                    if source.get("type") == "huggingface" and source.get("repo"):
                        print(f"Checking {preset.get('id')}: {source['repo']}")

                        update = await scanner.check_for_updates(
                            session,
                            source["repo"],
                            source.get("revision")
                        )

                        results.append({
                            "preset_id": preset.get("id"),
                            "file_path": file_info.get("path"),
                            **update
                        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Scan for HuggingFace updates")
    parser.add_argument("--presets-dir", type=Path, default=Path("presets"))
    parser.add_argument("--token", type=str, help="HuggingFace API token")
    parser.add_argument("--output", type=Path, default=Path("version_scan.json"))
    args = parser.parse_args()

    results = asyncio.run(scan_presets(args.presets_dir, args.token))

    with open(args.output, 'w') as f:
        json.dump({
            "scanned_at": datetime.utcnow().isoformat() + "Z",
            "results": results
        }, f, indent=2)

    # Summary
    updates_available = sum(1 for r in results if r.get("update_available"))
    errors = sum(1 for r in results if r.get("error"))

    print(f"\nScan complete:")
    print(f"  Total scanned: {len(results)}")
    print(f"  Updates available: {updates_available}")
    print(f"  Errors: {errors}")


if __name__ == "__main__":
    main()
