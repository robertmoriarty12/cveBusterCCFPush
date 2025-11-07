#!/usr/bin/env python3
"""
Quick Test Script - Verify Azure connection without GUI
"""
import json
import sys


def test_imports():
    """Test that all required packages are installed"""
    print("🧪 Testing Python imports...")
    
    try:
        import tkinter
        print("  ✅ tkinter")
    except ImportError:
        print("  ❌ tkinter - Install with: sudo apt install python3-tk")
        return False
    
    try:
        from azure.identity import ClientSecretCredential
        print("  ✅ azure-identity")
    except ImportError:
        print("  ❌ azure-identity - Install with: pip3 install azure-identity")
        return False
    
    try:
        from azure.monitor.ingestion import LogsIngestionClient
        print("  ✅ azure-monitor-ingestion")
    except ImportError:
        print("  ❌ azure-monitor-ingestion - Install with: pip3 install azure-monitor-ingestion")
        return False
    
    return True


def test_config():
    """Test that configuration file exists and is valid"""
    print("\n📋 Testing configuration...")
    
    try:
        with open('connector_config.json', 'r') as f:
            config = json.load(f)
        
        required_fields = [
            'tenant_id', 'application_id', 'application_secret',
            'dce_endpoint', 'dcr_immutable_id', 'stream_name'
        ]
        
        missing = [field for field in required_fields if not config.get(field)]
        
        if missing:
            print(f"  ⚠️  Configuration exists but missing fields: {', '.join(missing)}")
            return False
        
        print("  ✅ Configuration file is valid")
        print(f"     DCE: {config['dce_endpoint']}")
        print(f"     Stream: {config['stream_name']}")
        return True
        
    except FileNotFoundError:
        print("  ⚠️  connector_config.json not found")
        print("     Run the GUI and save configuration first")
        return False
    except json.JSONDecodeError:
        print("  ❌ connector_config.json is not valid JSON")
        return False


def test_data():
    """Test that data file can be generated"""
    print("\n📊 Testing data generation...")
    
    try:
        import subprocess
        result = subprocess.run(['python3', 'generate_data.py'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✅ Data generation successful")
            
            # Check file was created
            import os
            if os.path.exists('cvebuster_data.json'):
                with open('cvebuster_data.json', 'r') as f:
                    data = json.load(f)
                print(f"     Generated {len(data)} records")
                return True
        else:
            print(f"  ❌ Data generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("="*60)
    print("CVE Buster - System Test")
    print("="*60)
    print()
    
    results = {
        'imports': test_imports(),
        'config': test_config(),
        'data': test_data()
    }
    
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.capitalize()}: {status}")
    
    print()
    
    if all(results.values()):
        print("🎉 All tests passed! Ready to use the GUI.")
        print("   Run: python3 config_gui.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please resolve issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
