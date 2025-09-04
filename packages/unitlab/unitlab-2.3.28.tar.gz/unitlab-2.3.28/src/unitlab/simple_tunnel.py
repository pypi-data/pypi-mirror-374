#!/usr/bin/env python3
"""
Simple Cloudflare Tunnel for Jupyter - MVP Version
Uses hardcoded tunnel credentials
"""

import subprocess
from pathlib import Path
import time


class SimpleTunnel:
    def __init__(self, device_id=None):
        """
        Initialize SimpleTunnel with hardcoded everything
        device_id: Unique device identifier for subdomain generation
        """
        # Everything hardcoded for simplicity
        self.tunnel_uuid = "c6caf64a-7499-4aa5-8702-0d1870388114"
        self.domain = "1scan.uz"
        
        # Generate unique subdomain from device_id
        if device_id:
            # Clean device_id: remove special chars, lowercase, limit length
            clean_id = device_id.replace('-', '').replace('_', '').replace('.', '').lower()[:30]
            self.subdomain = clean_id
        else:
            # Fallback to a random subdomain if no device_id
            import uuid
            self.subdomain = str(uuid.uuid4())[:8]
        
        # The unique URL for this device
        self.jupyter_url = "https://{}.{}".format(self.subdomain, self.domain)
        
        self.jupyter_process = None
        self.tunnel_process = None
    
    def start_jupyter(self, port=8888):
        """Start Jupyter notebook server"""
        print("🚀 Starting Jupyter on port {}...".format(port))
        
        cmd = [
            "jupyter", "notebook",
            "--port", '8888',
            "--no-browser",
            "--ip", "0.0.0.0",
            "--ServerApp.token=''",
            "--ServerApp.password=''",
            "--ServerApp.allow_origin='*'"
        ]
        
        self.jupyter_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for Jupyter to start
        time.sleep(3)
        
        print("✅ Jupyter started on port {}".format(port))
        return True
    
    def get_cloudflared_path(self):
        """Get cloudflared binary, download if needed"""
        import os
        import platform
        
        # Check if cloudflared exists in system
        try:
            import shutil
            if shutil.which("cloudflared"):
                print("✅ Using system cloudflared")
                return "cloudflared"
        except:
            pass
        
        # Check local binary
        local_bin = os.path.expanduser("~/.local/bin/cloudflared")
        if os.path.exists(local_bin):
            print("✅ Using existing cloudflared from ~/.local/bin")
            return local_bin
        
        # Download it
        print("📦 Downloading cloudflared (this may take a moment)...")
        system = platform.system().lower()
        if system == "linux":
            arch = "amd64" if "x86" in platform.machine() else "arm64"
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{}".format(arch)
            
            os.makedirs(os.path.expanduser("~/.local/bin"), exist_ok=True)
            result = subprocess.run("curl -L {} -o {}".format(url, local_bin), shell=True, capture_output=True)
            if result.returncode == 0:
                subprocess.run("chmod +x {}".format(local_bin), shell=True)
                print("✅ cloudflared downloaded successfully")
                return local_bin
            else:
                print("❌ Failed to download cloudflared")
                raise Exception("Could not download cloudflared")
        
        raise Exception("Could not find or download cloudflared")
    
    def start_tunnel(self, local_port=8888):
        """Start cloudflared tunnel - simple and direct"""
        print("🔧 Starting Cloudflare tunnel...")
        
        # Get cloudflared (downloads if needed)
        try:
            cloudflared = self.get_cloudflared_path()
        except Exception as e:
            print("⚠️ Error getting cloudflared: {}".format(e))
            # Fallback - try to use system cloudflared anyway
            cloudflared = "cloudflared"
        
        # Simple command - just run the tunnel
        cmd = [
            cloudflared,
            "tunnel",
            "run",
            "--url", "http://127.0.0.1:{}".format(local_port),
            self.tunnel_uuid
        ]
        
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for tunnel to establish
        time.sleep(3)
        
        print("✅ Tunnel running at {}".format(self.jupyter_url))
    
    def start(self):
        """Start tunnel and Jupyter (non-blocking)"""
        try:
            print("="*50)
            print("🌐 Simple Cloudflare Tunnel for Jupyter - MVP") 
            print("="*50)
            
            # 1. Cloudflared should be installed on system
            
            # 2. Start Jupyter
            if not self.start_jupyter():
                raise Exception("Failed to start Jupyter")
            
            # 3. Start tunnel
            self.start_tunnel()
            
            # 4. Print access info
            print("\n" + "="*50)
            print("🎉 SUCCESS! Your Jupyter is now accessible at:")
            print("   {}".format(self.jupyter_url))
            print("   Device subdomain: {}".format(self.subdomain))
            print("="*50)
            
            return True
            
        except Exception as e:
            print("❌ Error: {}".format(e))
            self.stop()
            return False
    
    def stop(self):
        """Stop tunnel and Jupyter"""
        if self.jupyter_process:
            self.jupyter_process.terminate()
            self.jupyter_process = None
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process = None
    
    def run(self):
        """Main entry point for standalone use - sets up everything and blocks"""
        try:
            if self.start():
                # Keep running
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down...")
            self.stop()
            print("👋 Goodbye!")


def main():
    """Example usage with device ID"""
    
    # Generate a unique device ID (in real usage, this comes from main.py)
    import platform
    import uuid
    hostname = platform.node().replace('.', '-').replace(' ', '-')[:20]
    random_suffix = str(uuid.uuid4())[:8]
    device_id = "{}-{}".format(hostname, random_suffix)
    
    print("Device ID: {}".format(device_id))
    
    # Create tunnel with device ID for unique subdomain
    tunnel = SimpleTunnel(device_id=device_id)
    tunnel.run()


if __name__ == "__main__":
    main()