# Pulumi AVD - Pure Python Network Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete Python-based network automation solution using Arista AVD (Ansible Validated Designs) and Pulumi for infrastructure as code.

## 🎯 Overview

This project demonstrates how to:

- Generate network device configurations using **PyAVD** (pure Python, no Ansible required)
- Deploy configurations to Arista EOS devices using **Pulumi**
- Manage infrastructure state with idempotent operations

## 🏗️ Architecture

```bash
┌─────────────────┐
│  Inventory      │
│  (YAML files)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  __main__.py    │  ← Integrated: PyAVD + Pulumi
│                 │     1. Generate configs (PyAVD)
│  [PyAVD Build]  │     2. Deploy configs (Pulumi)
│  [Pulumi Deploy]│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EOS Devices    │  ← Deployed configs
└─────────────────┘
```

**Key Feature**: `pulumi up` automatically generates fresh configs before deployment!

## 📁 Project Structure

```bash
.
├── build.py                  # PyAVD build script (generates configs)
├── __main__.py               # Pulumi main program (deploys configs)
├── eos_provider.py           # Custom Pulumi dynamic provider for EOS
├── inventory.yml             # Device inventory
├── group_vars/               # AVD configuration variables
│   ├── FABRIC.yml           # Fabric-wide settings
│   ├── SPINES.yml           # Spine configuration
│   └── LEAFS.yml            # Leaf configuration
├── intended/                 # Generated outputs
│   ├── configs/             # EOS CLI configs (.cfg)
│   └── structured_configs/  # Structured YAML configs
├── Makefile                  # Convenience commands
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install "pyavd[ansible]==6.1.0" pulumi pyeapi
```

Or use the Makefile:

```bash
make install
```

### 2. Deploy Everything with One Command!

```bash
export PULUMI_CONFIG_PASSPHRASE=""
pulumi login --local
pulumi up
# OR
make deploy
```

**That's it!** The `pulumi up` command now:

1. ✅ Automatically generates AVD configs using PyAVD
1. ✅ Deploys configs to EOS devices
1. ✅ Tracks state for idempotent operations

### 3. (Optional) Generate Configs Only

If you want to generate configs without deploying:

```bash
python build.py
# OR
make build
```

### 🎯 Makefile Shortcuts

```bash
make help           # Show all available commands
make validate       # Validate YAML files
make build          # Generate configs
make preview        # Build and preview changes
make deploy         # Build and deploy
make check-configs  # Verify generated configs
make clean          # Remove generated files
```

## 🔧 Configuration

### Topology

The default topology includes:

- **2 Spine switches** (AS 65100)
- **2 Leaf switches** (AS 65001, 65002)
- **eBGP** underlay and overlay
- **VXLAN/EVPN** for overlay networking
- **cEOSLab** platform

### Customization

Edit the YAML files in `group_vars/` to customize:

- BGP AS numbers
- IP addressing
- VXLAN settings
- Management settings
- NTP/DNS configuration

## 📖 Workflow

### Simplified Workflow (Integrated Build)

1. **Modify inventory/group_vars** - Define your network topology
1. **Run `pulumi preview`** - Configs auto-generate, preview changes
1. **Run `pulumi up`** - Configs auto-generate and deploy!

That's it! The build step is integrated into Pulumi.

### Continuous Operations

```bash
# Make changes to group_vars
vim group_vars/FABRIC.yml

# Preview and deploy (auto-generates configs)
export PULUMI_CONFIG_PASSPHRASE=""
pulumi preview  # Auto-builds and shows diff
pulumi up       # Auto-builds and deploys
```

### Manual Build (Optional)

If you want to generate configs without Pulumi:

```bash
python build.py  # Standalone config generation
```

## ✨ Features

### PyAVD (Configuration Generation)

- ✅ Pure Python - No Ansible required
- ✅ Schema validation
- ✅ Structured config generation
- ✅ CLI config generation
- ✅ Fast execution

### Pulumi (Deployment)

- ✅ Idempotent deployments
- ✅ State tracking
- ✅ Diff detection
- ✅ Rollback support
- ✅ Infrastructure as Code

## 🔍 Key Files

### `__main__.py`

**Integrated Pulumi + PyAVD program** that:

1. Generates fresh configs using PyAVD (no Ansible!)
1. Deploys configs to devices using Pulumi
1. Provides a single command workflow: `pulumi up`

### `build.py` (Optional)

Standalone Python script for generating configs without deployment.
Useful for testing or CI/CD pipelines.

### `eos_provider.py`

Custom Pulumi dynamic provider that:

- Connects to EOS devices via pyeapi
- Applies configurations
- Tracks changes for idempotency

## 📚 Resources

- [Arista AVD Documentation](https://avd.arista.com/)
- [PyAVD Documentation](https://avd.arista.com/docs/pyavd/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [pyeapi Documentation](https://pyeapi.readthedocs.io/)

## 🤝 Contributing

This is a reference implementation. Feel free to adapt for your use case!

## 📄 License

MIT
