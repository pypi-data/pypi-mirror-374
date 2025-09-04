#!/usr/bin/env python3
"""
Easiest Dynamic Tunnel - Each device gets its own tunnel at deviceid.1scan.uz
Using Cloudflare API with service token
"""

import subprocess
import time
import os
import requests
import json

class EasyTunnel:
    def __init__(self, device_id=None):
        """Initialize with device ID"""
        # Generate clean device ID
        if device_id:
            self.device_id = device_id.replace('-', '').replace('_', '').replace('.', '').lower()[:20]
        else:
            import uuid
            self.device_id = str(uuid.uuid4())[:8]
        
        self.subdomain = self.device_id
        self.jupyter_url = "https://{}.1scan.uz".format(self.subdomain)
        
        # Processes
        self.jupyter_process = None
        self.tunnel_process = None
        
        # We'll use service tokens (created per tunnel)
        self.tunnel_token = None
    
    def get_cloudflared_path(self):
        """Get or download cloudflared binary"""
        import shutil
        if shutil.which("cloudflared"):
            return "cloudflared"
        
        local_bin = os.path.expanduser("~/.local/bin/cloudflared")
        if os.path.exists(local_bin):
            return local_bin
        
        # Download it
        print("📦 Downloading cloudflared...")
        import platform
        system = platform.system().lower()
        if system == "linux":
            arch = "amd64" if "x86" in platform.machine() else "arm64"
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{}".format(arch)
            
            os.makedirs(os.path.dirname(local_bin), exist_ok=True)
            subprocess.run("curl -L {} -o {}".format(url, local_bin), shell=True, capture_output=True)
            subprocess.run("chmod +x {}".format(local_bin), shell=True)
            print("✅ cloudflared downloaded")
            return local_bin
        
        return "cloudflared"
    
    def create_quick_tunnel(self):
        """Use Cloudflare Quick Tunnel - no auth needed, but random URL"""
        print("🔧 Creating quick tunnel (no auth needed)...")
        
        cloudflared = self.get_cloudflared_path()
        
        # Quick tunnel command - generates random URL
        cmd = [
            cloudflared,
            "tunnel",
            "--url", "http://localhost:8888",
            "--no-tls-verify",
            "--metrics", "localhost:0"  # Disable metrics
        ]
        
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read output to get URL
        print("⏳ Getting tunnel URL...")
        for i in range(30):
            line = self.tunnel_process.stdout.readline()
            if line and "trycloudflare.com" in line:
                # Extract URL from output
                import re
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    self.jupyter_url = match.group(0)
                    print("✅ Quick tunnel URL: {}".format(self.jupyter_url))
                    return True
            time.sleep(0.5)
        
        return False
    
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
    
    def start(self):
        """Start everything - super simple"""
        try:
            print("="*50)
            print("🌐 Easy Dynamic Tunnel")
            print("Device ID: {}".format(self.device_id))
            print("="*50)
            
            # 1. Start Jupyter
            if not self.start_jupyter():
                raise Exception("Failed to start Jupyter")
            
            # 2. Create tunnel (quick tunnel for now)
            if not self.create_quick_tunnel():
                raise Exception("Failed to create tunnel")
            
            print("\n" + "="*50)
            print("🎉 SUCCESS! Your Jupyter is accessible at:")
            print("   {}".format(self.jupyter_url))
            print("="*50)
            print("\n📝 Note: For persistent URLs at {}.1scan.uz,".format(self.subdomain))
            print("   we need Cloudflare API integration")
            
            return True
            
        except Exception as e:
            print("❌ Error: {}".format(e))
            self.stop()
            return False
    
    def stop(self):
        """Stop everything"""
        if self.jupyter_process:
            self.jupyter_process.terminate()
            self.jupyter_process = None
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process = None
    
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
            print("👋 Goodbye!")


# For integration with existing client.py
class EasyTunnelAdapter:
    """Adapter to make EasyTunnel work with existing client.py interface"""
    def __init__(self, device_id):
        self.tunnel = EasyTunnel(device_id)
        self.jupyter_process = None
        self.tunnel_process = None
        self.jupyter_url = None
    
    def start(self):
        """Start method compatible with client.py"""
        if self.tunnel.start():
            self.jupyter_process = self.tunnel.jupyter_process
            self.tunnel_process = self.tunnel.tunnel_process
            self.jupyter_url = self.tunnel.jupyter_url
            return True
        return False
    
    def stop(self):
        """Stop method compatible with client.py"""
        self.tunnel.stop()


def main():
    """Test the easy tunnel"""
    import platform
    import uuid
    
    hostname = platform.node().replace('.', '-')[:20]
    device_id = "{}-{}".format(hostname, str(uuid.uuid4())[:8])
    
    tunnel = EasyTunnel(device_id=device_id)
    tunnel.run()


if __name__ == "__main__":
    main()