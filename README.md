# cveBuster CCF Push Connector for Microsoft Sentinel

A **complete, production-ready Microsoft Sentinel CCF (Codeless Connector Framework) Push connector** that enables vulnerability scanners to push data directly to Azure Sentinel. This project demonstrates the CCF Push pattern with a full implementation including connector definition files, ARM templates, and a Python client.

---

## 🎯 What is This Project?

This repository contains a **complete CCF Push solution** consisting of:

1. **CCF Connector Definition Files** - JSON configurations that define the Sentinel data connector
2. **ARM Deployment Templates** - Packaged solution for deploying to Microsoft Sentinel
3. **Python Push Client** - Reference implementation for pushing vulnerability data to Azure
4. **Documentation** - Complete guides for deployment and usage

### CCF Push vs. CCF Pull (Polling)

| Aspect | CCF Push (This Project) | CCF Pull |
|--------|------------------------|----------|
| **Data Flow** | Your app pushes to Azure | Sentinel polls your API |
| **Authentication** | Service Principal (OAuth 2.0) | API Key in headers |
| **Trigger** | Event-driven (real-time) | Scheduled (every 5 min) |
| **Infrastructure** | DCE + DCR + Service Principal | Web API + Pagination |
| **Best For** | Real-time events, internal tools | Multi-tenant SaaS, public APIs |
| **Latency** | Immediate (< 1 second) | Up to 5 minutes delay |
| **Complexity** | Moderate (Azure components) | Higher (API implementation) |

**This project uses CCF Push** because vulnerability data benefits from real-time ingestion and doesn't require exposing a public API.

---

## 📦 Repository Structure

