# cveBuster CCF Push Connector - Deployment Guide

## ✅ Package Created Successfully!

Your CCF Push connector has been packaged and is ready to deploy to Microsoft Sentinel.

## 📦 Generated Files

```
Solutions/cveBusterPush/Package/
├── mainTemplate.json          ⭐ Main ARM deployment template
├── createUiDefinition.json    ⭐ Azure Portal UI definition
├── testParameters.json        📝 Test parameters file
└── 3.0.0.zip                  📦 Complete package archive
```

## 🚀 Deployment Options

### Option 1: Deploy via Azure Portal (Recommended for Testing)

1. **Navigate to Azure Portal**
   - Go to https://portal.azure.com
   - Navigate to your Sentinel workspace
   - Go to **Configuration** → **Content hub** → **Content management**

2. **Import the Solution**
   ```powershell
   # Upload the mainTemplate.json directly or use the .zip package
   ```

3. **Deploy the Connector**
   - Search for "cveBuster" in Content Hub
   - Click **Install**
   - Fill in required parameters:
     - Workspace name
     - Resource group
     - Secret for Entra App (save this!)

### Option 2: Deploy via PowerShell

```powershell
# Set your parameters
$resourceGroup = "your-sentinel-rg"
$workspace = "your-sentinel-workspace"
$location = "eastus"

# Deploy the template
New-AzResourceGroupDeployment `
  -ResourceGroupName $resourceGroup `
  -TemplateFile "C:\GitHub\Azure-Sentinel\Solutions\cveBusterPush\Package\mainTemplate.json" `
  -workspace $workspace `
  -workspace-location $location `
  -Verbose
```

### Option 3: Deploy via Azure CLI

```bash
# Set your parameters
RESOURCE_GROUP="your-sentinel-rg"
WORKSPACE="your-sentinel-workspace"
LOCATION="eastus"

# Deploy the template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file "C:/GitHub/Azure-Sentinel/Solutions/cveBusterPush/Package/mainTemplate.json" \
  --parameters workspace=$WORKSPACE workspace-location=$LOCATION
```

## 📋 What Gets Deployed

The deployment creates the following Azure resources:

1. **Data Collection Endpoint (DCE)**
   - Public endpoint: `https://[workspace]-[guid].ingest.monitor.azure.com`
   - Used by your scanner to push data

2. **Data Collection Rule (DCR)**
   - Defines the data schema (11 fields)
   - Includes KQL transformation for enrichment
   - Adds RiskScore calculation
   - Renames fields for consistency

3. **Custom Log Analytics Table**
   - Table name: `cveBusterVulnerabilities_CL`
   - 16 columns (including enriched fields)
   - Queryable immediately after deployment

4. **Entra ID App Registration**
   - Service Principal with auto-generated credentials
   - Assigned "Monitoring Metrics Publisher" role on DCR
   - Secret displayed once after deployment (save it!)

5. **Data Connector Definition**
   - Appears in Sentinel Data Connectors gallery
   - Shows connectivity status
   - Provides configuration UI

## 🔐 Post-Deployment: Get Credentials

After deployment, navigate to the connector page in Sentinel:

1. Go to **Sentinel** → **Configuration** → **Data connectors**
2. Search for **"cveBuster Vulnerability Scanner (Push)"**
3. Click **Open connector page**
4. Copy the following values:

```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "application_id": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
  "application_secret": "YOUR_SECRET_FROM_DEPLOYMENT",
  "dce_endpoint": "https://xxxx-xxxx.ingest.monitor.azure.com",
  "dcr_immutable_id": "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "stream_name": "Custom-cveBusterVulnerabilities"
}
```

## 🔧 Configure Your Scanner

Update `Solutions/cveBusterPush/PythonPushConnector/connector_config.json`:

```json
{
  "tenant_id": "<from connector page>",
  "application_id": "<from connector page>",
  "application_secret": "<from deployment>",
  "dce_endpoint": "<from connector page>",
  "dcr_immutable_id": "<from connector page>",
  "stream_name": "Custom-cveBusterVulnerabilities"
}
```

## 🧪 Test the Connection

### Step 1: Generate Test Data
```bash
cd Solutions/cveBusterPush/PythonPushConnector
python3 generate_data.py
```

### Step 2: Push Data to Sentinel
```bash
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json
```

Expected output:
```
📋 Configuration:
   Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Client ID: yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
   DCE: https://xxxx.ingest.monitor.azure.com
   DCR: dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Stream: Custom-cveBusterVulnerabilities
   Records to send: 500
   Batch size: 25

🔐 Authenticating with Azure...
🔗 Creating Azure Monitor Ingestion Client...

📤 Sending data in batches of 25...

Batch 1: Sending 25 records... ✅ Success
Batch 2: Sending 25 records... ✅ Success
...
Batch 20: Sending 25 records... ✅ Success

📊 Summary:
   Total Records: 500
   Successfully Sent: 500
   Failed: 0
   Success Rate: 100.0%
```

