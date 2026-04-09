import pulumi
import os
from eos_provider import EosDeviceConfig

# 1. Define where AVD outputs your .cfg files
AVD_CONFIG_DIR = "./intended/configs/"

# 2. Switch credentials (in production, use pulumi.Config() to pull these securely from secrets)
EOS_USER = "admin"
EOS_PASS = "admin"

# List to keep track of managed device names for output
managed_devices = []

# 3. Iterate over every AVD generated config file
if os.path.exists(AVD_CONFIG_DIR):
    for filename in os.listdir(AVD_CONFIG_DIR):
        if filename.endswith(".cfg"):
            # Assuming the filename is the switch hostname (e.g., DC1-LEAF1.cfg)
            hostname = filename.replace(".cfg", "")
            managed_devices.append(hostname)
            
            # Read the configuration AVD generated
            filepath = os.path.join(AVD_CONFIG_DIR, filename)
            with open(filepath, 'r') as f:
                intended_config = f.read()

            # 4. Invoke our Custom Pulumi Resource!
            # Pulumi will check if this config text matches what is currently 
            # deployed. If not, it will connect via pyeapi and push the diff.
            EosDeviceConfig(f"avd-config-{hostname}",
                host=hostname,  # Assuming DNS is resolvable. If not, map to IPs.
                username=EOS_USER,
                password=EOS_PASS,
                config_text=intended_config
            )

# 5. Export the list of managed switches to the CLI output
pulumi.export("active_switches", managed_devices)
