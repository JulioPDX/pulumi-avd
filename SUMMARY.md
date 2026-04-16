# Deployment Methods Summary

## Quick Comparison

### 🔧 Method 1: Direct to Device (pyeapi)

**Best for:** Labs, testing, small networks

```
┌─────────┐     ┌──────────────┐     ┌────────────┐
│ Pulumi  │────▶│ eos_provider │────▶│ EOS Device │
└─────────┘     │   (pyeapi)   │     │   (eAPI)   │
                └──────────────┘     └────────────┘
```

**Pros:**

- ✅ Simple setup
- ✅ Fast deployment
- ✅ No additional infrastructure
- ✅ Perfect for labs

**Cons:**

- ❌ No change control
- ❌ No approval workflow
- ❌ Limited audit trail

**Files:** `__main__.py`, `eos_provider.py`

**Usage:**

```bash
pulumi up
```

______________________________________________________________________

### ☁️ Method 2: CloudVision Workflow (cv_workflow)

**Best for:** Production, enterprises, compliance-driven environments

```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│ Pulumi  │────▶│ cv_provider  │────▶│ CloudVision  │────▶│ EOS Device │
└─────────┘     │(cv_workflow) │     │   Portal     │     │  (agents)  │
                └──────────────┘     └──────────────┘     └────────────┘
```

**Pros:**

- ✅ Enterprise change control
- ✅ Approval workflows
- ✅ Full audit trail
- ✅ Automated rollback
- ✅ Compliance reporting
- ✅ Parallel deployment

**Cons:**

- ❌ Requires CloudVision
- ❌ More complex setup
- ❌ Additional licensing

**Files:** `__main_cv__.py`, `cv_provider.py`

**Usage:**

```bash
export CV_SERVER="https://cv.example.com"
export CV_TOKEN="your-api-token"

# Switch to CV method
mv __main__.py __main_direct__.py
mv __main_cv__.py __main__.py

pulumi up
```

______________________________________________________________________

## Feature Matrix

| Feature                 | Direct (pyeapi) | CloudVision (cv_workflow) |
| ----------------------- | --------------- | ------------------------- |
| Setup Complexity        | Low             | Medium                    |
| Infrastructure Required | None            | CloudVision Portal        |
| Change Control          | ❌              | ✅                        |
| Approval Workflow       | ❌              | ✅                        |
| Audit Trail             | Basic           | Complete                  |
| Rollback                | Manual          | Automated                 |
| Compliance Reporting    | ❌              | ✅                        |
| Multi-device Deploy     | Sequential      | Parallel                  |
| Configuration Diff      | Pulumi only     | CV + Pulumi               |
| Scheduling              | ❌              | ✅                        |
| Validation              | Basic           | Extensive                 |
| Cost                    | Free            | Requires CV license       |

______________________________________________________________________

## When to Use Each Method

### Use Direct (pyeapi) When:

- Working in a lab environment
- Testing configurations
- Small-scale deployments (\<10 devices)
- No compliance requirements
- Fast iteration needed
- No CloudVision available

### Use CloudVision (cv_workflow) When:

- Production environment
- Compliance/audit requirements
- Large-scale deployments (>10 devices)
- Change control mandatory
- Approval workflows needed
- Rollback automation required
- Multiple teams involved
- CloudVision already in use

______________________________________________________________________

## Migration Path

### Start with Direct

```bash
# Initial development
pulumi up  # Uses __main__.py (direct)
```

### Move to CloudVision

```bash
# Production deployment
mv __main__.py __main_direct__.py  # Keep for reference
mv __main_cv__.py __main__.py      # Switch to CV

export CV_SERVER="https://cv.prod.com"
export CV_TOKEN="production-token"

pulumi up  # Now uses CloudVision
```

______________________________________________________________________

## Configuration Examples

### Direct Method Configuration

```python
# In __main__.py
EOS_USER = "admin"
EOS_PASS = "admin"
```

### CloudVision Method Configuration

```bash
# Environment variables
export CV_SERVER="https://www.cv-staging.corp.arista.io"
export CV_TOKEN="your-api-token"
```

Or using Pulumi config:

```bash
pulumi config set cv_server https://cv.example.com
pulumi config set --secret cv_token your-api-token
```

______________________________________________________________________

## Next Steps

1. **Choose your deployment method** based on your environment
1. **Review** [DEPLOYMENT_METHODS.md](DEPLOYMENT_METHODS.md) for detailed guide
1. **Configure** credentials for your chosen method
1. **Test** in lab before production
1. **Deploy** with confidence!

______________________________________________________________________

## Resources

- [DEPLOYMENT_METHODS.md](DEPLOYMENT_METHODS.md) - Full deployment guide
- [PyAVD cv_workflow docs](https://avd.arista.com/docs/pyavd/cv_workflow.html)
- [CloudVision Portal](https://www.arista.com/en/products/eos/eos-cloudvision)
