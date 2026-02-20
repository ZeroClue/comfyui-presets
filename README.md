# ComfyUI Presets Registry

Centralized preset definitions for ComfyUI models with version pinning and validation.

## Structure

```
comfyui-presets/
├── presets/           # Individual preset YAML files
│   ├── video/         # Video generation models
│   ├── image/         # Image generation models
│   └── audio/         # Audio generation models
├── scripts/           # Management scripts
│   ├── validate.py    # Schema validation
│   ├── migrate.py     # Migration from old format
│   ├── generate_registry.py  # Registry generation
│   ├── scan_versions.py      # HF version scanning
│   └── check_urls.py         # URL health checking
├── schema.yaml        # JSON Schema for preset validation
├── registry.json      # Pre-computed metadata for fast loading
└── .github/           # GitHub Actions workflows
```

## Preset Format

Each preset is a YAML file at `presets/{category}/{preset-id}/preset.yaml`:

```yaml
id: wan-2-2-5-t2v
version: "1.0.0"
name: "WAN 2.2.5 Text-to-Video"
category: Video Generation
type: video
description: "14B parameter text-to-video model"
download_size: "32.5GB"

requirements:
  vram_gb: 24
  disk_gb: 32.5

files:
  - path: checkpoints/model.safetensors
    url: https://huggingface.co/...
    size: "29.5GB"
    source:
      type: huggingface
      repo: Wan-AI/Wan2.5-T2V-14B
      revision: abc123...  # Commit SHA for version pinning
    checksum:
      algorithm: sha256
      value: "..."

tags: [t2v, video, wan]
use_case: "High-quality text-to-video generation"
```

## Usage

### Fetch Registry

```bash
curl -s https://raw.githubusercontent.com/zeroclue/comfyui-presets/main/registry.json
```

### Fetch Specific Preset

```bash
curl -s https://raw.githubusercontent.com/zeroclue/comfyui-presets/main/presets/video/wan-2-2-5-t2v/preset.yaml
```

### Validate Presets

```bash
python scripts/validate.py --all
python scripts/validate.py --preset presets/video/wan-2-2-5-t2v/preset.yaml
```

### Generate Registry

```bash
python scripts/generate_registry.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new presets.

## License

MIT
