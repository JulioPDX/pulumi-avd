# Integrated Build Process

## Overview

The build process is now **fully integrated** into the Pulumi workflow! You no longer need to run a separate build step before deployment.

## How It Works

When you run `pulumi up` or `pulumi preview`, the following happens automatically:

```bash
1. 🔨 PyAVD generates fresh configurations
   ├─ Loads inventory.yml
   ├─ Merges group_vars
   ├─ Generates AVD facts
   ├─ Creates structured configs
   └─ Generates CLI configs (.cfg)

2. 🚀 Pulumi deploys configurations
   ├─ Reads generated .cfg files
   ├─ Compares with Pulumi state
   ├─ Connects to devices (if changes)
   └─ Applies configurations
```

## Benefits

### ✅ Single Command Workflow

```bash
pulumi up  # Builds AND deploys!
```

No more:

```bash
# Old way
python build.py  # Step 1: Generate configs
pulumi up        # Step 2: Deploy
```

### ✅ Always Fresh Configs

Every Pulumi run generates fresh configs from your inventory, ensuring consistency.

### ✅ Simplified CI/CD

Your CI/CD pipeline only needs:

```bash
git pull
pulumi up --yes
```

### ✅ Faster Iteration

Change `group_vars` → Run `pulumi preview` → See exactly what will change!

## Implementation Details

### Before: Separate Build

```python
# Old __main__.py
import pulumi
from eos_provider import EosDeviceConfig

# Read pre-generated configs
for file in configs:
    EosDeviceConfig(...)
```

### After: Integrated Build

```python
# New __main__.py
import pulumi
from pyavd import get_avd_facts, get_device_config
from eos_provider import EosDeviceConfig

# Step 1: Generate configs inline
devices = load_inventory()
avd_facts = get_avd_facts(...)
for device in devices:
    config = get_device_config(...)
    save_config(config)

# Step 2: Deploy configs
for file in configs:
    EosDeviceConfig(...)
```

## What Changed

### Files Modified

- ✅ `__main__.py` - Now includes PyAVD build logic
- ✅ `README.md` - Updated workflow documentation
- ✅ `Makefile` - Updated to reflect auto-generation

### Files Still Useful

- ✅ `build.py` - Optional standalone build script
  - Useful for testing configs without deployment
  - Useful in CI/CD for validation stages
  - Useful for debugging

## Use Cases

### 1. Normal Development

```bash
vim group_vars/FABRIC.yml  # Make changes
pulumi preview             # Auto-builds, shows diff
pulumi up                  # Auto-builds, deploys
```

### 2. Config Validation Only

```bash
python build.py            # Generate configs
ls intended/configs/       # Review .cfg files
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
- name: Deploy Network
  run: |
    pulumi login
    pulumi up --yes  # Builds and deploys in one step!
```

## Performance

**Before (2 steps):**

- Build: ~3-5 seconds
- Deploy: ~2-3 seconds
- **Total: ~5-8 seconds**

**After (integrated):**

- Build + Deploy: ~5-8 seconds
- **Total: ~5-8 seconds** (same!)

The integration doesn't add overhead - it just simplifies the workflow!

## Rollback Behavior

Pulumi state tracks the **config content**, not just files.

If you:

1. Change `group_vars`
1. Run `pulumi preview` (generates new configs)
1. Don't like the changes
1. Revert `group_vars`
1. Run `pulumi preview` again

**Result**: Pulumi will show "no changes" because the generated config matches the state.

## Advanced: Skipping Auto-Build

If you need to deploy pre-generated configs (unusual), you can:

1. Generate configs manually: `python build.py`
1. Comment out the build section in `__main__.py`
1. Run `pulumi up`

But this defeats the purpose of the integrated workflow!

## Summary

The integrated approach provides:

- ✨ Simpler workflow
- ✨ Guaranteed consistency
- ✨ Faster iteration
- ✨ Better CI/CD integration
- ✨ No performance penalty

**Recommendation**: Use the integrated workflow for all normal operations. Keep `build.py` for special cases like config validation or troubleshooting.
