#!/usr/bin/env python3
"""
Demo mode for config_gui.py - Pre-fills with example values
Useful for testing the GUI without real Azure credentials
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# Import the main app but override config loading
import config_gui


class DemoMode(config_gui.CCFPushConnectorGUI):
    """Demo version with pre-filled example data"""
    
    def load_config(self):
        """Override to load demo config"""
        return {
            'tenant_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'application_id': 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy',
            'application_secret': 'demo-secret-not-real',
            'dce_endpoint': 'https://demo-dce-xxxxx.ingest.monitor.azure.com',
            'dcr_immutable_id': 'dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'stream_name': 'Custom-cveBusterv2_CL'
        }
    
    def manual_send_action(self):
        """Override to simulate sending without real Azure"""
        self.log("=" * 50)
        self.log("🎬 DEMO MODE - Simulating Manual Send")
        self.log("(No real data sent to Azure)")
        self.log("=" * 50)
        self.status_label.config(text="Status: Demo Mode")
        
        # Simulate data generation
        self.log("Step 1: Generating test data...")
        import time
        time.sleep(1)
        self.log("✅ Generated 500 vulnerability records")
        
        # Simulate sending
        self.log("Step 2: Sending to Azure DCE...")
        time.sleep(1)
        self.log("Batch 1: Sending 25 records... ✅ Success")
        time.sleep(0.5)
        self.log("Batch 2: Sending 25 records... ✅ Success")
        time.sleep(0.5)
        self.log("Batch 3: Sending 25 records... ✅ Success")
        time.sleep(0.5)
        self.log("...")
        time.sleep(0.5)
        self.log("Batch 20: Sending 25 records... ✅ Success")
        
        self.log("\n" + "=" * 50)
        self.log("📊 Summary:")
        self.log("   Total Records: 500")
        self.log("   Successfully Sent: 500")
        self.log("   Failed: 0")
        self.log("   Success Rate: 100.0%")
        self.log("=" * 50)
        self.log("\n✅ DEMO: Data would be sent successfully!")
        
        self.status_label.config(text="Status: Demo Complete ✅")
        messagebox.showinfo("Demo Complete", 
                          "This is demo mode - no data actually sent.\n\n"
                          "To send real data:\n"
                          "1. Enter real Azure credentials\n"
                          "2. Use the regular config_gui.py")


def main():
    root = tk.Tk()
    app = DemoMode(root)
    
    # Add demo mode indicator
    demo_label = tk.Label(root, text="🎬 DEMO MODE", 
                         font=('Arial', 12, 'bold'),
                         bg='yellow', fg='black')
    demo_label.place(relx=1.0, x=-10, y=10, anchor='ne')
    
    root.mainloop()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎬 Running in DEMO MODE")
    print("="*60)
    print("Pre-filled with example values - no real Azure connection")
    print("Useful for testing the GUI without real credentials")
    print("="*60 + "\n")
    main()