### Step 3: Query in Sentinel

Wait 5-10 minutes for data to appear, then run:

```kql
cveBusterVulnerabilities_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| take 10
```

## 📊 Sample Queries

### Critical vulnerabilities
```kql
cveBusterVulnerabilities_CL
| where VulnerabilitySeverity == "Critical"
| where IsExploitAvailable == true
| project TimeGenerated, AssetName, VulnerabilityId, VulnerabilityCVSS, RemediationStatus
| order by VulnerabilityCVSS desc
```

### Risk score distribution
```kql
cveBusterVulnerabilities_CL
| summarize Count=count() by RiskScore
| render columnchart
```

### Assets with most vulnerabilities
```kql
cveBusterVulnerabilities_CL
| where RemediationStatus == "Open"
| summarize VulnCount=count(), AvgRiskScore=avg(RiskScore) by AssetName
| order by VulnCount desc
| take 10
```

## 🛠️ Troubleshooting

### Data not appearing in Sentinel

1. **Check authentication**
   ```powershell
   # Verify service principal works
   az login --service-principal `
     -u <application_id> `
     -p <application_secret> `
     --tenant <tenant_id>
   ```

2. **Verify DCE is accessible**
   ```powershell
   Invoke-WebRequest -Uri "<dce_endpoint>" -Method HEAD
   ```

3. **Check DCR permissions**
   - Azure Portal → Monitor → Data Collection Rules
   - Select your DCR → Access control (IAM)
   - Verify service principal has "Monitoring Metrics Publisher" role

4. **Review DCR logs**
   ```kql
   AzureDiagnostics
   | where Category == "DataCollectionRuleIngestionLogs"
   | where ResourceId contains "cveBusterPushCustomDCR"
   | order by TimeGenerated desc
   ```

### Schema validation errors

Ensure your data matches the expected format:
- All datetime fields must be ISO 8601: `2025-11-06T10:30:00Z`
- CVSS must be numeric (float), not string
- Booleans must be `true`/`false`, not strings

### Rate limiting (429 errors)

The DCE has rate limits:
- Default: 1 MB/sec or 10 requests/sec
- Adjust batch size in `send_to_azure.py`
- Add delays between batches

## 🔄 Update the Connector

To update the connector after making changes:

1. **Modify connector files**
   ```
   Data Connectors/cveBusterPush_ccp/
   ├── connectorDefinition.json
   ├── dataConnector.json
   ├── DCR.json
   └── table.json
   ```

2. **Update version** in `Data/Solution_cveBuster.json`

3. **Repackage**
   ```powershell
   cd C:\GitHub\Azure-Sentinel\Tools\Create-Azure-Sentinel-Solution\V3
   .\createSolutionV3.ps1 `
     -packageConfigPath "C:\GitHub\Azure-Sentinel\Solutions\cveBusterPush\Data\Solution_cveBuster.json" `
     -outputFolderPath "C:\GitHub\Azure-Sentinel\Solutions\cveBusterPush\Package"
   ```

4. **Redeploy**
   ```powershell
   New-AzResourceGroupDeployment `
     -ResourceGroupName $resourceGroup `
     -TemplateFile "C:\GitHub\Azure-Sentinel\Solutions\cveBusterPush\Package\mainTemplate.json" `
     -workspace $workspace `
     -workspace-location $location
   ```

## 📚 Files Reference

### Core Connector Files
- **connectorDefinition.json** - UI definition, instructions, permissions
- **dataConnector.json** - Push connector configuration (kind: "Push")
- **DCR.json** - Data Collection Rule with schema and transformation
- **table.json** - Log Analytics table definition

### Generated Deployment Files
- **mainTemplate.json** - ARM template for deployment
- **createUiDefinition.json** - Azure Portal UI
- **testParameters.json** - Test parameters

### Python Client Files
- **send_to_azure.py** - Push client using Azure SDK
- **generate_data.py** - Test data generator
- **config_gui.py** - Configuration GUI

## 🎯 Next Steps

1. ✅ **Deploy the connector** using one of the methods above
2. ✅ **Configure your scanner** with the credentials
3. ✅ **Test data ingestion** with sample data
4. ✅ **Create Analytics Rules** to detect critical vulnerabilities
5. ✅ **Build Workbooks** for visualization
6. ✅ **Set up Automation** with Logic Apps

## 📞 Support Resources

- [Azure Monitor Ingestion API Docs](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Data Collection Rules](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/data-collection-rule-overview)
- [Sentinel CCF Documentation](https://learn.microsoft.com/en-us/azure/sentinel/create-codeless-connector)

---

**Status**: ✅ Ready to Deploy  
**Package Version**: 3.0.0  
**Last Updated**: November 6, 2025  
**Connector Type**: CCF Push Pattern
