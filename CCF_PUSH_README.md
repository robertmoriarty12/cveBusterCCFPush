# cveBuster Push Connector for Microsoft Sentinel

A production-ready Codeless Connector Framework (CCF) Push connector that enables your cveBuster vulnerability scanner to push data directly to Microsoft Sentinel via Azure Monitor Ingestion API.

## 🎯 What is CCF Push?

Unlike CCF Pull (where Sentinel polls your API), **CCF Push** allows your application to push data directly to Azure:
- ✅ **Your app controls timing** - Send data when events occur
- ✅ **No API endpoint needed** - No need to host a public API
- ✅ **Secure authentication** - Uses Entra ID Service Principal
- ✅ **Automatic retry** - Built-in error handling
- ✅ **Real-time ingestion** - Data appears in minutes

## 📋 Architecture

```
┌─────────────────────────┐
│  cveBuster Scanner      │
│  (Your Python App)      │
└───────────┬─────────────┘
            │
            │ 1. Authenticate with Entra ID
            │    (Tenant ID + Client ID + Secret)
            ▼
┌─────────────────────────────────────┐
│  Azure Active Directory             │
│  Returns: OAuth 2.0 Bearer Token    │
└───────────┬─────────────────────────┘
            │
            │ 2. POST data with token
            ▼
┌─────────────────────────────────────┐
│  Data Collection Endpoint (DCE)     │
│  https://xxx.ingest.monitor.azure.com │
└───────────┬─────────────────────────┘
            │
            │ 3. Apply transformation
            ▼
┌─────────────────────────────────────┐
│  Data Collection Rule (DCR)         │
│  • Validates schema                 │
│  • Enriches data (RiskScore)        │
│  • Renames fields                   │
└───────────┬─────────────────────────┘
            │
            │ 4. Ingest to table
            ▼
┌─────────────────────────────────────┐
│  Log Analytics Workspace            │
│  cveBusterVulnerabilities_CL        │
└───────────┬─────────────────────────┘
            │
            │ 5. Analyze & Alert
            ▼
┌─────────────────────────────────────┐
│  Microsoft Sentinel                 │
│  • Analytics Rules                  │
│  • Workbooks                        │
│  • Incidents                        │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Microsoft Sentinel workspace
- Azure subscription with Owner or Contributor permissions
- PowerShell with Az modules
- Python 3.x (for cveBuster scanner)

### Step 1: Package the Solution

```powershell
cd C:\GitHub\Azure-Sentinel\Tools\Create-Azure-Sentinel-Solution\V3
.\createSolutionV3.ps1 `
  -packageConfigPath "C:\GitHub\Azure-Sentinel\Solutions\cveBusterPush\Data\Solution_cveBuster.json" `
  -outputFolderPath "C:\GitHub\Azure-Sentinel\Solutions\cveBusterPush\Package"
```

### Step 2: Deploy to Sentinel

1. Navigate to your Sentinel workspace in Azure Portal
2. Go to **Configuration** → **Data connectors**
3. Click **Import** and upload the packaged solution
4. Find **cveBuster Vulnerability Scanner (Push)** connector
5. Click **Open connector page**
6. Click **Deploy cveBuster Push connector resources**
7. Enter a secret for the Entra application (save this!)
8. Wait for deployment (creates DCE, DCR, Table, Entra App)

### Step 3: Get Configuration Values

After deployment, copy these values from the connector page:
- ✅ Tenant ID
- ✅ Application ID
- ✅ Application Secret (the one you entered)
- ✅ Data Collection Endpoint Uri
- ✅ Data Collection Rule Immutable ID
- ✅ Stream Name: `Custom-cveBusterVulnerabilities`

### Step 4: Update Your Scanner Configuration

Update your cveBuster scanner's `connector_config.json`:

```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "application_id": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
  "application_secret": "your-secret-from-deployment",
  "dce_endpoint": "https://xxxx-xxxx.ingest.monitor.azure.com",
  "dcr_immutable_id": "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "stream_name": "Custom-cveBusterVulnerabilities"
}
```

### Step 5: Run Your Scanner

```bash
cd Solutions/cveBusterPush/PythonPushConnector
python3 send_to_azure.py --config connector_config.json --data cvebuster_data.json
```

### Step 6: Verify Data in Sentinel

```kql
cveBusterVulnerabilities_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 10
```

## 📊 Data Schema

The connector ingests vulnerability data with the following enriched schema:

| Field | Type | Description |
|-------|------|-------------|
| `TimeGenerated` | datetime | Ingestion timestamp |
| `EventVendor` | string | Always "cveBuster" |
| `EventProduct` | string | Always "Vulnerability Scanner" |
| `EventType` | string | Always "Vulnerability" |
| `VulnerabilityId` | string | CVE ID (e.g., CVE-2024-1234) |
| `VulnerabilityTitle` | string | Vulnerability description |
| `VulnerabilitySeverity` | string | Critical/High/Medium/Low |
| `VulnerabilityCVSS` | real | CVSS score (0.0-10.0) |
| `AssetName` | string | Machine/host name |
| `AssetPriority` | string | Asset criticality |
| `IsPatchAvailable` | boolean | Patch availability |
| `IsExploitAvailable` | boolean | Public exploit exists |
| `FirstDetected` | datetime | Discovery date |
| `LastUpdated` | datetime | Last modified date |
| `RemediationStatus` | string | Open/In Progress/Patched |
| `RiskScore` | int | Calculated risk (1-10) |

## 🔐 Security Features

### Authentication
- ✅ **OAuth 2.0** - Industry-standard authentication
- ✅ **Service Principal** - Dedicated Entra app for connector
- ✅ **Token caching** - Automatic token refresh by Azure SDK
- ✅ **RBAC** - Monitoring Metrics Publisher role on DCR

### Data Protection
- ✅ **TLS encryption** - All data in transit is encrypted
- ✅ **Schema validation** - DCR enforces data types
- ✅ **Access control** - Workspace-level permissions required

## 📈 Sample KQL Queries

### Critical vulnerabilities with exploits
```kql
cveBusterVulnerabilities_CL
| where VulnerabilitySeverity == "Critical" 
| where IsExploitAvailable == true
| project TimeGenerated, AssetName, VulnerabilityId, VulnerabilityCVSS, RemediationStatus
| order by VulnerabilityCVSS desc
```

### Vulnerability count by severity
```kql
cveBusterVulnerabilities_CL
| where TimeGenerated > ago(7d)
| summarize Count=count() by VulnerabilitySeverity
| render piechart
```

### Top 10 vulnerable assets
```kql
cveBusterVulnerabilities_CL
| where RemediationStatus == "Open"
| summarize VulnCount=count(), AvgRiskScore=avg(RiskScore) by AssetName
| order by VulnCount desc
| take 10
```

### Patching progress over time
```kql
cveBusterVulnerabilities_CL
| summarize 
    Open=countif(RemediationStatus == "Open"),
    InProgress=countif(RemediationStatus == "In Progress"),
    Patched=countif(RemediationStatus == "Patched")
    by bin(TimeGenerated, 1d)
