# CLAUDE.md

Preset registry for ComfyUI-docker. Contains model definitions, validation, and version scanning.

## Repository Purpose

Centralized preset management for ComfyUI models. Dashboard pods consume `registry.json` without performing local scanning.

## Key Commands

```bash
# Validate all preset YAML files
python scripts/validate.py

# Generate registry.json from presets/
python scripts/generate_registry.py

# Check URL health (requires HF_TOKEN for gated models)
HF_TOKEN=xxx python scripts/check_urls.py

# Scan for HuggingFace version changes
HF_TOKEN=xxx python scripts/scan_versions.py
```

## Directory Structure

- `presets/` - YAML preset files organized by type (image/, video/, audio/)
- `schema.yaml` - JSON Schema for preset validation
- `registry.json` - Pre-computed metadata for fast dashboard loading
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
3. Run `python scripts/generate_registry.py`
4. Commit both preset and updated registry.json
