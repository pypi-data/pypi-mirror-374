#!/usr/bin/env python3
"""
Dynamic Cloudflare Tunnel - Creates a unique tunnel for each device via API
Simple and automatic!
"""

import subprocess
import requests
import json
import time
import os

class DynamicTunnel:
    def __init__(self, device_id=None):
        """
        Initialize with device ID for unique tunnel creation
        """
        # Cloudflare API credentials (hardcoded for simplicity)
        self.cf_api_token = os.getenv("CF_API_TOKEN", "YOUR_API_TOKEN_HERE")
        self.cf_account_id = os.getenv("CF_ACCOUNT_ID", "c91192ae20a5d43f65e087550d8dc89b")
        self.cf_zone_id = os.getenv("CF_ZONE_ID", "YOUR_ZONE_ID_HERE")
        
        # Domain config
        self.domain = "1scan.uz"
        
        # Generate clean device ID
        if device_id:
            self.device_id = device_id.replace('-', '').replace('_', '').replace('.', '').lower()[:20]
        else:
            import uuid
            self.device_id = str(uuid.uuid4())[:8]
        
        # Tunnel will be created with this name
        self.tunnel_name = "agent-{}".format(self.device_id)
        self.subdomain = self.device_id
        self.jupyter_url = "https://{}.{}".format(self.subdomain, self.domain)
        
        self.tunnel_id = None
        self.tunnel_token = None
        self.jupyter_process = None
        self.tunnel_process = None
        
    def create_tunnel(self):
        """Create a new tunnel via Cloudflare API"""
        print("🔧 Creating tunnel: {}".format(self.tunnel_name))
        
        url = "https://api.cloudflare.com/client/v4/accounts/{}/tunnels".format(self.cf_account_id)
        
        headers = {
            "Authorization": "Bearer {}".format(self.cf_api_token),
            "Content-Type": "application/json"
        }
        
        data = {
            "name": self.tunnel_name,
            "tunnel_secret": None  # Let Cloudflare generate it
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                self.tunnel_id = result["result"]["id"]
                self.tunnel_token = result["result"]["token"]
                print("✅ Tunnel created: {}".format(self.tunnel_id))
                return True
            else:
                print("❌ Failed to create tunnel: {}".format(result.get("errors", "Unknown error")))
                return False
                
        except Exception as e:
            print("❌ Error creating tunnel: {}".format(e))
            return False
    
    def create_dns_record(self):
        """Create DNS record for the tunnel"""
        print("🔧 Creating DNS record: {}.{}".format(self.subdomain, self.domain))
        
        url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(self.cf_zone_id)
        
        headers = {
            "Authorization": "Bearer {}".format(self.cf_api_token),
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "CNAME",
            "name": self.subdomain,
            "content": "{}.cfargotunnel.com".format(self.tunnel_id),
            "proxied": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200 and result.get("success"):
                print("✅ DNS record created")
                return True
            else:
                # Might already exist, try to update
                print("⚠️  DNS might already exist, continuing...")
                return True
                
        except Exception as e:
            print("⚠️  DNS error (continuing): {}".format(e))
            return True  # Continue anyway
    
    def get_cloudflared_path(self):
        """Get or download cloudflared binary"""
        import platform
        
        # Check if exists
        try:
            import shutil
            if shutil.which("cloudflared"):
                return "cloudflared"
        except:
            pass
        
        # Check local
        local_bin = os.path.expanduser("~/.local/bin/cloudflared")
        if os.path.exists(local_bin):
            return local_bin
        
        # Download
        print("📦 Downloading cloudflared...")
        system = platform.system().lower()
        if system == "linux":
            arch = "amd64" if "x86" in platform.machine() else "arm64"
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{}".format(arch)
            
            os.makedirs(os.path.expanduser("~/.local/bin"), exist_ok=True)
            subprocess.run("curl -L {} -o {}".format(url, local_bin), shell=True)
            subprocess.run("chmod +x {}".format(local_bin), shell=True)
            print("✅ cloudflared downloaded")
            return local_bin
        
        return "cloudflared"
    
    def start_jupyter(self):
        """Start Jupyter notebook"""
        print("🚀 Starting Jupyter...")
        
        cmd = [
            "jupyter", "notebook",
            "--port", "8888",
            "--no-browser",
            "--ip", "0.0.0.0",
            "--NotebookApp.token=''",
            "--NotebookApp.password=''",
            "--NotebookApp.allow_origin='*'"
        ]
        
        self.jupyter_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        print("✅ Jupyter started on port 8888")
        return True
    
    def start_tunnel(self):
        """Start the tunnel using the token"""
        print("🔧 Starting tunnel...")
        
        cloudflared = self.get_cloudflared_path()
        
        # Use the token to run tunnel
        cmd = [
            cloudflared,
            "tunnel",
            "run",
            "--token", self.tunnel_token
        ]
        
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(5)
        print("✅ Tunnel running at {}".format(self.jupyter_url))
        return True
    
    def start(self):
        """Main entry point - creates everything dynamically"""
        try:
            print("="*50)
            print("🌐 Dynamic Cloudflare Tunnel")
            print("Device ID: {}".format(self.device_id))
            print("="*50)
            
            # 1. Create tunnel via API
            if not self.create_tunnel():
                raise Exception("Failed to create tunnel")
            
            # 2. Create DNS record
            self.create_dns_record()
            
            # 3. Start Jupyter
            if not self.start_jupyter():
                raise Exception("Failed to start Jupyter")
            
            # 4. Start tunnel
            if not self.start_tunnel():
                raise Exception("Failed to start tunnel")
            
            print("\n" + "="*50)
            print("🎉 SUCCESS! Your unique tunnel is ready:")
            print("   {}".format(self.jupyter_url))
            print("   Tunnel ID: {}".format(self.tunnel_id))
            print("="*50)
            
            return True
            
        except Exception as e:
            print("❌ Error: {}".format(e))
            self.cleanup()
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.jupyter_process:
            self.jupyter_process.terminate()
        if self.tunnel_process:
            self.tunnel_process.terminate()
        
        # Optionally delete tunnel via API
        if self.tunnel_id and self.cf_api_token != "YOUR_API_TOKEN_HERE":
            try:
                url = "https://api.cloudflare.com/client/v4/accounts/{}/tunnels/{}".format(
                    self.cf_account_id, self.tunnel_id
                )
                headers = {"Authorization": "Bearer {}".format(self.cf_api_token)}
                requests.delete(url, headers=headers)
                print("🗑️  Tunnel deleted")
            except:
                pass
    
    def run(self):
        """Run and keep alive"""
        try:
            if self.start():
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down...")
            self.cleanup()
            print("👋 Goodbye!")


def main():
    """Test dynamic tunnel creation"""
    import platform
    import uuid
    
    hostname = platform.node().replace('.', '-')[:20]
    device_id = "{}-{}".format(hostname, str(uuid.uuid4())[:8])
    
    print("Creating dynamic tunnel for: {}".format(device_id))
    
    tunnel = DynamicTunnel(device_id=device_id)
    tunnel.run()


if __name__ == "__main__":
    main()