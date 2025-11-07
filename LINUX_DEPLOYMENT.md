# Linux Server Deployment Guide

## 🐧 Quick Deploy to Linux Server

Follow these steps to clone and run the cveBuster CCF Push connector on your Linux server.

---

## Step 1: Prerequisites Check

```bash
# Check Python version (need 3.7+)
python3 --version

# Check pip
pip3 --version

# Check git
git --version

# Check internet connectivity to Azure
curl -I https://monitor.azure.com
```

**Expected output:**
- Python 3.7 or higher
- pip3 installed
- git installed
- HTTP 200/301 from Azure endpoint

---

## Step 2: Clone the Repository

```bash
# Navigate to your working directory
cd ~

# Clone the repo
git clone https://github.com/robertmoriarty12/cveBusterCCFPush.git

# Enter the directory
cd cveBusterCCFPush
```

---

## Step 3: Configure Credentials

**IMPORTANT:** You need your Azure credentials from Sentinel.

### Option A: Copy from Windows (if you have connector_config.json)

On your **Windows machine**:
```powershell
# Copy the config file content to clipboard
Get-Content C:\GitHub\cveBusterCCFPush\connector_config.json | Set-Clipboard
```

On your **Linux server**:
```bash
# Create the config file
nano connector_config.json
# Paste the content (Ctrl+Shift+V)
# Save and exit (Ctrl+X, then Y, then Enter)
```

### Option B: Create from scratch

```bash
# Copy the example
cp connector_config.example.json connector_config.json

# Edit with your credentials
nano connector_config.json
```

Your `connector_config.json` should look like:
```json
{
  "tenant_id": "3474cd6c-c085-4003-b28d-665e24dc31a5",
  "application_id": "your-app-id",
  "application_secret": "your-secret",
  "dce_endpoint": "https://asi-0daaa8b2-095d-46cb-b119-6f611a02fcf7-mpaf.centralus-1.ingest.monitor.azure.com",
  "dcr_immutable_id": "dcr-b015c5833e53483e8ccfe3ae725ba6bf",
  "stream_name": "Custom-cveBusterVulnerabilities"
}
```

**Get these values from:**
1. Sentinel → Data Connectors
2. Search "cveBuster Vulnerability Scanner (Push)"
3. Open connector page
4. Copy all displayed values

---

## Step 4: Install Dependencies

```bash
# Install Python packages
pip3 install azure-identity azure-monitor-ingestion

# Or use requirements file
pip3 install -r requirements.txt
```

**Verify installation:**
```bash
python3 -c "import azure.identity, azure.monitor.ingestion; print('✅ Azure SDKs installed')"
```

---

## Step 5: Generate Test Data

```bash
# Generate 500 sample vulnerabilities
python3 generate_data.py
```

**Expected output:**
```
✅ Generated 500 vulnerability records
💾 Saved to: cvebuster_data.json
📊 File size: 125.8 KB
```

---

## Step 6: Test Connection (Optional but Recommended)

```bash
# Run system diagnostics
python3 test_system.py --config connector_config.json
```

This checks:
- ✅ Python version
- ✅ Required packages
- ✅ Config file validity
- ✅ Azure authentication
- ✅ DCE connectivity

---

## Step 7: Push Data to Sentinel

### Quick Start (Recommended)
```bash
# Make script executable
chmod +x run_push.sh

# Run the push
./run_push.sh
```

### Manual Command
```bash
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json \
  --batch-size 25
```

**Expected output:**
```
🔐 Authenticating to Azure...
✅ Authenticated successfully
📊 Loading data from cvebuster_data.json...
✅ Loaded 500 records
📤 Pushing to Azure Monitor...
  ✓ Batch 1/20 (25 records) - Success
  ✓ Batch 2/20 (25 records) - Success
  ...
  ✓ Batch 20/20 (25 records) - Success
✅ Successfully pushed 500 records to Azure Monitor
⏱️  Total time: 15.3 seconds
```

---

## Step 8: Verify in Sentinel

**Wait 5-10 minutes** for Azure to process the data, then:

1. Go to **Microsoft Sentinel**
2. Click **Logs**
3. Run this query:

```kql
cveBusterVulnerabilities_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 10
```

**Expected results:**
- 10 vulnerability records
- All fields populated
- Recent TimeGenerated values

---

## 🔄 Running on Schedule

### Option 1: Cron Job (Hourly)

```bash
# Open crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd ~/cveBusterCCFPush && python3 send_to_azure.py --config connector_config.json --data cvebuster_data.json >> /var/log/cvebuster_push.log 2>&1
```

### Option 2: Systemd Service (Advanced)

Create `/etc/systemd/system/cvebuster-push.service`:
```ini
[Unit]
Description=cveBuster CCF Push Connector
After=network.target

[Service]
Type=oneshot
User=yourusername
WorkingDirectory=/home/yourusername/cveBusterCCFPush
ExecStart=/usr/bin/python3 send_to_azure.py --config connector_config.json --data cvebuster_data.json
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/cvebuster-push.timer`:
```ini
[Unit]
Description=Run cveBuster Push Hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cvebuster-push.timer
sudo systemctl start cvebuster-push.timer

# Check status
sudo systemctl status cvebuster-push.timer
```

---

## 🛠️ Troubleshooting

### Authentication Failed

```bash
# Test Azure CLI login with same credentials
az login --service-principal \
  -u $(jq -r .application_id connector_config.json) \
  -p $(jq -r .application_secret connector_config.json) \
  --tenant $(jq -r .tenant_id connector_config.json)
```

### DCE Connection Issues

```bash
# Test DCE endpoint
curl -I $(jq -r .dce_endpoint connector_config.json)
```

### Schema Validation Errors

Check your data format:
```bash
# View first record
head -n 20 cvebuster_data.json | jq '.[0]'
```

Ensure:
- Datetime fields are ISO 8601 (`2025-01-06T10:30:00Z`)
- CVSS is numeric (not string)
- Booleans are `true`/`false` (not strings)

### Enable Debug Mode

Edit `send_to_azure.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 View Logs

```bash
# Real-time push output
tail -f /var/log/cvebuster_push.log

# Or if using systemd
journalctl -u cvebuster-push.service -f
```

---

## 🔐 Security Best Practices

1. **Protect credentials:**
   ```bash
   chmod 600 connector_config.json
   ```

2. **Don't commit credentials:**
   ```bash
   # Already in .gitignore, but verify:
   cat .gitignore | grep connector_config.json
   ```

3. **Rotate secrets regularly** in Azure Portal

4. **Use managed identities** if running on Azure VM

---

## 📝 Next Steps

1. **Create Analytics Rules** in Sentinel:
   - Detect critical vulnerabilities with active exploits
   - Alert on high-risk assets
   - Track patching progress

2. **Build Workbooks**:
   - Vulnerability trends
   - Asset risk scores
   - Compliance dashboards

3. **Integrate with SOAR**:
   - Automated ticket creation
   - Slack/Teams notifications
   - Patch management workflows

---

## 🆘 Need Help?

- Check logs: `tail -f /var/log/cvebuster_push.log`
- Test connection: `python3 test_system.py --config connector_config.json`
- Verify data: `python3 -c "import json; print(len(json.load(open('cvebuster_data.json'))))"`
- Review Azure Monitor logs in Azure Portal

---

**✅ You're all set!** Your Linux server is now pushing vulnerability data to Microsoft Sentinel.
