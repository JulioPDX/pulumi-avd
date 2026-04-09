#!/usr/bin/env python3
"""
AVD Build Script using PyAVD
Generates device configurations without Ansible
"""

import yaml
from pathlib import Path
from pyavd import (
    get_avd_facts,
    get_device_structured_config,
    get_device_config,
)

# Define paths
INVENTORY_FILE = Path("inventory.yml")
GROUP_VARS_DIR = Path("group_vars")
OUTPUT_DIR = Path("intended")
CONFIGS_DIR = OUTPUT_DIR / "configs"
STRUCTURED_CONFIGS_DIR = OUTPUT_DIR / "structured_configs"

# Create output directories
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
STRUCTURED_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)


def load_yaml(file_path):
    """Load YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_inventory():
    """Load and parse inventory"""
    inventory = load_yaml(INVENTORY_FILE)
    
    devices = {}
    # Extract hosts from inventory
    fabric = inventory['all']['children']['FABRIC']['children']
    
    for group_name, group_data in fabric.items():
        if 'hosts' in group_data:
            for hostname in group_data['hosts'].keys():
                devices[hostname] = {
                    'group': group_name,
                    'hostname': hostname
                }
    
    return devices


def merge_group_vars(hostname, group):
    """Merge group_vars for a device"""
    # Load FABRIC vars (common to all)
    fabric_vars = load_yaml(GROUP_VARS_DIR / "FABRIC.yml")
    
    # Load group-specific vars
    group_file = GROUP_VARS_DIR / f"{group}.yml"
    group_vars = load_yaml(group_file) if group_file.exists() else {}
    
    # Merge: fabric_vars + group_vars
    merged = {**fabric_vars, **group_vars}
    merged['inventory_hostname'] = hostname
    
    return merged


def build_all_inputs(devices):
    """Build all_inputs dict for pyavd"""
    all_inputs = {}
    
    for hostname, device_info in devices.items():
        inputs = merge_group_vars(hostname, device_info['group'])
        all_inputs[hostname] = inputs
    
    return all_inputs


def main():
    print("🚀 Starting PyAVD build process...")
    
    # Load inventory
    print("📋 Loading inventory...")
    devices = load_inventory()
    print(f"   Found {len(devices)} devices: {', '.join(devices.keys())}")
    
    # Build inputs for all devices
    print("📦 Building device inputs...")
    all_inputs = build_all_inputs(devices)
    
    # Generate AVD facts
    print("🔍 Generating AVD facts...")
    avd_facts = get_avd_facts(all_inputs)
    
    # Generate configs for each device
    print("⚙️  Generating device configurations...")
    for hostname in devices.keys():
        print(f"   - {hostname}")
        
        # Get structured config (returns EOSConfig object in pyavd 6.x)
        structured_config = get_device_structured_config(
            hostname=hostname,
            inputs=all_inputs[hostname],
            avd_facts=avd_facts
        )

        # Generate CLI config (pass the EOSConfig object directly)
        device_config = get_device_config(structured_config)

        # Write structured config as YAML (use _as_dict() method)
        structured_file = STRUCTURED_CONFIGS_DIR / f"{hostname}.yml"
        with open(structured_file, 'w') as f:
            yaml.dump(structured_config._as_dict(), f, default_flow_style=False, sort_keys=False)
        
        # Write CLI config
        config_file = CONFIGS_DIR / f"{hostname}.cfg"
        with open(config_file, 'w') as f:
            f.write(device_config)
    
    print(f"\n✅ Build complete!")
    print(f"   📁 Structured configs: {STRUCTURED_CONFIGS_DIR}")
    print(f"   📁 CLI configs: {CONFIGS_DIR}")


if __name__ == "__main__":
    main()