| render timechart
```

## 🔧 DCR Transformation Logic

The DCR automatically enriches your data:

### Risk Score Calculation
```kql
RiskScore = case(
    Severity == 'Critical' and ExploitAvailable == true, 10,
    Severity == 'Critical' and ExploitAvailable == false, 9,
    Severity == 'High' and ExploitAvailable == true, 8,
    Severity == 'High' and ExploitAvailable == false, 7,
    Severity == 'Medium' and ExploitAvailable == true, 6,
    Severity == 'Medium' and ExploitAvailable == false, 5,
    Severity == 'Low', 3,
    1
)
```

### Field Renaming
- `VulnId` → `VulnerabilityId`
- `MachineName` → `AssetName`
- `AssetCriticality` → `AssetPriority`
- `DiscoveryDate` → `FirstDetected`
- `LastModified` → `LastUpdated`
- `Status` → `RemediationStatus`

## 🛠️ Troubleshooting

### No data appearing
```powershell
# Test authentication
az login --service-principal --username <AppId> --password <Secret> --tenant <TenantId>

# Verify DCE is reachable
Invoke-WebRequest -Uri "https://<DCE>.ingest.monitor.azure.com" -Method HEAD

# Check Python SDK logs
# Enable logging in send_to_azure.py with logging_enable=True
```

### Authentication errors
- ✅ Verify Application ID and Secret are correct
- ✅ Ensure Tenant ID matches your Entra tenant
- ✅ Check service principal has "Monitoring Metrics Publisher" role on DCR
- ✅ Confirm secret hasn't expired (check Entra app registration)

### Schema validation errors
- ✅ Ensure all datetime fields are in ISO 8601 format
- ✅ Verify CVSS is a number (float/int), not string
- ✅ Check boolean fields are `true`/`false`, not strings
- ✅ Validate required fields are present (VulnId, Severity, etc.)

### Data not transforming correctly
- ✅ Check DCR transformation KQL in Azure Portal
- ✅ Verify field names match exactly (case-sensitive)
- ✅ Test transformation in Log Analytics with sample data
- ✅ Review Azure Monitor DCR logs for errors

## 📚 File Structure

```
cveBusterPush/
├── Data/
│   └── Solution_cveBuster.json        # Solution package config
├── Data Connectors/
│   └── cveBusterPush_ccp/
│       ├── connectorDefinition.json   # UI definition
│       ├── dataConnector.json         # Push connector config
│       ├── DCR.json                   # Data Collection Rule
│       └── table.json                 # Table schema
├── PythonPushConnector/
│   ├── send_to_azure.py              # Push client
│   ├── generate_data.py              # Test data generator
│   └── config_gui.py                 # Configuration GUI
├── Package/                          # Generated by packaging tool
├── SolutionMetadata.json             # Publisher metadata
└── README.md                         # This file
```

## 🔄 Update Workflow

When you need to update the connector:

1. **Modify connector files** in `Data Connectors/cveBusterPush_ccp/`
2. **Update version** in `Data/Solution_cveBuster.json`
3. **Repackage** using createSolutionV3.ps1
4. **Redeploy** to Sentinel (incremental update)

## 📖 References

- [Microsoft Sentinel CCF Documentation](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector)
- [Azure Monitor Ingestion API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Data Collection Rules](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Jamf Protect Reference](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/Jamf%20Protect)

## 📞 Support

For issues or questions:
- Review troubleshooting section above
- Check Azure Monitor DCR logs
- Test connectivity from your scanner
- Review Microsoft Sentinel documentation

---

**Version**: 1.0.0  
**Last Updated**: November 6, 2025  
**Connector Type**: CCF Push (Client pushes to Azure)  
**Pattern**: Based on Jamf Protect CCF Push connector
