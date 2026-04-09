# Quick Start Guide

## 🚀 One-Command Deployment

```bash
export PULUMI_CONFIG_PASSPHRASE=""
pulumi login --local
pulumi up
```

**That's it!** This single command:

1. ✅ Generates fresh configs from your inventory
1. ✅ Deploys to your network devices
1. ✅ Tracks state for idempotency

______________________________________________________________________

## 📋 Common Commands

### Deploy Everything

```bash
pulumi up           # Auto-builds and deploys
# OR
make deploy
```

### Preview Changes

```bash
pulumi preview      # Auto-builds and shows diff
# OR
make preview
```

### Generate Configs Only

```bash
python build.py     # Standalone config generation
# OR
make build
```

### Validate Inventory

```bash
make validate       # Check YAML syntax
```

### Clean Generated Files

```bash
make clean          # Remove intended/ directory
```

______________________________________________________________________

## 📝 Typical Workflow

```bash
# 1. Make changes to your network design
vim group_vars/FABRIC.yml

# 2. Preview what will change
pulumi preview

# 3. Apply changes
pulumi up
```

______________________________________________________________________

## 🔧 What Gets Generated

Every `pulumi up` or `pulumi preview` creates:

```bash
intended/
├── configs/              # EOS CLI configs
│   ├── spine1.cfg
│   ├── spine2.cfg
│   ├── leaf1.cfg
│   └── leaf2.cfg
└── structured_configs/   # YAML structured configs
    ├── spine1.yml
    ├── spine2.yml
    ├── leaf1.yml
    └── leaf2.yml
```

______________________________________________________________________

## 🎯 Key Points

- ✅ **No separate build step needed** - Configs auto-generate!
- ✅ **Always fresh** - Every run generates new configs
- ✅ **Idempotent** - Running twice doesn't change anything
- ✅ **Fast** - Complete build + deploy in ~5-8 seconds

______________________________________________________________________

## 🆘 Troubleshooting

### "No configs generated"

Check your inventory and group_vars are valid:

```bash
make validate
```

### "Pulumi shows changes every time"

This shouldn't happen with the integrated build. Check:

```bash
pulumi preview  # Run twice - should show "unchanged" on second run
```

### "Want to see generated configs"

```bash
ls -lh intended/configs/
cat intended/configs/spine1.cfg
```

______________________________________________________________________

## 📚 Learn More

- [README.md](README.md) - Full documentation
- [INTEGRATION.md](INTEGRATION.md) - How the integration works
- [COMPARISON.md](COMPARISON.md) - Before/after comparison
- [MIGRATION.md](MIGRATION.md) - Migration from Ansible

______________________________________________________________________

## 🎓 Next Steps

1. Customize your topology in `group_vars/`
1. Run `pulumi preview` to see changes
1. Deploy with `pulumi up`
1. Enjoy automated network management! 🎉
