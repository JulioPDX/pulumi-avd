# Pulumi AVD - Pure Python Network Automation

A complete Python-based network automation solution using Arista AVD (Ansible Validated Designs) and Pulumi for infrastructure as code.

## 🎯 Overview

This project demonstrates how to:
- Generate network device configurations using **PyAVD** (pure Python, no Ansible required)
- Deploy configurations to Arista EOS devices using **Pulumi**
- Manage infrastructure state with idempotent operations

## 🏗️ Architecture

```
┌─────────────────┐
│  Inventory      │
│  (YAML files)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  build.py       │  ← PyAVD generates configs
│  (PyAVD)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  intended/      │  ← Generated EOS configs
│  configs/       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  __main__.py    │  ← Pulumi deployment
│  (Pulumi)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EOS Devices    │  ← Deployed configs
└─────────────────┘
```

## 📁 Project Structure

```
.
├── build.py                  # PyAVD build script (generates configs)
├── __main__.py               # Pulumi main program (deploys configs)
├── eos_provider.py           # Custom Pulumi dynamic provider for EOS
├── inventory.yml             # Device inventory
├── group_vars/               # AVD configuration variables
│   ├── FABRIC.yml           # Fabric-wide settings
│   ├── SPINES.yml           # Spine configuration
│   └── LEAFS.yml            # Leaf configuration
└── intended/                 # Generated outputs
    ├── configs/             # EOS CLI configs (.cfg)
    └── structured_configs/  # Structured YAML configs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install "pyavd[ansible]==6.1.0" pulumi pyeapi pyyaml
```

Or use the Makefile:
```bash
make install
```

### 2. Generate Configurations

```bash
python build.py
# OR
make build
```

This will:
- Load inventory and group_vars
- Generate AVD facts
- Create structured configs in `intended/structured_configs/`
- Create EOS CLI configs in `intended/configs/`

### 3. Deploy with Pulumi

```bash
export PULUMI_CONFIG_PASSPHRASE=""
pulumi up
# OR
make deploy
```

This will:
- Read generated configs from `intended/configs/`
- Connect to devices via pyeapi
- Apply configurations to EOS devices
- Track state for idempotent operations

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

### Development Workflow

1. **Modify inventory/group_vars** - Define your network topology
2. **Run build.py** - Generate configurations
3. **Review configs** - Check `intended/configs/`
4. **Run pulumi preview** - See what will change
5. **Run pulumi up** - Deploy to devices

### Continuous Operations

```bash
# Make changes to group_vars
vim group_vars/FABRIC.yml

# Regenerate configs
python build.py

# Preview changes
pulumi preview

# Deploy
pulumi up
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

### build.py
Pure Python script using PyAVD to generate configurations without Ansible.

### __main__.py
Pulumi program that reads generated configs and deploys them to devices.

### eos_provider.py
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

Apache 2.0
