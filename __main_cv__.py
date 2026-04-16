"""
Pulumi AVD - CloudVision Deployment
Uses cv_workflow from PyAVD to deploy via CloudVision instead of direct device access
"""

import hashlib
import os
import pulumi
import yaml
from pathlib import Path
from cv_provider import CloudVisionDeployment
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
    # Load FABRIC vars (common to all)
    fabric_vars = load_yaml_file(GROUP_VARS_DIR / "FABRIC.yml")

    # Load group-specific vars
    group_file = GROUP_VARS_DIR / f"{group}.yml"
    group_vars = load_yaml_file(group_file) if group_file.exists() else {}

    # Load NETWORK_SERVICES vars (if exists)
    network_services_file = GROUP_VARS_DIR / "NETWORK_SERVICES.yml"
    network_services_vars = (
        load_yaml_file(network_services_file) if network_services_file.exists() else {}
    )

    # Merge: fabric_vars + group_vars + network_services_vars
    merged = {**fabric_vars, **group_vars}

    # Merge network services (tenants, etc.)
    if network_services_vars:
        for key, value in network_services_vars.items():
            if (
                key in merged
                and isinstance(merged[key], list)
                and isinstance(value, list)
            ):
                # Merge lists (like tenants)
                merged[key].extend(value)
            else:
                # Override or add new keys
                merged[key] = value

    merged["inventory_hostname"] = hostname
    return merged


def build_all_inputs(devices):
    """Build all_inputs dict for pyavd"""
    all_inputs = {}
    for hostname, device_info in devices.items():
        inputs = merge_group_vars(hostname, device_info["group"])
        all_inputs[hostname] = inputs
    return all_inputs


def calculate_config_hash():
    """Calculate hash of all generated configs for change detection"""
    hasher = hashlib.sha256()
    for config_file in sorted(CONFIGS_DIR.glob("*.cfg")):
        with open(config_file, "rb") as f:
            hasher.update(f.read())
    return hasher.hexdigest()


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
# Step 2: Deploy Configurations via CloudVision
# ============================================================================

print("☁️  Deploying configurations via CloudVision...")

# CloudVision configuration (use pulumi.Config() for production)
CV_SERVER = os.environ.get("CV_SERVER", "https://www.cv-staging.corp.arista.io")
CV_TOKEN = os.environ.get("CV_TOKEN", "")
WORKSPACE_NAME = "pulumi-avd-workspace"

# Calculate config hash for change detection
config_hash = calculate_config_hash()

# Deploy via CloudVision
cv_deployment = CloudVisionDeployment(
    "avd-cv-deployment",
    cv_server=CV_SERVER,
    cv_token=CV_TOKEN,
    workspace_name=WORKSPACE_NAME,
    inventory_path=str(INVENTORY_FILE),
    config_hash=config_hash,
)

# Export deployment info
pulumi.export("deployment_method", "CloudVision")
pulumi.export("workspace_name", WORKSPACE_NAME)
pulumi.export("config_hash", config_hash)
pulumi.export("devices_count", len(devices))
pulumi.export("devices", list(devices.keys()))
