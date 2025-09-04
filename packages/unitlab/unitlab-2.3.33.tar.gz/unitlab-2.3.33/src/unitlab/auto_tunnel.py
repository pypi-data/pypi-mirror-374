#!/usr/bin/env python3
"""
Automatic Tunnel Creation - Simplest approach using cloudflared's built-in quick tunnel
No API tokens needed!
"""

import subprocess
import time
import re
import os

class AutoTunnel:
    def __init__(self, device_id=None):
        """
        Initialize auto tunnel - no credentials needed!
        """
        self.device_id = device_id or "device"
        self.jupyter_process = None
        self.tunnel_process = None
        self.tunnel_url = None
        
    def get_cloudflared_path(self):
        """Get or download cloudflared binary"""
        import platform
        
        # Check if exists in system
        import shutil
        if shutil.which("cloudflared"):
            return "cloudflared"
        
        # Check local
        local_bin = os.path.expanduser("~/.local/bin/cloudflared")
        if os.path.exists(local_bin):
            return local_bin
        
        # Download it
        print("📦 Downloading cloudflared...")
        system = platform.system().lower()
        if system == "linux":
            arch = "amd64" if "x86" in platform.machine() else "arm64"
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{}".format(arch)
            
            os.makedirs(os.path.expanduser("~/.local/bin"), exist_ok=True)
            subprocess.run("curl -L {} -o {}".format(url, local_bin), shell=True, capture_output=True)
            subprocess.run("chmod +x {}".format(local_bin), shell=True)
            print("✅ cloudflared downloaded")
            return local_bin
        
        return "cloudflared"
    
    def start_jupyter(self):
        """Start Jupyter notebook"""
        print("🚀 Starting Jupyter on port 8888...")
        
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
        print("✅ Jupyter started")
        return True
    
    def start_tunnel(self):
        """Start tunnel using cloudflared quick tunnel - no auth needed!"""
        print("🔧 Starting automatic tunnel (no credentials needed)...")
        
        cloudflared = self.get_cloudflared_path()
        
        # Use cloudflared's quick tunnel feature - generates random URL
        cmd = [
            cloudflared,
            "tunnel",
            "--url", "http://localhost:8888"
        ]
        
        self.tunnel_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Read output to get the tunnel URL
        print("⏳ Waiting for tunnel URL...")
        for _ in range(30):  # Wait up to 30 seconds
            line = self.tunnel_process.stdout.readline()
            if line:
                # Look for the tunnel URL in output
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    self.tunnel_url = match.group(0)
                    print("✅ Tunnel created: {}".format(self.tunnel_url))
                    return True
            time.sleep(1)
        
        print("❌ Failed to get tunnel URL")
        return False
    
    def start(self):
        """Start everything - super simple!"""
        try:
            print("="*50)
            print("🌐 Automatic Cloudflare Tunnel (No Auth Needed!)")
            print("Device: {}".format(self.device_id))
            print("="*50)
            
            # 1. Start Jupyter
            if not self.start_jupyter():
                raise Exception("Failed to start Jupyter")
            
            # 2. Start tunnel (automatic, no credentials)
            if not self.start_tunnel():
                raise Exception("Failed to start tunnel")
            
            print("\n" + "="*50)
            print("🎉 SUCCESS! Your Jupyter is accessible at:")
            print("   {}".format(self.tunnel_url))
            print("="*50)
            print("\n⚠️  Note: This URL is temporary and random")
            print("For persistent URLs, use Cloudflare API approach")
            
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
            print("👋 Goodbye!")


def main():
    """Test automatic tunnel"""
    import platform
    device_id = platform.node()
    
    print("Starting auto tunnel for: {}".format(device_id))
    
    tunnel = AutoTunnel(device_id=device_id)
    tunnel.run()


if __name__ == "__main__":
    main()