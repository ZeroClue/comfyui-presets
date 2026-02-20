#!/usr/bin/env python3
"""
Check URL health for all preset files
"""

import sys
import yaml
import json
import argparse
import asyncio
import aiohttp
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


async def check_url(session: aiohttp.ClientSession, url: str, timeout: int = 10) -> Dict[str, Any]:
    """Check if URL is accessible"""
    result = {
        "url": url,
        "status": "unknown",
        "status_code": None,
        "error": None,
        "response_time_ms": None
    }

    try:
        start = time.time()
        async with session.head(url, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as resp:
            result["status_code"] = resp.status
            result["response_time_ms"] = int((time.time() - start) * 1000)

            if resp.status == 200:
                result["status"] = "ok"
            elif resp.status == 401:
                result["status"] = "auth_required"
            elif resp.status == 403:
                result["status"] = "forbidden"
            elif resp.status == 404:
                result["status"] = "not_found"
            else:
                result["status"] = f"http_{resp.status}"

    except asyncio.TimeoutError:
        result["status"] = "timeout"
        result["error"] = "Request timed out"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


async def check_all_urls(presets_dir: Path, concurrency: int = 5) -> List[Dict[str, Any]]:
    """Check all URLs in all presets"""
    results = []
    semaphore = asyncio.Semaphore(concurrency)

    # Collect all URLs first
    urls_to_check = []
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

            for file_info in preset.get("files", []):
                url = file_info.get("url")
                if url:
                    urls_to_check.append({
                        "preset_id": preset.get("id"),
                        "file_path": file_info.get("path"),
                        "url": url
                    })

    print(f"Checking {len(urls_to_check)} URLs...")

    async with aiohttp.ClientSession() as session:
        async def check_with_semaphore(item):
            async with semaphore:
                result = await check_url(session, item["url"])
                result["preset_id"] = item["preset_id"]
                result["file_path"] = item["file_path"]
                print(f"  {result['status']:15} {item['url'][:60]}...")
                return result

        tasks = [check_with_semaphore(item) for item in urls_to_check]
        results = await asyncio.gather(*tasks)

    return results


def main():
    parser = argparse.ArgumentParser(description="Check URL health")
    parser.add_argument("--presets-dir", type=Path, default=Path("presets"))
    parser.add_argument("--output", type=Path, default=Path("url_check.json"))
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent requests")
    args = parser.parse_args()

    results = asyncio.run(check_all_urls(args.presets_dir, args.concurrency))

    with open(args.output, 'w') as f:
        json.dump({
            "checked_at": datetime.utcnow().isoformat() + "Z",
            "results": results
        }, f, indent=2)

    # Summary
    by_status = {}
    for r in results:
        status = r["status"]
        by_status[status] = by_status.get(status, 0) + 1

    print(f"\nURL Health Summary:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
