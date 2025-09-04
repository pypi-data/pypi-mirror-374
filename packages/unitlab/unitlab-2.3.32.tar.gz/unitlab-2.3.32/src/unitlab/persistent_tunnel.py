#!/usr/bin/env python3
"""
Persistent Tunnel - Each device gets deviceid.1scan.uz
Uses Cloudflare API to create named tunnels
"""

import subprocess
import requests
import json
import time
import os
import base64

class PersistentTunnel:
    def __init__(self, device_id=None):
        """Initialize with device ID"""
        
        # Cloudflare credentials (hardcoded for simplicity)
        self.cf_email = "uone2323@gmail.com"
        self.cf_api_key = "1c634bd17ca6ade0eb91966323589fd98c72e"  # Global API Key
        
        # Account and Zone IDs
        self.cf_account_id = "c91192ae20a5d43f65e087550d8dc89b"  # Your account ID
        self.cf_zone_id = "78182c3883adad79d8f1026851a68176"  # Zone ID for 1scan.uz
        
        # Clean device ID for subdomain
        if device_id:
            self.device_id = device_id.replace('-', '').replace('_', '').replace('.', '').lower()[:20]
        else:
            import uuid
            self.device_id = str(uuid.uuid4())[:8]
        
        self.tunnel_name = "agent-{}".format(self.device_id)
        self.subdomain = self.device_id
        self.domain = "1scan.uz"
        self.jupyter_url = "https://{}.{}".format(self.subdomain, self.domain)
        
        self.tunnel_id = None
        self.tunnel_credentials = None
        self.jupyter_process = None
        self.tunnel_process = None
    
    def get_zone_id(self):
        """Get Zone ID for 1scan.uz"""
        print("🔍 Getting Zone ID for {}...".format(self.domain))
        
        url = "https://api.cloudflare.com/client/v4/zones"
        headers = self._get_headers()
        params = {"name": self.domain}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["result"]:
                self.cf_zone_id = data["result"][0]["id"]
                print("✅ Zone ID: {}".format(self.cf_zone_id))
                return self.cf_zone_id
        
        print("❌ Could not get Zone ID")
        return None
    
    def _get_headers(self):
        """Get API headers for Global API Key"""
        return {
            "X-Auth-Email": self.cf_email,
            "X-Auth-Key": self.cf_api_key,
            "Content-Type": "application/json"
        }
    
    def get_or_create_tunnel(self):
        """Get existing tunnel or create a new one"""
        # First, check if tunnel already exists
        print("🔍 Checking for existing tunnel: {}...".format(self.tunnel_name))
        
        list_url = "https://api.cloudflare.com/client/v4/accounts/{}/cfd_tunnel".format(self.cf_account_id)
        headers = self._get_headers()
        
        # Check if tunnel exists
        response = requests.get(list_url, headers=headers)
        if response.status_code == 200:
            tunnels = response.json().get("result", [])
            for tunnel in tunnels:
                if tunnel["name"] == self.tunnel_name:
                    print("✅ Found existing tunnel: {}".format(tunnel["id"]))
                    self.tunnel_id = tunnel["id"]
                    
                    # For persistent device IDs, always recreate to ensure fresh state
                    print("🔄 Recreating tunnel for persistent device...")
                    delete_url = "https://api.cloudflare.com/client/v4/accounts/{}/cfd_tunnel/{}".format(
                        self.cf_account_id, tunnel["id"]
                    )
                    del_resp = requests.delete(delete_url, headers=headers)
                    if del_resp.status_code in [200, 204]:
                        print("✅ Deleted old tunnel")
                        time.sleep(2)
                    else:
                        print("⚠️  Could not delete old tunnel, trying to create new one anyway")
                    break
        
        # Create new tunnel
        return self.create_new_tunnel()
    
    def create_new_tunnel(self):
        """Create a brand new tunnel"""
        print("🔧 Creating new tunnel: {}...".format(self.tunnel_name))
        
        # Generate random tunnel secret (32 bytes)
        import secrets
        tunnel_secret = base64.b64encode(secrets.token_bytes(32)).decode()
        
        url = "https://api.cloudflare.com/client/v4/accounts/{}/cfd_tunnel".format(self.cf_account_id)
        headers = self._get_headers()
        
        data = {
            "name": self.tunnel_name,
            "tunnel_secret": tunnel_secret
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            result = response.json()["result"]
            self.tunnel_id = result["id"]
            
            # Create credentials JSON
            self.tunnel_credentials = {
                "AccountTag": self.cf_account_id,
                "TunnelSecret": tunnel_secret,
                "TunnelID": self.tunnel_id
            }
            
            # Save credentials to file with tunnel name (not ID) for consistency
            cred_file = "/tmp/tunnel-{}.json".format(self.tunnel_name)
            with open(cred_file, 'w') as f:
                json.dump(self.tunnel_credentials, f)
            
            print("✅ Tunnel created: {}".format(self.tunnel_id))
            return cred_file
        else:
            print("❌ Failed to create tunnel: {}".format(response.text[:200]))
            return None
    
    def create_dns_record(self):
        """Create DNS CNAME record"""
        if not self.tunnel_id:
            return False
        
        print("🔧 Creating DNS record: {}.{}...".format(self.subdomain, self.domain))
        
        # Get zone ID if we don't have it
        if self.cf_zone_id == "NEED_ZONE_ID_FOR_1SCAN_UZ":
            self.get_zone_id()
        
        url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(self.cf_zone_id)
        headers = self._get_headers()
        
        data = {
            "type": "CNAME",
            "name": self.subdomain,
            "content": "{}.cfargotunnel.com".format(self.tunnel_id),
            "proxied": True,
            "ttl": 1
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print("✅ DNS record created")
            return True
        elif "already exists" in response.text:
            print("⚠️  DNS record already exists")
            return True
        else:
            print("❌ Failed to create DNS: {}".format(response.text[:200]))
            return False
    
    def create_tunnel_config(self, cred_file):
        """Create tunnel config file"""
        config_file = "/tmp/tunnel-config-{}.yml".format(self.tunnel_name)
        with open(config_file, 'w') as f:
            f.write("tunnel: {}\n".format(self.tunnel_id))
            f.write("credentials-file: {}\n\n".format(cred_file))
            f.write("ingress:\n")
            f.write("  - hostname: {}.{}\n".format(self.subdomain, self.domain))
            f.write("    service: http://localhost:8888\n")
            f.write("  - service: http_status:404\n")
        
        return config_file
    
    def get_cloudflared_path(self):
        """Get or download cloudflared for any platform"""
        import shutil
        import platform
        
        # Check if already in system PATH
        if shutil.which("cloudflared"):
            return "cloudflared"
        
        # Determine binary location based on OS
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "windows":
            local_bin = os.path.expanduser("~/cloudflared/cloudflared.exe")
        else:
            local_bin = os.path.expanduser("~/.local/bin/cloudflared")
        
        # Check if already downloaded
        if os.path.exists(local_bin):
            return local_bin
        
        # Download based on platform
        print("📦 Downloading cloudflared for {}...".format(system))
        
        if system == "linux":
            # Linux: detect architecture
            if "arm" in machine or "aarch64" in machine:
                arch = "arm64"
            elif "386" in machine or "i686" in machine:
                arch = "386"
            else:
                arch = "amd64"
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{}".format(arch)
            
            os.makedirs(os.path.dirname(local_bin), exist_ok=True)
            subprocess.run("curl -L {} -o {}".format(url, local_bin), shell=True, capture_output=True)
            subprocess.run("chmod +x {}".format(local_bin), shell=True)
            
        elif system == "darwin":
            # macOS: supports both Intel and Apple Silicon
            if "arm" in machine:
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz"
            else:
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
            
            os.makedirs(os.path.dirname(local_bin), exist_ok=True)
            # Download and extract tar.gz
            subprocess.run("curl -L {} | tar xz -C {}".format(url, os.path.dirname(local_bin)), shell=True, capture_output=True)
            subprocess.run("chmod +x {}".format(local_bin), shell=True)
            
        elif system == "windows":
            # Windows: typically amd64
            if "arm" in machine:
                arch = "arm64"
            elif "386" in machine:
                arch = "386"
            else:
                arch = "amd64"
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-{}.exe".format(arch)
            
            os.makedirs(os.path.dirname(local_bin), exist_ok=True)
            # Use PowerShell on Windows to download
            subprocess.run("powershell -Command \"Invoke-WebRequest -Uri {} -OutFile {}\"".format(url, local_bin), shell=True, capture_output=True)
        
        else:
            print("❌ Unsupported platform: {}".format(system))
            raise Exception("Platform {} not supported".format(system))
        
        print("✅ cloudflared downloaded successfully")
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
            "--NotebookApp.password=''",
            "--NotebookApp.allow_origin='*'"

            
        ]
        
        self.jupyter_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        time.sleep(3)
        print("✅ Jupyter started")
        return True
    
    def start_tunnel(self, config_file):
        """Start tunnel with config"""
        print("🔧 Starting tunnel...")
        
        cloudflared = self.get_cloudflared_path()
        
        cmd = [
            cloudflared,
            "tunnel",
            "--config", config_file,
            "run"
        ]
        
        self.tunnel_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        time.sleep(5)
        print("✅ Tunnel running at {}".format(self.jupyter_url))
        return True
    
    def start(self):
        """Main entry point"""
        try:
            print("="*50)
            print("🌐 Persistent Tunnel with API")
            print("Device: {}".format(self.device_id))
            print("Target: {}.{}".format(self.subdomain, self.domain))
            print("="*50)
            
            # API credentials are hardcoded, so we're ready to go
            
            # 1. Get existing or create new tunnel via API
            cred_file = self.get_or_create_tunnel()
            if not cred_file:
                print("⚠️  Falling back to quick tunnel")
                return self.start_quick_tunnel()
            
            # 2. Create DNS record
            self.create_dns_record()
            
            # 3. Create config
            config_file = self.create_tunnel_config(cred_file)
            
            # 4. Start services
            self.start_jupyter()
            self.start_tunnel(config_file)
            
            print("\n" + "="*50)
            print("🎉 SUCCESS! Persistent URL created:")
            print("   {}".format(self.jupyter_url))
            print("   Tunnel ID: {}".format(self.tunnel_id))
            print("="*50)
            
            return True
            
        except Exception as e:
            print("❌ Error: {}".format(e))
            import traceback
            traceback.print_exc()
            self.stop()
            return False
    
    def start_quick_tunnel(self):
        """Fallback to quick tunnel"""
        print("🔧 Using quick tunnel (temporary URL)...")
        
        # Start Jupyter first
        self.start_jupyter()
        
        # Start quick tunnel
        cloudflared = self.get_cloudflared_path()
        cmd = [cloudflared, "tunnel", "--url", "http://localhost:8888"]
        
        self.tunnel_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        
        # Get URL from output
        for _ in range(30):
            line = self.tunnel_process.stdout.readline()
            if "trycloudflare.com" in line:
                import re
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    self.jupyter_url = match.group(0)
                    print("✅ Quick tunnel: {}".format(self.jupyter_url))
                    return True
            time.sleep(0.5)
        
        return False
    
    def stop(self):
        """Stop everything"""
        if self.jupyter_process:
            self.jupyter_process.terminate()
        if self.tunnel_process:
            self.tunnel_process.terminate()
        
        # Optionally delete tunnel when stopping
        if self.tunnel_id:
            try:
                url = "https://api.cloudflare.com/client/v4/accounts/{}/cfd_tunnel/{}".format(
                    self.cf_account_id, self.tunnel_id
                )
                requests.delete(url, headers=self._get_headers())
                print("🗑️  Tunnel deleted")
            except Exception:
                pass  # Ignore cleanup errors
    
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
    import platform
    import uuid
    
    hostname = platform.node().replace('.', '-')[:20]
    device_id = "{}-{}".format(hostname, str(uuid.uuid4())[:8])
    
    print("Device ID: {}".format(device_id))
    
    tunnel = PersistentTunnel(device_id=device_id)
    tunnel.run()


if __name__ == "__main__":
    main()