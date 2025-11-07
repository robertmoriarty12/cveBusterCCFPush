#!/bin/bash
# Setup script for CVE Buster CCF Push Connector on Ubuntu

echo "======================================================"
echo "CVE Buster - CCF Push Connector Setup"
echo "======================================================"
echo ""

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Ubuntu"
    echo "   It may work on other Debian-based systems"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install Python 3 and tkinter
echo "🐍 Installing Python 3 and tkinter..."
sudo apt install -y python3 python3-pip python3-tk

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION installed"

# Install required Python packages
echo "📚 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
echo "🔧 Setting executable permissions..."
chmod +x config_gui.py
chmod +x send_to_azure.py
chmod +x generate_data.py

# Verify installation
echo ""
echo "======================================================"
echo "✅ Setup Complete!"
echo "======================================================"
echo ""
echo "To launch the application:"
echo "  python3 config_gui.py"
echo ""
echo "Or:"
echo "  ./config_gui.py"
echo ""
echo "======================================================"
echo ""

# Test imports
echo "🧪 Testing Python imports..."
python3 -c "import tkinter; print('  ✅ tkinter')"
python3 -c "from azure.identity import ClientSecretCredential; print('  ✅ azure-identity')"
python3 -c "from azure.monitor.ingestion import LogsIngestionClient; print('  ✅ azure-monitor-ingestion')"

echo ""
echo "🚀 Ready to go! Run: python3 config_gui.py"