```
cveBusterCCFPush/
├── README.md                              # This file
├── SolutionMetadata.json                  # Solution publisher metadata
│
├── Data Connectors/                       # CCF Connector Definition
│   └── cveBusterPush_ccp/
│       ├── connectorDefinition.json       # UI definition for Sentinel gallery
│       ├── dataConnector.json             # Core Push connector config
│       ├── DCR.json                       # Data Collection Rule with KQL transform
│       └── table.json                     # Log Analytics table schema
│
├── Package/                               # Deployment Templates
│   ├── mainTemplate.json                  # ARM template (818 lines)
│   ├── createUiDefinition.json            # Azure Portal deployment UI
│   ├── testParameters.json                # Test deployment parameters
│   └── 3.0.0.zip                         # Complete solution package
│
└── PythonConnector/                       # Python Push Client
    ├── send_to_azure.py                   # Main data push client
    ├── generate_data.py                   # Test data generator
    ├── config_gui.py                      # GUI configuration tool
    ├── demo_mode.py                       # Demo data generator
    ├── test_system.py                     # System diagnostics
    ├── requirements.txt                   # Python dependencies
    ├── connector_config.example.json      # Config template
    ├── run_push.sh                        # Quick start script
    └── setup.sh                           # Environment setup
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Microsoft Sentinel                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Data Connectors Gallery                                   │ │
│  │  • cveBuster Vulnerability Scanner (Push)                  │ │
│  │  • Deploy Button → Creates Azure Resources                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ User clicks "Deploy"
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ARM Template Deployment                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Service Principal│  │ Data Collection  │  │ Data         │ │
│  │ (App Registration)│  │ Endpoint (DCE)  │  │ Collection   │ │
│  │ + Client Secret  │  │                  │  │ Rule (DCR)   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Custom Log Analytics Table                                │ │
│  │ cveBusterVulnerabilities_CL                              │ │
│  │ (12 columns: VulnId, Severity, CVSS, MachineName, etc.) │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Deployment outputs credentials
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Your Python Application (Linux/Windows)            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  send_to_azure.py                                         │ │
│  │  1. Authenticate with Service Principal (OAuth 2.0)      │ │
│  │  2. Load vulnerability data (JSON)                       │ │
│  │  3. POST to DCE endpoint in batches                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS POST with Bearer token
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Azure Monitor Ingestion API                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Data Collection Endpoint (DCE)                           │ │
│  │  • Receives JSON payload                                  │ │
│  │  • Validates authentication                               │ │
│  │  • Routes to DCR                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Data Collection Rule (DCR)                               │ │
│  │  • Applies KQL transformation: source | extend TimeGenerated = now() │
│  │  • Validates schema against table definition             │ │
│  │  • Ingests to Log Analytics                              │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 5-10 minute indexing
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           Log Analytics Workspace                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  cveBusterVulnerabilities_CL                             │ │
│  │  • Query with KQL                                         │ │
│  │  • Create analytics rules                                 │ │
│  │  • Build workbooks                                        │ │
│  │  • Trigger alerts and automation                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 CCF Connector Components Explained

### 1. **connectorDefinition.json**
Defines how the connector appears in Sentinel's Data Connectors gallery.

**Key Features:**
- **Publisher Information** - Microsoft logo, links, support info
- **Instruction Steps** - Markdown guide shown to users
- **Deployment Button** - DeployPushConnectorButton creates Azure resources
- **Configuration Fields** - CopyableLabel elements display credentials after deployment

**What it does:** Creates the visual UI in Sentinel's data connectors page.

### 2. **dataConnector.json**
Core connector configuration defining behavior.

**Key Settings:**
- **kind**: "Push" - Declares this is a CCF Push connector
- **dataTypes**: Specifies the custom table name
- **connectivityCriteria**: Defines connection status logic
- **auth**: Authentication type ("Push" for Service Principal)

**What it does:** Tells Sentinel this is a Push connector that writes to a specific table.

### 3. **DCR.json**
Data Collection Rule defining data transformation and routing.

**Key Components:**
- **streams**: Declares Custom-cveBusterVulnerabilities stream
- **columns**: Schema definition (12 fields)
- **transformKql**: source | extend TimeGenerated = now()
  - Adds ingestion timestamp to each record
  - Must output columns matching table schema exactly

**What it does:** Transforms incoming JSON data and validates against schema before ingestion.

**Important:** The KQL transform must output column names that **exactly match** the table schema. Mismatches cause deployment errors.

### 4. **table.json**
Log Analytics custom table schema definition.

**Schema (12 columns):**
- TimeGenerated (datetime) - Ingestion timestamp
- VulnId (string) - CVE identifier
- VulnTitle (string) - Vulnerability description
- Severity (string) - Critical/High/Medium/Low
- CVSS (real) - CVSS score 0.0-10.0
- MachineName (string) - Asset hostname
- AssetCriticality (string) - Asset importance
- PatchAvailable (boolean) - Patch availability
- ExploitAvailable (boolean) - Public exploit exists
- DiscoveryDate (datetime) - First detection
- LastModified (datetime) - Last update
- Status (string) - Open/In Progress/Patched

**What it does:** Defines the structure of the cveBusterVulnerabilities_CL table in Log Analytics.

---

## 🚀 Part 1: Deploy the CCF Connector to Sentinel

### Prerequisites
- Microsoft Sentinel workspace deployed
- Azure subscription with Contributor/Owner access
- Resource group for deployment

### Deployment Steps

#### Option A: Deploy from Content Hub (Recommended)

1. **Navigate to Sentinel**
   - Go to your Sentinel workspace
   - Click **Content Hub**

2. **Upload Solution Package**
   - Click **Import**
   - Upload Package/3.0.0.zip from this repo
   - Click **Install**

3. **Configure Deployment**
   - Select your workspace
   - Choose resource group
   - Click **Review + create**

4. **Retrieve Credentials**
   - After deployment, go to **Data Connectors**
   - Search for "cveBuster Vulnerability Scanner (Push)"
   - Open connector page
   - Copy all displayed values:
     - Tenant ID
     - Application (Client) ID
     - Application Secret
     - DCE Endpoint
     - DCR Immutable ID
     - Stream Name

#### Option B: Manual ARM Deployment

1. **Deploy ARM Template**
   ```bash
   az deployment group create \
     --resource-group <your-rg> \
     --template-file Package/mainTemplate.json \
     --parameters workspace=<sentinel-workspace-name>
   ```

2. **Capture Deployment Outputs**
   - The deployment outputs all required credentials
   - Save these for Python client configuration

### What Gets Created?

The deployment creates:
- ✅ **Service Principal** (App Registration) with client secret
- ✅ **Data Collection Endpoint (DCE)** with ingestion endpoint
- ✅ **Data Collection Rule (DCR)** with stream and transformation
- ✅ **Custom Log Analytics Table** (cveBusterVulnerabilities_CL)
- ✅ **Role Assignment** (Monitoring Metrics Publisher on DCR)

---

## 🐍 Part 2: Setup the Python Push Client

### Prerequisites
- Python 3.7+ installed
- pip3 package manager
- Credentials from connector deployment (Part 1)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/robertmoriarty12/cveBusterCCFPush.git
cd cveBusterCCFPush/PythonConnector
```

#### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

**Installs:**
- zure-identity==1.15.0 - Azure authentication
- zure-monitor-ingestion==1.0.3 - Data ingestion client

