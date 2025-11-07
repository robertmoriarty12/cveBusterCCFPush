#!/bin/bash
# cveBuster CCF Push - Quick Start Script
# Run this on your Linux box to send data to Sentinel

echo "=============================================="
echo "cveBuster CCF Push Connector - Quick Start"
echo "=============================================="
echo ""

# Step 1: Install Python dependencies
echo "📦 Step 1: Installing Python dependencies..."
pip3 install azure-identity azure-monitor-ingestion
echo "✅ Dependencies installed"
echo ""

# Step 2: Generate test data
echo "📊 Step 2: Generating test vulnerability data..."
python3 generate_data.py
echo "✅ Test data generated (cvebuster_data.json)"
echo ""

# Step 3: Send data to Azure Sentinel
echo "🚀 Step 3: Pushing data to Azure Sentinel..."
python3 send_to_azure.py \
  --config connector_config.json \
  --data cvebuster_data.json \
  --batch-size 25

echo ""
echo "=============================================="
echo "✅ Done! Check Sentinel in 5-10 minutes"
echo "=============================================="
echo ""
echo "Query in Sentinel:"
echo "cveBusterVulnerabilities_CL"
echo "| where TimeGenerated > ago(1h)"
echo "| order by TimeGenerated desc"
echo "| take 10"
