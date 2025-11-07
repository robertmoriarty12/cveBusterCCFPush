#!/usr/bin/env python3
"""
Lightweight GUI for CCF Push Connector Configuration and Manual Data Push
Runs on Ubuntu with tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration file path
CONFIG_FILE = "connector_config.json"
DATA_FILE = "cvebuster_data.json"
GENERATE_SCRIPT = "generate_data.py"


class CCFPushConnectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CVE Buster - CCF Push Connector")
        self.root.geometry("700x650")
        
        # Configuration values
        self.config = self.load_config()
        
        # Create UI
        self.create_widgets()
        self.populate_fields()
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="CVE Buster CCF Push Connector", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Azure Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Tenant ID
        ttk.Label(config_frame, text="Tenant ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tenant_id_entry = ttk.Entry(config_frame, width=50)
        self.tenant_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Application (Client) ID
        ttk.Label(config_frame, text="Application ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.app_id_entry = ttk.Entry(config_frame, width=50)
        self.app_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Application Secret
        ttk.Label(config_frame, text="Application Secret:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.app_secret_entry = ttk.Entry(config_frame, width=50, show="*")
        self.app_secret_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # DCE Endpoint
        ttk.Label(config_frame, text="DCE Endpoint:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.dce_entry = ttk.Entry(config_frame, width=50)
        self.dce_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Label(config_frame, text="(e.g., https://xxx.ingest.monitor.azure.com)", 
                 font=('Arial', 8), foreground='gray').grid(row=4, column=1, sticky=tk.W)
        
        # DCR Immutable ID
        ttk.Label(config_frame, text="DCR Immutable ID:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.dcr_entry = ttk.Entry(config_frame, width=50)
        self.dcr_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Label(config_frame, text="(e.g., dcr-xxxxxxxxxxxxxxxxxxxxx)", 
                 font=('Arial', 8), foreground='gray').grid(row=6, column=1, sticky=tk.W)
        
        # Stream Name
        ttk.Label(config_frame, text="Stream Name:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.stream_entry = ttk.Entry(config_frame, width=50)
        self.stream_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Label(config_frame, text="(e.g., Custom-cveBusterv2_CL)", 
                 font=('Arial', 8), foreground='gray').grid(row=8, column=1, sticky=tk.W)
        
        # Save Config Button
        save_btn = ttk.Button(main_frame, text="💾 Save Configuration", 
                             command=self.save_config_action)
        save_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Data Generation & Push Section
        action_frame = ttk.LabelFrame(main_frame, text="Data Push Actions", padding="10")
        action_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Manual Send Button
        self.manual_send_btn = ttk.Button(action_frame, text="🚀 Manual Send", 
                                         command=self.manual_send_action,
                                         style='Accent.TButton')
        self.manual_send_btn.grid(row=0, column=0, padx=5, pady=10)
        
        # Generate Data Only Button
        generate_btn = ttk.Button(action_frame, text="📊 Generate Data Only", 
                                 command=self.generate_data_action)
        generate_btn.grid(row=0, column=1, padx=5, pady=10)
        
        # Status Label
        self.status_label = ttk.Label(action_frame, text="Status: Ready", 
                                     font=('Arial', 10))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Log Output
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70, 
                                                  state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear Log Button
        clear_log_btn = ttk.Button(log_frame, text="Clear Log", 
                                   command=self.clear_log)
        clear_log_btn.grid(row=1, column=0, pady=5)
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def log(self, message):
        """Add message to log output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        
    def clear_log(self):
        """Clear the log output"""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return {}
        return {}
        
    def populate_fields(self):
        """Populate form fields with saved config"""
        self.tenant_id_entry.insert(0, self.config.get('tenant_id', ''))
        self.app_id_entry.insert(0, self.config.get('application_id', ''))
        self.app_secret_entry.insert(0, self.config.get('application_secret', ''))
        self.dce_entry.insert(0, self.config.get('dce_endpoint', ''))
        self.dcr_entry.insert(0, self.config.get('dcr_immutable_id', ''))
        self.stream_entry.insert(0, self.config.get('stream_name', 'Custom-cveBusterv2_CL'))
        
    def save_config_action(self):
        """Save configuration to JSON file"""
        config = {
            'tenant_id': self.tenant_id_entry.get().strip(),
            'application_id': self.app_id_entry.get().strip(),
            'application_secret': self.app_secret_entry.get().strip(),
            'dce_endpoint': self.dce_entry.get().strip(),
            'dcr_immutable_id': self.dcr_entry.get().strip(),
            'stream_name': self.stream_entry.get().strip()
        }
        
        # Validate required fields
        if not all([config['tenant_id'], config['application_id'], 
                   config['application_secret'], config['dce_endpoint'], 
                   config['dcr_immutable_id'], config['stream_name']]):
            messagebox.showerror("Validation Error", 
                               "All fields are required!")
            return
            
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            self.config = config
            self.log("✅ Configuration saved successfully")
            self.status_label.config(text="Status: Configuration Saved")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            self.log(f"❌ Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save config: {e}")
            
    def generate_data_action(self):
        """Generate test data using generate_data.py"""
        self.log("📊 Generating test data...")
        self.status_label.config(text="Status: Generating Data...")
        
        if not os.path.exists(GENERATE_SCRIPT):
            self.log(f"❌ Error: {GENERATE_SCRIPT} not found in current directory")
            messagebox.showerror("Error", f"{GENERATE_SCRIPT} not found!")
            self.status_label.config(text="Status: Error")
            return
            
        try:
            result = subprocess.run(['python3', GENERATE_SCRIPT], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("✅ Test data generated successfully")
                self.log(result.stdout)
                self.status_label.config(text="Status: Data Generated")
                
                # Check if data file exists
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                    self.log(f"📦 Generated {len(data)} vulnerability records")
            else:
                self.log(f"❌ Error generating data: {result.stderr}")
                messagebox.showerror("Error", f"Failed to generate data:\n{result.stderr}")
                self.status_label.config(text="Status: Error")
        except subprocess.TimeoutExpired:
            self.log("❌ Data generation timed out")
            self.status_label.config(text="Status: Timeout")
        except Exception as e:
            self.log(f"❌ Exception: {e}")
            messagebox.showerror("Error", f"Exception: {e}")
            self.status_label.config(text="Status: Error")
            
    def manual_send_action(self):
        """Generate data and send to Azure DCE"""
        # Validate config exists
        if not all([self.config.get('tenant_id'), self.config.get('application_id'),
                   self.config.get('application_secret'), self.config.get('dce_endpoint'),
                   self.config.get('dcr_immutable_id'), self.config.get('stream_name')]):
            messagebox.showerror("Configuration Error", 
                               "Please save configuration before sending data!")
            return
            
        self.log("=" * 50)
        self.log("🚀 Starting Manual Send Operation")
        self.status_label.config(text="Status: Sending Data...")
        
        # Step 1: Generate data
        self.log("Step 1: Generating fresh test data...")
        self.generate_data_action()
        
        # Step 2: Check data file exists
        if not os.path.exists(DATA_FILE):
            self.log("❌ No data file found to send")
            self.status_label.config(text="Status: Error - No Data")
            return
            
        # Step 3: Send data to Azure
        self.log("Step 2: Sending data to Azure DCE...")
        try:
            # Call the send script
            result = subprocess.run([
                'python3', 'send_to_azure.py',
                '--config', CONFIG_FILE,
                '--data', DATA_FILE
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log("✅ Data sent successfully to Azure!")
                self.log(result.stdout)
                self.status_label.config(text="Status: Send Complete ✅")
                messagebox.showinfo("Success", "Data sent to Azure successfully!")
            else:
                self.log(f"❌ Error sending data: {result.stderr}")
                messagebox.showerror("Error", f"Failed to send data:\n{result.stderr}")
                self.status_label.config(text="Status: Send Failed ❌")
        except subprocess.TimeoutExpired:
            self.log("❌ Send operation timed out")
            self.status_label.config(text="Status: Timeout")
        except FileNotFoundError:
            self.log("❌ send_to_azure.py not found - creating it...")
            self.status_label.config(text="Status: Missing Script")
            messagebox.showwarning("Missing Script", 
                                 "send_to_azure.py not found. Please ensure it exists.")
        except Exception as e:
            self.log(f"❌ Exception: {e}")
            messagebox.showerror("Error", f"Exception: {e}")
            self.status_label.config(text="Status: Error")


def main():
    root = tk.Tk()
    app = CCFPushConnectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