#### 3. Configure Credentials

Create connector_config.json with your deployment credentials:

```bash
cat > connector_config.json << 'EOF'
{
  "tenant_id": "your-tenant-id",
  "application_id": "your-app-id",
  "application_secret": "your-app-secret",
  "dce_endpoint": "https://your-dce.ingest.monitor.azure.com",
  "dcr_immutable_id": "dcr-your-dcr-id",
  "stream_name": "Custom-cveBusterVulnerabilities"
}
EOF
```

**Replace the values** with credentials from your Sentinel connector deployment.

#### 4. Generate Test Data

```bash
python3 generate_data.py
```

**Output:** Creates cvebuster_data.json with 500 sample vulnerability records.

#### 5. Push Data to Sentinel

```bash
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json \
  --batch-size 25
```

**Expected Output:**
```
============================================================
CVE Buster - Azure Data Ingestion
============================================================

📋 Configuration:
   Tenant ID: 3474cd6c-c085-4003-b28d-665e24dc31a5
   Client ID: 344d9215-e518-4346-b684-668fc55a773d
   ...

🔐 Authenticating with Azure...
🔗 Creating Azure Monitor Ingestion Client...
📤 Sending data in batches of 25...

Batch 1: Sending 25 records... ✅ Success
Batch 2: Sending 25 records... ✅ Success
...
Batch 20: Sending 25 records... ✅ Success

============================================================
📊 Summary:
   Total Records: 500
   Successfully Sent: 500
   Failed: 0
   Success Rate: 100.0%
============================================================

✅ All data sent successfully!
```

---

## 🔍 Part 3: Query Data in Sentinel

### Wait for Indexing
Data takes **5-10 minutes** to appear after ingestion.

### Basic Query

```kql
cveBusterVulnerabilities_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 10
```

### Check Data Distribution

```kql
cveBusterVulnerabilities_CL
| summarize Count=count() by Severity
| render piechart
```

### Find Critical Vulnerabilities with Exploits

```kql
cveBusterVulnerabilities_CL
| where Severity == "Critical" and ExploitAvailable == true
| project TimeGenerated, MachineName, VulnId, CVSS, Status
| order by CVSS desc
```

### Vulnerability Trend Over Time

```kql
cveBusterVulnerabilities_CL
| summarize Count=count() by bin(TimeGenerated, 1h), Severity
| render timechart
```

### Top 10 Vulnerable Assets

```kql
cveBusterVulnerabilities_CL
| where Status == "Open"
| summarize VulnCount=count() by MachineName
| order by VulnCount desc
| take 10
```

### Patching Progress Dashboard

```kql
cveBusterVulnerabilities_CL
| summarize 
    Open=countif(Status == "Open"),
    InProgress=countif(Status == "In Progress"),
    Patched=countif(Status == "Patched")
| extend PatchRate = round(Patched * 100.0 / (Open + InProgress + Patched), 2)
```

---

## 🔧 Python Client Components

### send_to_azure.py
**Main data push client** using Azure Monitor Ingestion API.

**Features:**
- OAuth 2.0 authentication with Service Principal
- Batch processing (configurable size)
- Automatic retry logic (429, 500, 502, 503, 504)
- Progress tracking and error reporting
- Supports command-line arguments

**Usage:**
```bash
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json \
  --batch-size 25
```

### generate_data.py
**Test data generator** creating realistic vulnerability records.

**Features:**
- Generates 500 CVE records
- Realistic severity distribution (30% Critical, 25% High, 25% Medium, 20% Low)
- CVSS scores matching severity levels
- Random asset names and criticality
- Mix of patched/unpatched vulnerabilities
- Exploit availability flags

**Usage:**
```bash
python3 generate_data.py
```

**Output:** cvebuster_data.json (500 records)

### config_gui.py
**GUI configuration tool** for interactive setup (requires tkinter).

**Features:**
- Visual configuration editor
- Save/load configuration
- Manual data generation button
- One-click push to Azure
- Activity log viewer

**Usage:**
```bash
python3 config_gui.py
```

### test_system.py
**System diagnostics tool** for troubleshooting.

**Checks:**
- Python version
- Required packages installed
- Config file validity
- Azure authentication
- DCE connectivity

**Usage:**
```bash
python3 test_system.py --config connector_config.json
```

### demo_mode.py
**Demo data generator** with time-based distribution.

**Features:**
- 30% recent records (last 2 minutes)
- 70% historical records (30-90 days old)
- Simulates real-world vulnerability age distribution

**Usage:**
```bash
python3 demo_mode.py
```

---

