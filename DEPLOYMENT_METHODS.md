# Deployment Methods

This project supports **two deployment methods** for applying AVD-generated configurations to network devices:

1. **Direct to Device (pyeapi)** - Default method, deploys directly to devices
1. **CloudVision Workflow (cv_workflow)** - Enterprise method, deploys via CloudVision Portal

## 🔄 Method Comparison

| Feature               | Direct (pyeapi)        | CloudVision (cv_workflow) |
| --------------------- | ---------------------- | ------------------------- |
| **File**              | `__main__.py`          | `__main_cv__.py`          |
| **Provider**          | `eos_provider.py`      | `cv_provider.py`          |
| **Connection**        | Direct to each device  | Via CloudVision           |
| **Authentication**    | Device credentials     | CV API token              |
| **Change Control**    | No                     | Yes (built-in)            |
| **Rollback**          | Manual                 | Automated                 |
| **Audit Trail**       | Limited                | Full                      |
| **Multi-device**      | Sequential             | Parallel                  |
| **Network Access**    | Requires device access | Requires CV access        |
| **Best For**          | Labs, small networks   | Production, enterprises   |
| **Compliance**        | Manual tracking        | Automated compliance      |
| **Approval Workflow** | No                     | Yes                       |

______________________________________________________________________

## Method 1: Direct to Device (pyeapi)

### Overview

Connects directly to each device via eAPI and applies configuration using config replace.

### Architecture

```
Pulumi → pyeapi → Device eAPI (HTTPS) → EOS Device
```

### Files

- `__main__.py` - Main Pulumi program
- `eos_provider.py` - Dynamic provider for direct deployment

### Configuration

```python
# In __main__.py
EOS_USER = "admin"
EOS_PASS = "admin"
```

### Requirements

- ✅ Devices must be reachable via HTTPS (port 443)
- ✅ eAPI must be enabled on each device
- ✅ Device credentials required
- ✅ Management interface configured

### Pros

- ✅ Simple setup
- ✅ No additional infrastructure needed
- ✅ Fast for small deployments
- ✅ Good for labs and testing

### Cons

- ❌ No built-in change control
- ❌ No approval workflow
- ❌ Limited audit trail
- ❌ Sequential deployment
- ❌ No automatic rollback

### Usage

```bash
# Default - uses __main__.py
pulumi up
```

______________________________________________________________________

## Method 2: CloudVision Workflow (cv_workflow)

### Overview

Uses PyAVD's `cv_workflow` to deploy configurations through CloudVision Portal, providing enterprise-grade change management.

### Architecture

```
Pulumi → cv_workflow → CloudVision → Streaming Agents → EOS Devices
```

### Files

- `__main_cv__.py` - CloudVision-based Pulumi program
- `cv_provider.py` - Dynamic provider for CV deployment

### Configuration

```bash
# Set environment variables
export CV_SERVER="https://www.cv-staging.corp.arista.io"
export CV_TOKEN="your-api-token"
```

Or use Pulumi config:

```bash
pulumi config set cv_server https://your-cv-server.com
pulumi config set --secret cv_token your-api-token
```

### Requirements

- ✅ CloudVision Portal instance
- ✅ CV API token with appropriate permissions
- ✅ Devices onboarded to CloudVision
- ✅ Streaming agents connected

### Pros

- ✅ Enterprise-grade change control
- ✅ Approval workflows
- ✅ Full audit trail
- ✅ Automatic rollback on failure
- ✅ Parallel deployment
- ✅ Compliance reporting
- ✅ Change scheduling
- ✅ Validation before deployment

### Cons

- ❌ Requires CloudVision infrastructure
- ❌ More complex setup
- ❌ Requires CV licensing
- ❌ Additional latency

### Usage

```bash
# Rename __main_cv__.py to __main__.py (or modify Pulumi.yaml)
mv __main__.py __main_direct__.py
mv __main_cv__.py __main__.py

# Deploy via CloudVision
export CV_SERVER="https://your-cv-server.com"
export CV_TOKEN="your-api-token"
pulumi up
```

______________________________________________________________________

## CloudVision Workflow Details

### How cv_workflow Works

The `cv_workflow` from PyAVD provides automated CloudVision integration:

1. **Config Generation** - PyAVD generates structured configs
1. **Configlet Creation** - Creates configlets in CloudVision
1. **Container Assignment** - Assigns configlets to device containers
1. **Change Control** - Creates change control with all devices
1. **Validation** - Validates configs before deployment
1. **Deployment** - Executes change control
1. **Verification** - Confirms successful deployment

### Features

#### Change Control

- Automatic change control creation
- Pre-deployment validation
- Scheduled deployments
- Approval workflows (if configured)

#### Rollback

- Automatic rollback on failure
- Snapshot-based recovery
- Configuration versioning

#### Audit Trail

- Who deployed what and when
- Configuration diffs
- Compliance reporting
- Change history

______________________________________________________________________

## Switching Between Methods

### Option 1: Rename Files

```bash
# Use CloudVision
mv __main__.py __main_direct__.py
mv __main_cv__.py __main__.py

# Switch back to direct
mv __main__.py __main_cv__.py
mv __main_direct__.py __main__.py
```

### Option 2: Modify Pulumi.yaml

```yaml
# In Pulumi.yaml
runtime:
  name: python
  options:
    toolchain: pip
    # Use this for CloudVision
    main: __main_cv__.py
    # Or this for direct
    # main: __main__.py
```

______________________________________________________________________

## Production Recommendations

### For Labs/Development

Use **Direct to Device** (pyeapi):

- Faster iteration
- Simpler setup
- No additional infrastructure

### For Staging/Production

Use **CloudVision Workflow**:

- Change control required
- Compliance tracking needed
- Multiple team members
- Large-scale deployments
- Regulatory requirements

______________________________________________________________________

## Example Workflows

### Lab Environment

```bash
# Direct deployment
python build.py  # Generate configs
pulumi up        # Deploy directly to devices
```

### Production Environment

```bash
# CloudVision deployment
export CV_SERVER="https://cv.production.com"
export CV_TOKEN=$(vault read -field=token secret/cv/token)

# Switch to CV method
ln -sf __main_cv__.py __main__.py

# Deploy via CloudVision
pulumi up

# Review change control in CloudVision UI
# Approve and execute when ready
```

______________________________________________________________________

## Troubleshooting

### Direct Method

**Connection Refused:**

```bash
# Check eAPI is enabled
docker exec <device> Cli -p 15 -c "show management api http-commands"

# Enable if needed
docker exec <device> Cli -p 15 -c "configure
management api http-commands
   no shutdown"
```

### CloudVision Method

**CV Connection Failed:**

```bash
# Verify CV server accessible
curl -k $CV_SERVER/cvpservice/login/authenticate

# Check token validity
# Verify devices are onboarded to CV
```

______________________________________________________________________

## Next Steps

- Choose deployment method based on your environment
- Configure credentials/tokens appropriately
- Test in lab before production
- Consider starting with direct method, migrating to CV for production
