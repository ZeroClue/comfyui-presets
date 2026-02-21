# Contributing to ComfyUI Presets

Thank you for your interest in contributing to the ComfyUI Presets registry! This guide will help you add new presets, fix issues, and improve the registry.

## Table of Contents

- [Quick Start](#quick-start)
- [Adding a New Preset](#adding-a-new-preset)
- [YAML Schema Reference](#yaml-schema-reference)
- [File Naming Conventions](#file-naming-conventions)
- [Required Fields Checklist](#required-fields-checklist)
- [Testing Your Changes](#testing-your-changes)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b add-my-preset`
3. Add your preset file (see [Adding a New Preset](#adding-a-new-preset))
4. Validate: `python scripts/validate.py`
5. Generate registry: `python scripts/generate_registry.py`
6. Commit and push your changes
7. Open a Pull Request

## Adding a New Preset

### Step 1: Determine the Preset Type

Choose the appropriate category for your model:

| Category | Directory | Type Value |
|----------|-----------|------------|
| Video Generation | `presets/video/` | `video` |
| Image Generation | `presets/image/` | `image` |
| Audio Generation | `presets/audio/` | `audio` |

### Step 2: Create the Preset File

Create a new file at: `presets/{type}/{preset-id}/preset.yaml`

Example structure:
```
presets/
  video/
    my-new-model/
      preset.yaml
  image/
    my-image-model/
      preset.yaml
  audio/
    my-audio-model/
      preset.yaml
```

### Step 3: Write the Preset YAML

Use this template as a starting point:

```yaml
id: my-model-basic
version: 1.0.0
name: My Model Basic
category: Image Generation  # or Video Generation, Audio Generation
type: image  # or video, audio
description: A brief description of what this model does and its capabilities.
download_size: 4.8GB
files:
  - path: checkpoints/model.safetensors
    url: https://huggingface.co/owner/model/resolve/main/model.safetensors
    size: 4.5GB
    optional: false
    source:
      type: huggingface
      repo: owner/model
      revision: null  # or specific commit SHA
  - path: vae/model_vae.safetensors
    url: https://huggingface.co/owner/model/resolve/main/vae.safetensors
    size: 335MB
    optional: false
    source:
      type: huggingface
      repo: owner/model
requirements:
  vram_gb: 12
  disk_gb: 4.8
  recommended_gpu:
    - RTX 4090
    - RTX 3090
    - A100
tags:
  - text-to-image
  - high-quality
  - sdxl-alternative
use_case: High-quality image generation for professional artwork
created: '2026-02-21T00:00:00Z'
updated: '2026-02-21T00:00:00Z'
```

## YAML Schema Reference

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier (lowercase, hyphens) | `flux-dev-basic` |
| `version` | string | Semantic version | `1.0.0` |
| `name` | string | Display name | `FLUX.1-dev` |
| `category` | enum | Model category | `Video Generation` |
| `type` | enum | Model type | `video` |
| `description` | string | Model description (max 500 chars) | `Text-to-image model...` |
| `files` | array | List of model files | See below |

### Required Files Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `path` | string | Relative path from `/workspace/models/` | `checkpoints/model.safetensors` |
| `url` | string | Download URL | `https://huggingface.co/...` |
| `size` | string | File size with unit | `4.8GB`, `335MB` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `download_size` | string | Total download size | `15.5GB` |
| `requirements.vram_gb` | number | Minimum VRAM | `24` |
| `requirements.disk_gb` | number | Required disk space | `15.5` |
| `requirements.recommended_gpu` | array | List of recommended GPUs | `["RTX 4090", "A100"]` |
| `requirements.dependencies` | array | Required dependencies | `["python>=3.10"]` |
| `tags` | array | Categorization tags (max 10) | `["video", "t2v"]` |
| `use_case` | string | Primary use case (max 200 chars) | `Text-to-video generation` |
| `files[].optional` | boolean | Is file optional? | `false` (default) |
| `files[].source.type` | enum | Source type | `huggingface`, `civitai`, `direct` |
| `files[].source.repo` | string | Repository identifier | `owner/model` |
| `files[].source.revision` | string | Git commit SHA | `abc123...` |
| `files[].checksum.algorithm` | enum | Checksum type | `sha256`, `md5` |
| `files[].checksum.value` | string | Checksum value | `abc123...` |

### Category and Type Values

```yaml
# Video Generation
category: Video Generation
type: video

# Image Generation
category: Image Generation
type: image

# Audio Generation
category: Audio Generation
type: audio
```

## File Naming Conventions

### Preset ID Format

- Use lowercase letters, numbers, and hyphens only
- Follow pattern: `{model}-{variant}-{type}`
- Be descriptive but concise

**Examples:**
- `wan-2-2-t2v` - WAN 2.2 text-to-video
- `flux-dev-basic` - FLUX dev basic setup
- `ace-step-v1-3-5b` - Ace Step v1.3 5B parameter

### Directory Structure

```
presets/
  {type}/
    {preset-id}/
      preset.yaml
```

**Examples:**
```
presets/video/wan-2-2-t2v/preset.yaml
presets/image/flux-dev-basic/preset.yaml
presets/audio/ace-step-v1-3-5b/preset.yaml
```

### File Path Format

Model files are relative to `/workspace/models/`:

| Model Type | Path Pattern |
|------------|--------------|
| Checkpoints | `checkpoints/{name}.safetensors` |
| VAE | `vae/{name}.safetensors` |
| Text Encoders | `text_encoders/{name}.safetensors` |
| LoRA | `loras/{name}.safetensors` |
| CLIP Vision | `clip_vision/{name}.safetensors` |
| Upscale Models | `upscale_models/{name}.safetensors` |
| Audio Encoders | `audio_encoders/{name}.safetensors` |

## Required Fields Checklist

Before submitting, verify your preset has:

- [ ] `id` - lowercase, hyphens only
- [ ] `version` - semantic version format (e.g., `1.0.0`)
- [ ] `name` - display name
- [ ] `category` - one of the three categories
- [ ] `type` - matches category
- [ ] `description` - clear description
- [ ] `download_size` - total size
- [ ] `files[]` - at least one file with:
  - [ ] `path` - relative to `/workspace/models/`
  - [ ] `url` - valid download URL
  - [ ] `size` - with unit (GB/MB)
- [ ] `requirements.vram_gb` - minimum VRAM
- [ ] `requirements.disk_gb` - total disk space
- [ ] `tags` - relevant tags
- [ ] `use_case` - primary use case
- [ ] `created` - ISO timestamp
- [ ] `updated` - ISO timestamp

## Testing Your Changes

### Validate Preset Syntax

```bash
# Validate all preset YAML files
python scripts/validate.py
```

### Generate Registry

```bash
# Generate registry.json from presets
python scripts/generate_registry.py
```

### Check URL Health

```bash
# Check if all URLs are accessible
# Requires HF_TOKEN for gated models
HF_TOKEN=your_token python scripts/check_urls.py
```

### Full Validation Workflow

```bash
# 1. Validate syntax
python scripts/validate.py

# 2. Check URLs (optional, requires HF_TOKEN)
HF_TOKEN=your_token python scripts/check_urls.py

# 3. Generate updated registry
python scripts/generate_registry.py

# 4. Verify registry was updated
git diff registry.json
```

## Pull Request Process

### Before Submitting

1. **Fork and Branch**: Create a feature branch from `main`
2. **Validate**: Run `python scripts/validate.py`
3. **Generate**: Run `python scripts/generate_registry.py`
4. **Commit**: Include both preset YAML and updated `registry.json`
5. **Test**: Verify URLs are accessible

### PR Requirements

- [ ] All validation checks pass
- [ ] `registry.json` is updated and included
- [ ] PR description explains the changes
- [ ] For new presets: URLs verified accessible
- [ ] For gated models: HF_TOKEN requirement noted

### Review Process

1. Automated validation runs on your PR
2. Maintainers review the changes
3. Feedback is addressed
4. PR is merged when approved

### Commit Message Format

Use conventional commits:

```
feat: add flux-schnell-basic preset
fix: correct URL for wan-2-2-t2v
docs: update contributing guide
chore: update registry.json
```

## Gated Models

Some HuggingFace models require authentication. For these:

1. Note the requirement in the preset description:
   ```yaml
   description: "Model description. Requires HuggingFace token for gated access."
   ```

2. Include `source` information:
   ```yaml
   source:
     type: huggingface
     repo: owner/gated-model
   ```

3. Users must configure their HF token in dashboard settings before downloading.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and contribute
- Follow GitHub's community guidelines

## Getting Help

- Open an issue for questions
- Check existing presets for examples
- Review the schema at `schema.yaml`

---

Thank you for contributing to the ComfyUI Presets registry!
