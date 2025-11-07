# 📦 PythonPushConnector - File Overview

## Core Application Files

### `config_gui.py` ⭐ MAIN APPLICATION
**Purpose**: Tkinter-based GUI for configuring and testing CCF Push connector  
**What it does**:
- Provides form fields for 6 Azure configuration values
- Saves configuration to `connector_config.json`
- Calls `generate_data.py` to create test data
- Calls `send_to_azure.py` to push data to Azure
- Shows real-time activity log
- Entry point for end users

**Run**: `python3 config_gui.py`

---

### `send_to_azure.py` 🚀 AZURE INGESTION
**Purpose**: Core data push logic using Azure SDK  
**What it does**:
- Authenticates with Azure using `ClientSecretCredential`
- Creates `LogsIngestionClient` connected to DCE
- Sends data in batches of 25 records
- Handles retries for transient errors (429, 500, 502, 503, 504)
- Returns detailed success/failure statistics

**Run standalone**: 
```bash
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json \
  --batch-size 25
```

---

### `generate_data.py` 📊 TEST DATA
**Purpose**: Creates realistic vulnerability test data  
**What it does**:
- Generates 500 CVE records
- 30% recent (last 2 minutes) - simulates new findings
- 70% old (30-90 days) - simulates historical data
- Outputs to `cvebuster_data.json`
- Mimics real scanner output structure

**Run**: `python3 generate_data.py`

---

## Supporting Files

### `setup.sh` 🔧 INSTALLATION
**Purpose**: Ubuntu setup script  
**What it does**:
- Installs Python 3 and tkinter
- Installs required pip packages
- Makes scripts executable
- Tests imports

**Run**: `./setup.sh`

---

### `test_system.py` 🧪 DIAGNOSTICS
**Purpose**: Verify installation and configuration  
**What it does**:
- Tests Python package imports
- Validates configuration file
- Tests data generation
- Provides diagnostic output

**Run**: `python3 test_system.py`

---

### `demo_mode.py` 🎬 DEMO
**Purpose**: GUI demo without real Azure connection  
**What it does**:
- Pre-fills form with example values
- Simulates data generation and sending
- Safe for testing/demos without credentials

**Run**: `python3 demo_mode.py`

---

## Configuration Files

### `requirements.txt` 📚
Python dependencies:
- `azure-identity==1.15.0` - Authentication
- `azure-monitor-ingestion==1.0.3` - Data ingestion

Install: `pip3 install -r requirements.txt`

---

### `connector_config.json` 🔐 (Auto-created)
**Purpose**: Stores Azure connection settings  
**Created by**: Saving configuration in GUI  
**Contains**:
```json
{
  "tenant_id": "...",
  "application_id": "...",
  "application_secret": "...",
  "dce_endpoint": "...",
  "dcr_immutable_id": "...",
  "stream_name": "..."
}
```
⚠️ **Contains secrets** - listed in `.gitignore`

---

### `connector_config.example.json` 📋
**Purpose**: Template showing config structure  
**Use**: Copy and fill in with your values

---

### `cvebuster_data.json` 📄 (Auto-created)
**Purpose**: Generated test data  
**Created by**: Running `generate_data.py`  
**Contains**: 500 vulnerability records in JSON array

---

## Documentation Files

### `README.md` 📖
Complete documentation:
- Full setup instructions
- Architecture diagrams
- Troubleshooting guide
- Feature list

### `QUICKSTART.md` ⚡
Quick reference:
- 5-minute setup
- Where to find Azure values
- Basic troubleshooting
- Command examples

### `FILES.md` 📑 (This file)
File-by-file breakdown

---

### `.gitignore` 🙈
**Purpose**: Prevent committing sensitive files  
**Excludes**:
- `connector_config.json` (secrets!)
- `cvebuster_data.json` (generated)
- Python cache files
- IDE files

---

## File Dependencies

```
config_gui.py (MAIN)
├── Imports: tkinter, json, subprocess
├── Calls: generate_data.py
├── Calls: send_to_azure.py
├── Reads: connector_config.json
└── Creates: connector_config.json

send_to_azure.py
├── Imports: azure.identity, azure.monitor.ingestion
├── Reads: connector_config.json
├── Reads: cvebuster_data.json
└── Sends to: Azure DCE

generate_data.py
├── Imports: json, random, datetime
└── Creates: cvebuster_data.json

setup.sh
├── Installs: python3, python3-tk
├── Installs: requirements.txt packages
└── Makes executable: *.py files

test_system.py
├── Tests: imports
├── Tests: connector_config.json
└── Tests: generate_data.py
```

---

## Typical Workflow

### First Time Setup:
1. Run `./setup.sh` (install dependencies)
2. Run `python3 config_gui.py` (launch GUI)
3. Fill in Azure configuration
4. Click "💾 Save Configuration"
5. Click "🚀 Manual Send"

### Subsequent Use:
1. Run `python3 config_gui.py`
2. Click "🚀 Manual Send" (config already saved)

### Debugging:
1. Run `python3 test_system.py`
2. Check output for failures
3. Fix issues and retry

### Demo/Testing:
1. Run `python3 demo_mode.py`
2. Test GUI without real Azure

---

## File Sizes (Approximate)

| File | Lines | Size |
|------|-------|------|
| `config_gui.py` | ~280 | 11 KB |
| `send_to_azure.py` | ~160 | 6 KB |
| `generate_data.py` | ~70 | 3 KB |
| `setup.sh` | ~50 | 2 KB |
| `test_system.py` | ~100 | 4 KB |
| `demo_mode.py` | ~90 | 4 KB |
| `README.md` | ~250 | 10 KB |
| `QUICKSTART.md` | ~120 | 5 KB |

**Total**: ~900 lines, ~45 KB

---

## Security Notes

### 🔒 Files with Secrets:
- `connector_config.json` - Contains `application_secret`
- **Never commit to git!** (listed in `.gitignore`)

### 🔐 Safe to Share:
- All `.py` files (no hardcoded secrets)
- All documentation files
- `connector_config.example.json` (template only)

### 🛡️ Best Practices:
- Use environment variables for secrets in production
- Rotate client secrets regularly
- Use Azure Key Vault for production deployments
- Consider managed identity instead of client secrets

---

## Modification Guide

### To Change Test Data:
**Edit**: `generate_data.py`  
**Modify**: 
- Number of records: Change `num_records` parameter
- Field structure: Update the `vuln` dictionary
- Time distribution: Adjust `if random.random() < 0.30` logic

### To Add GUI Features:
**Edit**: `config_gui.py`  
**Add to**: `create_widgets()` method  
**Examples**: 
- New buttons
- Additional form fields
- Custom validation

### To Change Azure Logic:
**Edit**: `send_to_azure.py`  
**Modify**:
- Batch size: Change `batch_size` default
- Retry logic: Update `if e.status_code in [...]` list
- Error handling: Modify exception handlers

---

## Integration Points

### For Production Use:
Replace `generate_data.py` with:
- Real vulnerability scanner output
- Database query results
- API response data
- File system monitoring

### Trigger Methods:
Replace GUI button with:
- Cron job: `0 */5 * * * python3 send_to_azure.py ...`
- Systemd timer: For continuous operation
- Webhook: Flask/FastAPI endpoint that calls send script
- File watcher: Monitor scanner output directory

---

## Questions?

- **GUI won't start**: Check tkinter installation
- **Azure connection fails**: Verify credentials in config
- **No data appearing**: Wait 5-10 min, check Azure logs
- **Script not executable**: Run `chmod +x *.py`

See [README.md](README.md) for full troubleshooting guide.
