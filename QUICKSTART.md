# Quick Start Guide - CVE Buster CCF Push Connector

## 🚀 5-Minute Setup on Ubuntu

### Step 1: Run Setup
```bash
cd PythonPushConnector
chmod +x setup.sh
./setup.sh
```

### Step 2: Launch GUI
```bash
python3 config_gui.py
```

### Step 3: Enter Your Azure Details

Get these from Azure Portal:

1. **Tenant ID** 
   - Azure Portal → Azure Active Directory → Overview → Tenant ID

2. **Application ID + Secret**
   - Azure Portal → App Registrations → Your App → Overview
   - Create a new client secret under "Certificates & secrets"

3. **DCE Endpoint**
   - Azure Portal → Monitor → Data Collection Endpoints → Your DCE
   - Copy the "Logs ingestion" endpoint URL

4. **DCR Immutable ID**
   - Azure Portal → Monitor → Data Collection Rules → Your DCR
   - Copy the "Immutable ID" (looks like: dcr-xxxxxxxxxxxx)

5. **Stream Name**
   - From your DCR configuration
   - Format: `Custom-{YourTableName}_CL`
   - Example: `Custom-cveBusterv2_CL`

### Step 4: Save & Test
- Click **"💾 Save Configuration"**
- Click **"🚀 Manual Send"**
- Watch the Activity Log for results!

## 📝 Command-Line Usage (Optional)

### Test Without GUI:
```bash
# Run system test
python3 test_system.py

# Generate data only
python3 generate_data.py

# Send data to Azure
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json
```

## 🔍 Verify Data in Sentinel

After sending data, check in Azure:

```kql
// Query your custom table
cveBusterv2_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 100
```

## ⚠️ Troubleshooting

### GUI won't start
```bash
# Install tkinter
sudo apt install python3-tk

# Verify
python3 -c "import tkinter; print('OK')"
```

### Azure connection fails
```bash
# Test authentication
python3 -c "
from azure.identity import ClientSecretCredential
cred = ClientSecretCredential(
    tenant_id='YOUR_TENANT',
    client_id='YOUR_CLIENT',
    client_secret='YOUR_SECRET'
)
token = cred.get_token('https://monitor.azure.com/.default')
print('✅ Auth successful')
"
```

### Data not appearing in Sentinel
- Wait 5-10 minutes (ingestion delay)
- Check DCR stream name matches exactly
- Verify app has "Monitoring Metrics Publisher" role on DCR
- Check Azure Monitor ingestion logs for errors

## 🎯 What This Does

```
┌─────────────────┐
│   config_gui.py │  ← You interact here
└────────┬────────┘
         │
         ├──► 1. generate_data.py
         │       (Creates 500 test CVE records)
         │
         └──► 2. send_to_azure.py
                  (Authenticates & sends to Azure)
                        │
                        ▼
                  ┌──────────────┐
                  │ Azure Monitor│
                  │ DCE → DCR    │
                  │ → Sentinel   │
                  └──────────────┘
```

## 📚 Next Steps

Once this works, you can:
- Replace `generate_data.py` with your real scanner
- Add automated triggering (instead of manual button)
- Deploy as a systemd service
- Add webhook support for real-time events

## 🆘 Get Help

Common issues:
- **"Module not found"** → Run `pip3 install -r requirements.txt`
- **"Permission denied"** → Run `chmod +x *.py`
- **"Config invalid"** → All 6 fields are required
- **"HTTP 403"** → Check app registration permissions on DCR

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.
