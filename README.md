# ComfyUI Presets Registry

[![Part of ComfyUI-Docker](https://img.shields.io/badge/Part%20of-ComfyUI--Docker-orange)](https://github.com/ZeroClue/ComfyUI-Docker)
[![Presets](https://img.shields.io/badge/Presets-56-blue)](presets/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **Part of [ZeroClue/ComfyUI-Docker](https://github.com/ZeroClue/ComfyUI-Docker)** — A containerized ComfyUI environment with unified dashboard

Centralized preset definitions for ComfyUI models with version pinning, VRAM requirements, and validation.

## Quick Links

- **Parent Project**: [ZeroClue/ComfyUI-Docker](https://github.com/ZeroClue/ComfyUI-Docker)
- **Dashboard Demo**: See the parent repo for screenshots and features
- **Registry JSON**: [registry.json](registry.json) — Pre-computed metadata for fast loading

## Structure

```
comfyui-presets/
├── presets/           # Individual preset YAML files
│   ├── video/         # Video generation models (26 presets)
│   ├── image/         # Image generation models (25 presets)
│   └── audio/         # Audio generation models (5 presets)
├── scripts/           # Management scripts
│   ├── validate.py    # Schema validation
│   ├── generate_registry.py  # Registry generation
│   ├── scan_versions.py      # HF version scanning
│   └── check_urls.py         # URL health checking
├── schema.yaml        # JSON Schema for preset validation
├── registry.json      # Pre-computed metadata for fast loading
└── .github/           # Issue templates & CI workflows
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

## Integration with ComfyUI-Docker

This registry is consumed by the [ComfyUI-Docker](https://github.com/ZeroClue/ComfyUI-Docker) dashboard to provide:

- **Preset Browsing**: Browse and install 56+ model presets
- **GPU Recommendations**: Filter presets by VRAM compatibility
- **Version Tracking**: See when updates are available
- **Checksum Validation**: Verify downloaded files with SHA256

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new presets.

## Related Projects

- **[ComfyUI-Docker](https://github.com/ZeroClue/ComfyUI-Docker)** — Main project with dashboard and Docker setup
- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** — The powerful and modular stable diffusion GUI

## License

MIT
