#!/usr/bin/env python3
"""
Simple API-based Dynamic Tunnel - Each device gets deviceid.1scan.uz
"""

import subprocess
import requests
import json
import time
import os

class APITunnel:
    def __init__(self, device_id=None):
        """Initialize with device ID"""
        # Hardcoded Cloudflare credentials for simplicity
        self.cf_email = "muminovbobur93@gmail.com"
        self.cf_api_key = "1ae47782b5e2e639fb088ee73e17b74db4b4e"  # Global API Key
        self.cf_account_id = "c91192ae20a5d43f65e087550d8dc89b"
        self.cf_zone_id = "06ebea0ee0b228c186f97fe9a0a7c83e"  # for 1scan.uz
        
        # Clean device ID for subdomain
        if device_id:
            self.device_id = device_id.replace('-', '').replace('_', '').replace('.', '').lower()[:20]
        else:
            import uuid
            self.device_id = str(uuid.uuid4())[:8]
        
        self.tunnel_name = "agent-{}".format(self.device_id)
        self.subdomain = self.device_id
        self.jupyter_url = "https://{}.1scan.uz".format(self.subdomain)
        
        self.tunnel_id = None
        self.tunnel_token = None
        self.jupyter_process = None
        self.tunnel_process = None
    
    def create_tunnel_via_cli(self):
        """Create tunnel using cloudflared CLI (simpler than API)"""
        print("🔧 Creating tunnel: {}...".format(self.tunnel_name))
        
        cloudflared = self.get_cloudflared_path()
        
        # Login with cert (one-time if not logged in)
        # This uses the cert.pem file if it exists
        cert_path = os.path.expanduser("~/.cloudflared/cert.pem")
        if not os.path.exists(cert_path):
            print("📝 First time setup - logging in to Cloudflare...")
            # Use service token instead of interactive login
            # Or use the API to create tunnel
        
        # Create tunnel using CLI
        cmd = [cloudflared, "tunnel", "create", self.tunnel_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract tunnel ID from output
            import re
            match = re.search(r'Created tunnel .* with id ([a-f0-9-]+)', result.stdout)
            if match:
                self.tunnel_id = match.group(1)
                print("✅ Tunnel created: {}".format(self.tunnel_id))
                
                # Get the tunnel token
                token_cmd = [cloudflared, "tunnel", "token", self.tunnel_name]
                token_result = subprocess.run(token_cmd, capture_output=True, text=True)
                if token_result.returncode == 0:
                    self.tunnel_token = token_result.stdout.strip()
                    return True
        
        print("⚠️  Could not create tunnel via CLI, using quick tunnel instead")
        return False
    
    def create_dns_record(self):
        """Add DNS record for subdomain"""
        if not self.tunnel_id:
            return False
            
        print("🔧 Creating DNS: {}.1scan.uz...".format(self.subdomain))
        
        url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(self.cf_zone_id)
        
        headers = {
            "X-Auth-Email": self.cf_email,
            "X-Auth-Key": self.cf_api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "CNAME",
            "name": self.subdomain,
            "content": "{}.cfargotunnel.com".format(self.tunnel_id),
            "proxied": True
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 409]:  # 409 = already exists
            print("✅ DNS configured")
            return True
        
        print("⚠️  DNS setup failed: {}".format(response.text[:100]))
        return False
    
    def get_cloudflared_path(self):
        """Get or download cloudflared"""
        import shutil
        if shutil.which("cloudflared"):
            return "cloudflared"
        
        local_bin = os.path.expanduser("~/.local/bin/cloudflared")
        if os.path.exists(local_bin):
            return local_bin
        
        # Download
        print("📦 Downloading cloudflared...")
        import platform
        system = platform.system().lower()
        arch = "amd64" if "x86" in platform.machine() else "arm64"
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{}".format(arch)
        
        os.makedirs(os.path.dirname(local_bin), exist_ok=True)
        subprocess.run("curl -L {} -o {}".format(url, local_bin), shell=True, capture_output=True)
        subprocess.run("chmod +x {}".format(local_bin), shell=True)
        return local_bin
    
    def start_jupyter(self):
        """Start Jupyter"""
        print("🚀 Starting Jupyter...")
        
        cmd = [
            "jupyter", "notebook",
            "--port", "8888",
            "--no-browser",
            "--ip", "0.0.0.0",
            "--NotebookApp.token=''",
            "--NotebookApp.password=''"
        ]
        
        self.jupyter_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        print("✅ Jupyter started")
        return True
    
    def start_tunnel(self):
        """Start tunnel - try with token first, fallback to quick tunnel"""
        cloudflared = self.get_cloudflared_path()
        
        if self.tunnel_token:
            # Use token-based tunnel
            print("🔧 Starting tunnel with token...")
            cmd = [cloudflared, "tunnel", "run", "--token", self.tunnel_token]
        elif self.tunnel_id:
            # Use tunnel ID
            print("🔧 Starting tunnel with ID...")
            cmd = [cloudflared, "tunnel", "run", "--url", "http://localhost:8888", self.tunnel_id]
        else:
            # Fallback to quick tunnel
            print("🔧 Starting quick tunnel (random URL)...")
            cmd = [cloudflared, "tunnel", "--url", "http://localhost:8888"]
            self.jupyter_url = "Check terminal output for URL"
        
        self.tunnel_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        time.sleep(5)
        print("✅ Tunnel running")
        return True
    
    def start(self):
        """Main entry point"""
        try:
            print("="*50)
            print("🌐 API-Based Dynamic Tunnel")
            print("Device: {}".format(self.device_id))
            print("="*50)
            
            # Try to create named tunnel
            tunnel_created = self.create_tunnel_via_cli()
            
            if tunnel_created:
                # Add DNS record
                self.create_dns_record()
            
            # Start services
            self.start_jupyter()
            self.start_tunnel()
            
            print("\n" + "="*50)
            print("🎉 SUCCESS!")
            if tunnel_created:
                print("📍 Your permanent URL: {}".format(self.jupyter_url))
            else:
                print("📍 Using quick tunnel - check output for URL")
            print("="*50)
            
            return True
            
        except Exception as e:
            print("❌ Error: {}".format(e))
            self.stop()
            return False
    
    def stop(self):
        """Stop everything"""
        if self.jupyter_process:
            self.jupyter_process.terminate()
        if self.tunnel_process:
            self.tunnel_process.terminate()
    
    def run(self):
        """Run and keep alive"""
        try:
            if self.start():
                print("\nPress Ctrl+C to stop...")
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down...")
            self.stop()


def main():
    """Test the API tunnel"""
    import platform
    import uuid
    
    hostname = platform.node().replace('.', '-')[:20]
    device_id = "{}-{}".format(hostname, str(uuid.uuid4())[:8])
    
    tunnel = APITunnel(device_id=device_id)
    tunnel.run()


if __name__ == "__main__":
    main()