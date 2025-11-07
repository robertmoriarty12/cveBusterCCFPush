#!/usr/bin/env python3
"""
Send CVE data to Azure Monitor using Data Collection Endpoint (DCE)
Uses Client Secret Credential for authentication
"""
import json
import uuid
import time
import argparse
from datetime import datetime
from azure.identity import ClientSecretCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError


def load_config(config_file):
    """Load Azure configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)


def load_data(data_file):
    """Load vulnerability data from JSON file"""
    with open(data_file, 'r') as f:
        return json.load(f)


def send_to_azure(config, data, batch_size=25):
    """
    Send data to Azure Monitor via Data Collection Endpoint
    
    Args:
        config: Dictionary with Azure configuration
        data: List of vulnerability records
        batch_size: Number of records to send per batch
    """
    print(f"\n{'='*60}")
    print(f"CVE Buster - Azure Data Ingestion")
    print(f"{'='*60}\n")
    
    # Extract configuration
    tenant_id = config['tenant_id']
    client_id = config['application_id']
    client_secret = config['application_secret']
    dce_endpoint = config['dce_endpoint']
    dcr_immutable_id = config['dcr_immutable_id']
    stream_name = config['stream_name']
    
    print(f"📋 Configuration:")
    print(f"   Tenant ID: {tenant_id}")
    print(f"   Client ID: {client_id}")
    print(f"   DCE: {dce_endpoint}")
    print(f"   DCR: {dcr_immutable_id}")
    print(f"   Stream: {stream_name}")
    print(f"   Records to send: {len(data)}")
    print(f"   Batch size: {batch_size}\n")
    
    # Create credential
    print("🔐 Authenticating with Azure...")
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False
    
    # Create logs ingestion client
    print("🔗 Creating Azure Monitor Ingestion Client...")
    try:
        client = LogsIngestionClient(
            endpoint=dce_endpoint,
            credential=credential,
            logging_enable=True
        )
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # Send data in batches
    print(f"\n📤 Sending data in batches of {batch_size}...\n")
    total_sent = 0
    total_failed = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"Batch {batch_num}: Sending {len(batch)} records...", end=" ")
        
        try:
            # Upload batch to Azure Monitor
            response = client.upload(
                rule_id=dcr_immutable_id,
                stream_name=stream_name,
                logs=batch
            )
            
            print(f"✅ Success")
            total_sent += len(batch)
            
        except HttpResponseError as e:
            print(f"❌ Failed (HTTP {e.status_code})")
            print(f"   Error: {e.message}")
            total_failed += len(batch)
            
            # Retry logic for transient errors
            if e.status_code in [429, 500, 502, 503, 504]:
                print(f"   Retrying in 2 seconds...")
                time.sleep(2)
                try:
                    response = client.upload(
                        rule_id=dcr_immutable_id,
                        stream_name=stream_name,
                        logs=batch
                    )
                    print(f"   ✅ Retry successful")
                    total_sent += len(batch)
                    total_failed -= len(batch)
                except Exception as retry_error:
                    print(f"   ❌ Retry failed: {retry_error}")
            else:
                # Non-transient error, stop processing
                break
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            total_failed += len(batch)
            break
            
        # Small delay between batches to avoid rate limiting
        if i + batch_size < len(data):
            time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary:")
    print(f"   Total Records: {len(data)}")
    print(f"   Successfully Sent: {total_sent}")
    print(f"   Failed: {total_failed}")
    print(f"   Success Rate: {(total_sent/len(data)*100):.1f}%")
    print(f"{'='*60}\n")
    
    return total_failed == 0


def main():
    parser = argparse.ArgumentParser(description='Send CVE data to Azure Monitor')
    parser.add_argument('--config', required=True, help='Path to config JSON file')
    parser.add_argument('--data', required=True, help='Path to data JSON file')
    parser.add_argument('--batch-size', type=int, default=25, 
                       help='Number of records per batch (default: 25)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration and data
        config = load_config(args.config)
        data = load_data(args.data)
        
        # Send to Azure
        success = send_to_azure(config, data, args.batch_size)
        
        if success:
            print("✅ All data sent successfully!")
            exit(0)
        else:
            print("⚠️  Some data failed to send")
            exit(1)
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        exit(1)
    except KeyError as e:
        print(f"❌ Missing configuration key: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
