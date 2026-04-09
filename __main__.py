import pulumi
import os
import yaml
from pathlib import Path
from eos_provider import EosDeviceConfig
from pyavd import (
    get_avd_facts,
    get_device_structured_config,
    get_device_config,
)

# ============================================================================
# Step 1: Generate AVD Configurations using PyAVD
# ============================================================================

print("🔨 Generating AVD configurations...")

# Define paths
INVENTORY_FILE = Path("inventory.yml")
GROUP_VARS_DIR = Path("group_vars")
OUTPUT_DIR = Path("intended")
CONFIGS_DIR = OUTPUT_DIR / "configs"
STRUCTURED_CONFIGS_DIR = OUTPUT_DIR / "structured_configs"

# Create output directories
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
STRUCTURED_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)


def load_yaml_file(file_path):
    """Load YAML file"""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def load_inventory():
    """Load and parse inventory"""
    inventory = load_yaml_file(INVENTORY_FILE)
    devices = {}
    fabric = inventory["all"]["children"]["FABRIC"]["children"]

    for group_name, group_data in fabric.items():
        if "hosts" in group_data:
            for hostname in group_data["hosts"].keys():
                devices[hostname] = {"group": group_name, "hostname": hostname}

    return devices


def merge_group_vars(hostname, group):
    """Merge group_vars for a device"""
    fabric_vars = load_yaml_file(GROUP_VARS_DIR / "FABRIC.yml")
    group_file = GROUP_VARS_DIR / f"{group}.yml"
    group_vars = load_yaml_file(group_file) if group_file.exists() else {}
    merged = {**fabric_vars, **group_vars}
    merged["inventory_hostname"] = hostname
    return merged


def build_all_inputs(devices):
    """Build all_inputs dict for pyavd"""
    all_inputs = {}
    for hostname, device_info in devices.items():
        inputs = merge_group_vars(hostname, device_info["group"])
        all_inputs[hostname] = inputs
    return all_inputs


# Load inventory and build inputs
devices = load_inventory()
all_inputs = build_all_inputs(devices)

# Generate AVD facts
avd_facts = get_avd_facts(all_inputs)

# Generate configs for each device
for hostname in devices.keys():
    structured_config = get_device_structured_config(
        hostname=hostname, inputs=all_inputs[hostname], avd_facts=avd_facts
    )

    # Generate CLI config
    device_config = get_device_config(structured_config)

    # Write CLI config
    config_file = CONFIGS_DIR / f"{hostname}.cfg"
    with open(config_file, "w") as f:
        f.write(device_config)

    # Write structured config
    structured_file = STRUCTURED_CONFIGS_DIR / f"{hostname}.yml"
    with open(structured_file, "w") as f:
        yaml.dump(
            structured_config._as_dict(), f, default_flow_style=False, sort_keys=False
        )

print(f"✅ Generated configs for {len(devices)} devices")

# ============================================================================
# Step 2: Deploy Configurations with Pulumi
# ============================================================================

print("🚀 Deploying configurations with Pulumi...")

# Switch credentials (in production, use pulumi.Config() to pull these securely from secrets)
EOS_USER = "admin"
EOS_PASS = "admin"

# List to keep track of managed device names for output
managed_devices = []

# Iterate over every AVD generated config file
for filename in os.listdir(CONFIGS_DIR):
    if filename.endswith(".cfg"):
        hostname = filename.replace(".cfg", "")
        managed_devices.append(hostname)

        # Read the configuration AVD generated
        filepath = os.path.join(CONFIGS_DIR, filename)
        with open(filepath, "r") as f:
            intended_config = f.read()

        # Invoke our Custom Pulumi Resource!
        # Pulumi will check if this config text matches what is currently
        # deployed. If not, it will connect via pyeapi and push the diff.
        EosDeviceConfig(
            f"avd-config-{hostname}",
            host=hostname,  # Assuming DNS is resolvable. If not, map to IPs.
            username=EOS_USER,
            password=EOS_PASS,
            config_text=intended_config,
        )

# Export the list of managed switches to the CLI output
pulumi.export("active_switches", managed_devices)