## 🔄 Automated Scheduling

### Cron Job (Linux)

Run every hour:
```bash
crontab -e
```

Add:
```
0 * * * * cd ~/cveBusterCCFPush/PythonConnector && python3 send_to_azure.py --config connector_config.json --data cvebuster_data.json >> /var/log/cvebuster_push.log 2>&1
```

### Systemd Service (Linux)

Create /etc/systemd/system/cvebuster-push.service:
```ini
[Unit]
Description=cveBuster CCF Push Connector
After=network.target

[Service]
Type=oneshot
User=azureuser
WorkingDirectory=/home/azureuser/cveBusterCCFPush/PythonConnector
ExecStart=/usr/bin/python3 send_to_azure.py --config connector_config.json --data cvebuster_data.json

[Install]
WantedBy=multi-user.target
```

Create /etc/systemd/system/cvebuster-push.timer:
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
```

---

## 🛠️ Troubleshooting

### Authentication Errors

**Error:** Application with identifier 'xxx' was not found
- **Solution:** Verify Application ID is correct from deployment output

**Error:** Invalid client secret provided
- **Solution:** Ensure secret is complete (Azure secrets contain special chars like ~)
- Secret must be the **Value**, not the **Secret ID**

**Error:** Authentication failed: AADSTS7000215
- **Solution:** Client secret expired - create new secret in App Registration

### Connection Issues

**Error:** Failed to connect to DCE endpoint
- **Solution:** Verify DCE endpoint URL is correct (starts with https://)
- Check network connectivity: curl -I <dce_endpoint>

**Error:** DCR not found
- **Solution:** Verify DCR Immutable ID is correct (starts with dcr-)

### Schema Validation Errors

**Error:** Invalid transform output columns do not match the ones defined by the output stream
- **Solution:** DCR transform must output column names matching table schema exactly
- Check DCR.json 	ransformKql field

**Error:** Invalid data type for column
- **Solution:** Ensure data types match:
  - Datetime: ISO 8601 format (2025-11-06T10:30:00Z)
  - CVSS: Numeric (float), not string
  - Booleans: 	rue/alse, not strings

### No Data in Sentinel

**Wait 5-10 minutes** - Azure indexing has latency

**Check ingestion:**
```kql
cveBusterVulnerabilities_CL
| where TimeGenerated > ago(24h)
| summarize count()
```

**If still no data:**
- Verify deployment succeeded (check Azure Portal)
- Check table exists: Log Analytics workspace → Tables
- Review DCR logs in Azure Monitor

---

## 🔐 Security Best Practices

### Protect Credentials

1. **Never commit connector_config.json** to git
   - Already in .gitignore
   - Double-check before pushing

2. **Restrict file permissions:**
   ```bash
   chmod 600 connector_config.json
   ```

3. **Rotate secrets regularly** (every 90 days recommended)

4. **Use Azure Key Vault** for production:
   ```python
   from azure.identity import DefaultAzureCredential
   from azure.keyvault.secrets import SecretClient
   
   credential = DefaultAzureCredential()
   vault_url = "https://your-vault.vault.azure.net"
   client = SecretClient(vault_url=vault_url, credential=credential)
   
   secret = client.get_secret("cvebuster-client-secret")
   application_secret = secret.value
   ```

5. **Use Managed Identity** for Azure VMs:
   - Eliminates need for secrets in config
   - Automatically managed by Azure
   - Preferred for production deployments

---

## 📚 Additional Resources

### Microsoft Documentation
- [Data Collection Rules](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Azure Monitor Ingestion API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Sentinel CCF Push Connectors](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector?tabs=push)
- [Custom Tables in Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/create-custom-table)

### Related Projects
- **JamfProtect CCF Push** - Reference pattern used as prototype
- **cveBusterPagination** - CCF Pull (polling) implementation
- **SentinelOne Connector** - Another CCF Push example

---

## 🤝 Contributing

This is a **learning and demonstration project**. Feel free to:
- Adapt for your own vulnerability scanner
- Add additional fields to the schema
- Implement advanced error handling
- Create analytics rules and workbooks
- Build automation playbooks

---

## 📄 License

MIT License - Use freely for learning and production.

---

## 🙏 Acknowledgments

Built for learning Microsoft Sentinel CCF connectors.
- Based on **JamfProtect** CCF Push pattern
- Inspired by **SentinelOne** integration architecture
- Uses Azure SDK best practices

---

**Version:** 1.0.0  
**Pattern:** CCF Push (Client-initiated)  
**Status:** Production-ready demo  
**Last Updated:** November 7, 2025
