#!/usr/bin/env python3
"""
Generate mock vulnerability data for CVE Buster
Creates test data with LastModified timestamps for testing CCF Push connector
"""
import json
import random
from datetime import datetime, timedelta


def generate_vulnerability_data(num_records=500):
    """
    Generate mock vulnerability data with LastModified distribution:
    - 70% old records (30-90 days ago)
    - 30% recent records (within last 2 minutes)
    
    This ensures records fall within CCF's 5-minute query window for testing.
    """
    vulnerabilities = []
    severity_levels = ["Critical", "High", "Medium", "Low"]
    machine_names = [f"SRV-{random.choice(['WEB', 'APP', 'DB', 'DC'])}-{i:03d}" 
                     for i in range(1, 51)]
    
    now = datetime.utcnow()
    
    for i in range(1, num_records + 1):
        # 30% recent (last 2 minutes), 70% old (30-90 days ago)
        if random.random() < 0.30:
            # Recent records - within last 2 minutes (120 seconds)
            seconds_ago = random.randint(0, 120)
            last_modified = now - timedelta(seconds=seconds_ago)
        else:
            # Old records - 30 to 90 days ago
            days_ago = random.randint(30, 90)
            last_modified = now - timedelta(days=days_ago)
        
        # Discovery date is always before last modified
        days_before_modified = random.randint(1, 30)
        discovery_date = last_modified - timedelta(days=days_before_modified)
        
        severity = random.choice(severity_levels)
        cvss = round(random.uniform(4.0, 10.0), 1)
        
        vuln = {
            "VulnId": f"CVE-2024-{10000 + i}",
            "VulnTitle": f"Security Vulnerability {i}",
            "Severity": severity,
            "CVSS": cvss,
            "MachineName": random.choice(machine_names),
            "AssetCriticality": random.choice(["High", "Medium", "Low"]),
            "PatchAvailable": random.choice([True, False]),
            "ExploitAvailable": random.choice([True, False]),
            "DiscoveryDate": discovery_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "LastModified": last_modified.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Status": random.choice(["Open", "In Progress", "Patched"])
        }
        vulnerabilities.append(vuln)
    
    return vulnerabilities


if __name__ == "__main__":
    print("Generating 500 vulnerability records...")
    print("Distribution: 70% old (30-90 days ago), 30% recent (last 2 minutes)")
    
    data = generate_vulnerability_data(500)
    
    # Count recent vs old
    now = datetime.utcnow()
    recent_count = sum(1 for v in data 
                      if (now - datetime.strptime(v['LastModified'], 
                          "%Y-%m-%dT%H:%M:%SZ")).total_seconds() < 120)
    
    with open('cvebuster_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Generated {len(data)} records")
    print(f"   - Recent (last 2 min): {recent_count}")
    print(f"   - Old (30-90 days): {len(data) - recent_count}")
    print("Saved to cvebuster_data.json")
