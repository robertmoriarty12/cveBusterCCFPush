# CVE Buster - Lightweight CCF Push Connector

A simple Python GUI application for testing Microsoft Sentinel CCF Push connectors. This tool allows you to configure Azure connection settings, generate test vulnerability data, and manually push it to Microsoft Sentinel.

## 🎯 Purpose

This lightweight application demonstrates the CCF Push pattern where your application pushes data directly to Microsoft Sentinel via a Data Collection Endpoint (DCE), rather than Sentinel polling your API.

## 📋 Prerequisites

### On Ubuntu:
```bash
# Install Python 3 and tkinter
sudo apt update
sudo apt install python3 python3-pip python3-tk

# Install required Python packages
pip3 install azure-identity azure-monitor-ingestion
```

## 🚀 Quick Start

1. **Launch the GUI**:
   ```bash
   python3 config_gui.py
   ```

2. **Configure Azure Settings**:
   - **Tenant ID**: Your Azure AD Tenant ID
   - **Application ID**: App Registration Client ID
   - **Application Secret**: App Registration Client Secret
   - **DCE Endpoint**: Data Collection Endpoint URL (e.g., `https://xxx.ingest.monitor.azure.com`)
   - **DCR Immutable ID**: Data Collection Rule ID (e.g., `dcr-xxxxxxxxxxxxx`)
   - **Stream Name**: Custom table stream (e.g., `Custom-cveBusterv2_CL`)

3. **Save Configuration**: Click "💾 Save Configuration" to persist settings

4. **Manual Send**: Click "🚀 Manual Send" to:
   - Generate fresh test data (500 vulnerability records)
   - Send data to Azure Monitor in batches of 25

## 📁 Files

| File | Description |
|------|-------------|
| `config_gui.py` | Main GUI application (tkinter-based) |
| `send_to_azure.py` | Azure data ingestion script using Client Secret authentication |
| `generate_data.py` | Test data generator (creates 500 CVE records) |
| `connector_config.json` | Saved configuration (auto-created) |
| `cvebuster_data.json` | Generated test data (auto-created) |

## 🔧 How It Works

### Architecture
```
┌──────────────────────┐
│  config_gui.py       │
│  (GUI Application)   │
└──────────┬───────────┘
           │
           ├──► generate_data.py
           │    (Creates cvebuster_data.json)
           │
           └──► send_to_azure.py
                (Sends data to Azure DCE)
                         │
                         ▼
                ┌─────────────────┐
                │  Azure Monitor  │
                │  DCE → DCR →    │
                │  Log Analytics  │
                └─────────────────┘
```

### Authentication Flow
1. Uses `ClientSecretCredential` (OAuth 2.0)
2. Automatically requests Bearer token from Azure AD
3. Token is cached and auto-refreshed by Azure SDK
4. Sends authenticated POST requests to DCE

## 🎨 GUI Features

- ✅ **Configuration Management**: Save/load Azure connection settings
- ✅ **Data Generation**: Generate 500 test vulnerability records
- ✅ **Manual Push**: One-click data ingestion to Sentinel
- ✅ **Activity Log**: Real-time logging of operations
- ✅ **Error Handling**: Retry logic for transient errors (429, 500, 502, 503, 504)
- ✅ **Batch Processing**: Sends data in batches of 25 records

## 📊 Test Data Distribution

The `generate_data.py` script creates:
- **500 total records**
- **30% recent** - LastModified within last 2 minutes
- **70% old** - LastModified 30-90 days ago

This distribution simulates a real-world scenario where most vulnerabilities are historical, but new ones appear regularly.

## 🔐 Azure Setup Required

Before using this tool, you need:

1. **App Registration** in Azure AD
   - Create a new app registration
   - Create a client secret
   - Note down: Tenant ID, Application (Client) ID, Secret

2. **Data Collection Endpoint (DCE)**
   - Create in Azure Monitor
   - Note down the ingestion endpoint URL

3. **Data Collection Rule (DCR)**
   - Define your custom table schema
   - Link to your DCE
   - Note down the immutable ID

4. **Permissions**
   - Grant your app registration "Monitoring Metrics Publisher" role on the DCR

## 🧪 Testing

### Command-Line Testing (without GUI):
```bash
# Generate test data
python3 generate_data.py

# Send to Azure (manual)
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json \
  --batch-size 25
```

## 🆚 CCF Push vs. CCF Poll

| Aspect | CCF Push (This Tool) | CCF Poll |
|--------|---------------------|----------|
| Direction | You → Sentinel | Sentinel → You |
| Authentication | Client Secret | API Key |
| Trigger | Manual/Event-driven | Scheduled (5 min) |
| Infrastructure | DCE + DCR | Web API Server |
| Best For | Real-time events | Multi-tenant SaaS |

## 🐛 Troubleshooting

### "Authentication failed"
- Verify Tenant ID, Client ID, and Secret are correct
- Ensure the app registration secret hasn't expired
- Check the app has "Monitoring Metrics Publisher" role

### "Failed to send data"
- Verify DCE endpoint URL is correct (should start with `https://`)
- Verify DCR Immutable ID is correct (starts with `dcr-`)
- Check stream name matches your DCR configuration
- Ensure custom table exists in Log Analytics

### "send_to_azure.py not found"
- Ensure all three Python files are in the same directory
- Check file permissions: `chmod +x *.py`

## 📝 Configuration File Format

The `connector_config.json` file stores:
```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "application_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "application_secret": "your-secret-here",
  "dce_endpoint": "https://xxx.ingest.monitor.azure.com",
  "dcr_immutable_id": "dcr-xxxxxxxxxxxxxxxxxxxxx",
  "stream_name": "Custom-cveBusterv2_CL"
}
```

## 🚀 Next Steps

This tool demonstrates the CCF Push pattern. To build a production connector:

1. **Replace test data generator** with real vulnerability scanner
2. **Add real-time triggering** (instead of manual button)
3. **Implement persistent queue** for reliability
4. **Add logging and monitoring** for operations
5. **Consider using managed identity** instead of client secret (for Azure-hosted apps)

## 📚 Related Projects

- **cveBusterCCFPaging-Pull**: Demonstrates CCF Poll pattern with Flask API
- **cveBuster-DataLake**: Simple Python script for data ingestion
- **Banff Protect**: Full .NET Aspire implementation

## 🙏 Credits

Built for learning Microsoft Sentinel CCF connectors.
Based on patterns from Jamf Protect connector and SentinelOne integration.
