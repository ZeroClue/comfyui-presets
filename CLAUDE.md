# CLAUDE.md

Preset registry for ComfyUI-docker. Contains model definitions, validation, and version scanning.

## Repository Purpose

Centralized preset management for ComfyUI models. Dashboard pods consume `registry.json` without performing local scanning.

## Key Commands

```bash
# Validate all preset YAML files
python scripts/validate.py

# Generate registry.json and model_index.json from presets/
python scripts/generate_registry.py

# Fetch actual file sizes from HuggingFace (HEAD requests, updates YAML + recalculates totals)
python scripts/fetch_sizes.py            # Update in place
python scripts/fetch_sizes.py --dry-run  # Preview changes only

# Check URL health (requires HF_TOKEN for gated models)
HF_TOKEN=xxx python scripts/check_urls.py

# Scan for HuggingFace version changes
HF_TOKEN=xxx python scripts/scan_versions.py
```

## Directory Structure

- `presets/` - YAML preset files organized by type (image/, video/, audio/)
- `schema.yaml` - JSON Schema for preset validation
- `registry.json` - Pre-computed metadata for fast dashboard loading
- `model_index.json` - Maps model file paths to preset IDs (consumed by ComfyUI-docker workflow scanner)
- `scripts/` - Validation, generation, and scanning tools

## Preset Schema

Each preset requires:
- `id`, `version`, `name`, `category`, `type`, `description`
- `files[]` with `path`, `url`, `size`
- `requirements.disk_gb` and optionally `requirements.vram_gb`

See `schema.yaml` for full specification.

## CI Workflows

- `.github/workflows/validate.yml` - Validates on PR/push
- `.github/workflows/scheduled-scan.yml` - Daily URL health check

## Adding Presets

1. Create YAML in `presets/{type}/{preset-id}/preset.yaml`
2. Run `python scripts/validate.py`
3. Run `python scripts/fetch_sizes.py` to get actual file sizes from HF (optional but recommended)
4. Run `python scripts/generate_registry.py` (generates both registry.json and model_index.json)
5. Commit preset, updated registry.json, and model_index.json

Note: `fetch_sizes.py` uses HEAD requests to get Content-Length from HF LFS. It skips files from gated repos that return redirect pages (detected when actual size <1MB but estimate >100MB). Gated repos require `HF_TOKEN` in the dashboard settings, not in this script.

- **Avoid duplicate presets**: When updating an old preset to a new model version, delete the old one if creating a new preset for the updated model. Don't have both coexist.
- **Use `text_encoders/` for preset file paths** (not `clip/`) — matches HF source structure and ComfyUI official workflows. Both directories work in ComfyUI but `text_encoders/` is the convention for presets.
- **YAML numeric tags must be quoted**: Use `'2512'` not `2512` in tags — YAML parses unquoted numbers as integers, but the schema requires strings.
