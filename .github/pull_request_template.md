## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] New preset added
- [ ] Preset update (URL fix, metadata correction)
- [ ] Bug fix
- [ ] Documentation update
- [ ] Schema/validation improvement

## Preset YAML Validation Checklist

<!-- For preset changes, confirm each item -->

- [ ] **Preset ID**: Lowercase letters, numbers, and hyphens only (e.g., `flux-dev-basic`)
- [ ] **Version**: Semantic versioning format (e.g., `1.0.0`)
- [ ] **Category**: One of `Video Generation`, `Image Generation`, `Audio Generation`
- [ ] **Type**: One of `video`, `image`, `audio`
- [ ] **Files**: All files have `path`, `url`, and `size` fields
- [ ] **File paths**: Relative to `/workspace/models/` (e.g., `checkpoints/model.safetensors`)
- [ ] **File sizes**: Format as `X.XGB` or `XXXmb` (e.g., `4.8GB`, `335MB`)
- [ ] **Requirements**: Both `vram_gb` and `disk_gb` specified
- [ ] **URLs**: All URLs are accessible (not 404)
- [ ] **Gated models**: HF_TOKEN requirement documented in preset description

## File Location

<!-- Confirm the preset file is in the correct location -->

- [ ] File path follows pattern: `presets/{type}/{preset-id}/preset.yaml`
- [ ] Example: `presets/video/wan-2-2-t2v/preset.yaml`

## Testing

<!-- Confirm you have tested the changes -->

- [ ] Ran `python scripts/validate.py` - all validations pass
- [ ] Ran `python scripts/generate_registry.py` - registry updated
- [ ] Verified URLs are accessible (for new presets)
- [ ] Tested preset installation in dashboard (if applicable)

## Validation Commands

```bash
# Validate all presets
python scripts/validate.py

# Generate updated registry
python scripts/generate_registry.py

# Check URL health (requires HF_TOKEN for gated models)
HF_TOKEN=your_token python scripts/check_urls.py
```

## Registry Update

<!-- Confirm registry.json is updated -->

- [ ] `registry.json` has been regenerated and included in this PR

## Screenshots (if applicable)

<!-- Add screenshots for UI-related changes -->

## Additional Notes

<!-- Any additional information reviewers should know -->

---

<!-- Thank you for contributing! -->
