"""
Cloudflare API-based Tunnel Configuration
Uses API to dynamically manage DNS and routes
SIMPLIFIED VERSION with unique tunnel names
"""

import os
import requests
import subprocess
import time
import logging
import uuid
from pathlib import Path
from .binary_manager import CloudflaredBinaryManager

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

class CloudflareAPITunnel:
    def __init__(self, device_id, base_domain="1scan.uz"):
        """
        Initialize Cloudflare tunnel with API configuration
        Each device gets a unique tunnel with UUID
        """
        self.device_id = device_id
        self.base_domain = base_domain
        
        # Clean device ID for use in hostnames (remove special chars)
        self.clean_device_id = device_id.replace(' ', '').replace('-', '').replace('.', '').replace('_', '')[:24]
        
        # Subdomains for this device (j for jupyter, s for ssh)
        self.jupyter_subdomain = f"j{self.clean_device_id}"
        self.ssh_subdomain = f"s{self.clean_device_id}"
        
        # URLs for access
        self.jupyter_url = f"https://{self.jupyter_subdomain}.{base_domain}"
        self.ssh_hostname = f"{self.ssh_subdomain}.{base_domain}"
        self.ssh_url = self.ssh_hostname  # Backward compatibility
        
        # Hardcoded Cloudflare credentials
        self.account_id = "c91192ae20a5d43f65e087550d8dc89b"
        self.api_token = "LJLe6QMOtpN0MeuLQ05_zUKKxVm4vEibkC8lxSJd"
        self.zone_id = "f17ca0e9cf056e87afb019c88f936ac9"
        
        # API configuration
        self.api_base = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Track created resources for cleanup
        self.tunnel_id = None
        self.tunnel_process = None
        self.created_dns_records = []
        self.tunnel_config_file = None
        
        # Binary manager for cloudflared
        self.binary_manager = CloudflaredBinaryManager()
    
    def create_dns_records(self):
        """
        Create DNS records pointing to the tunnel
        """
        if not self.api_token or not self.tunnel_id:
            print("⚠️  Cannot create DNS records without API token and tunnel ID")
            return False
            
        print(f"📡 Creating DNS records for device {self.device_id}...")
        
        dns_records = [
            {"name": self.jupyter_subdomain, "content": f"{self.tunnel_id}.cfargotunnel.com"},
            {"name": self.ssh_subdomain, "content": f"{self.tunnel_id}.cfargotunnel.com"}
        ]
        
        for record in dns_records:
            try:
                # Check if record exists
                check_url = f"{self.api_base}/zones/{self.zone_id}/dns_records"
                check_params = {"name": f"{record['name']}.{self.base_domain}", "type": "CNAME"}
                check_response = requests.get(check_url, headers=self.headers, params=check_params)
                
                if check_response.status_code == 200:
                    existing = check_response.json().get('result', [])
                    if existing:
                        print(f"   ✓ DNS record {record['name']}.{self.base_domain} already exists")
                        continue
                
                # Create new record
                data = {
                    "type": "CNAME",
                    "name": record['name'],
                    "content": record['content'],
                    "ttl": 1,
                    "proxied": True
                }
                
                response = requests.post(check_url, headers=self.headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"   ✅ Created DNS: {record['name']}.{self.base_domain}")
                        self.created_dns_records.append(result["result"]["id"])
                    else:
                        print(f"   ⚠️  Failed to create {record['name']}: {result.get('errors')}")
                else:
                    print(f"   ❌ HTTP error {response.status_code} for {record['name']}")
                    
            except Exception as e:
                print(f"   ❌ Error creating DNS record: {e}")
                continue
        
        return True
    
    def create_device_tunnel(self):
        """
        Create a unique tunnel for this device
        Each tunnel gets a unique UUID to avoid conflicts
        """
        # Always use a unique name with UUID
        unique_id = str(uuid.uuid4())[:8]
        tunnel_name = f"device-{self.clean_device_id}-{unique_id}"
        
        # Update clean_device_id to include UUID for DNS records
        self.clean_device_id_with_uuid = f"{self.clean_device_id}{unique_id}"
        
        # Update subdomains with UUID
        self.jupyter_subdomain = f"j{self.clean_device_id_with_uuid}"
        self.ssh_subdomain = f"s{self.clean_device_id_with_uuid}"
        
        # Update URLs with new subdomains
        self.jupyter_url = f"https://{self.jupyter_subdomain}.{self.base_domain}"
        self.ssh_hostname = f"{self.ssh_subdomain}.{self.base_domain}"
        self.ssh_url = self.ssh_hostname  # Backward compatibility
        
        print(f"📦 Creating new tunnel: {tunnel_name}")
        
        create_url = f"{self.api_base}/accounts/{self.account_id}/tunnels"
        
        # Generate secret
        tunnel_secret = os.urandom(32).hex()
        
        create_data = {
            "name": tunnel_name,
            "tunnel_secret": tunnel_secret
        }
        
        create_response = requests.post(create_url, headers=self.headers, json=create_data)
        
        if create_response.status_code in [200, 201]:
            tunnel = create_response.json()['result']
            print(f"✅ Created tunnel: {tunnel_name}")
            
            # Add the secret to the tunnel info (API doesn't return it)
            tunnel['tunnel_secret'] = tunnel_secret
            
            # Save credentials for this tunnel
            self._save_tunnel_credentials(tunnel)
            
            # Configure tunnel routes
            self._configure_tunnel_routes(tunnel['id'])
            
            # Store tunnel ID for DNS creation
            self.tunnel_id = tunnel['id']
            
            # Create DNS records for this device
            self.create_dns_records()
            
            return tunnel
        else:
            print(f"❌ Failed to create tunnel: {create_response.text}")
            return None
    
    def _configure_tunnel_routes(self, tunnel_id):
        """
        Configure ingress routes for the device tunnel
        Creates a config file for cloudflared
        """
        import yaml
        
        # Create config file for this tunnel
        config_dir = Path.home() / '.cloudflared'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / f'config-{tunnel_id}.yml'
        
        config = {
            "tunnel": tunnel_id,
            "credentials-file": str(config_dir / f"{tunnel_id}.json"),
            "ingress": [
                {
                    "hostname": f"{self.jupyter_subdomain}.{self.base_domain}",
                    "service": "http://localhost:8888",
                    "originRequest": {
                        "noTLSVerify": True
                    }
                },
                {
                    "hostname": f"{self.ssh_subdomain}.{self.base_domain}",
                    "service": "ssh://localhost:22"
                },
                {
                    "service": "http_status:404"
                }
            ]
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        print(f"✅ Created tunnel config: {config_file}")
        self.tunnel_config_file = config_file
    
    def _save_tunnel_credentials(self, tunnel_info):
        """
        Save tunnel credentials locally for this device
        Credentials must be base64 encoded for cloudflared
        """
        import base64
        import json
        
        creds_dir = Path.home() / '.cloudflared'
        creds_dir.mkdir(exist_ok=True)
        
        creds_file = creds_dir / f"{tunnel_info['id']}.json"
        
        # Get the secret - it should be hex string
        secret_hex = tunnel_info.get('tunnel_secret') or tunnel_info.get('secret')
        if secret_hex:
            # Convert hex to bytes then to base64
            secret_bytes = bytes.fromhex(secret_hex)
            secret_b64 = base64.b64encode(secret_bytes).decode('ascii')
        else:
            print("⚠️  No tunnel secret found")
            return None
        
        credentials = {
            "AccountTag": self.account_id,
            "TunnelSecret": secret_b64,  # Must be base64!
            "TunnelID": tunnel_info['id']
        }
        
        with open(creds_file, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"✅ Saved tunnel credentials: {creds_file}")
        return creds_file
    
    def start_tunnel_with_token(self):
        """
        Start tunnel using API-created tunnel with UUID
        """
        try:
            print("🚀 Starting Cloudflare tunnel...")
            
            # Ensure cloudflared is available
            cloudflared_path = self._ensure_cloudflared()
            if not cloudflared_path:
                raise RuntimeError("Failed to obtain cloudflared binary")
            
            # Create a new unique tunnel
            device_tunnel = self.create_device_tunnel()
            
            if not device_tunnel:
                print("❌ Could not create device tunnel")
                return None
            
            tunnel_id = device_tunnel['id']
            tunnel_name = device_tunnel['name']
            
            print(f"🚇 Starting tunnel: {tunnel_name} ({tunnel_id})")
            
            # Check credentials file exists
            creds_file = Path.home() / '.cloudflared' / f"{tunnel_id}.json"
            config_file = Path.home() / '.cloudflared' / f'config-{tunnel_id}.yml'
            
            if not creds_file.exists():
                print("❌ Error: No credentials file found for newly created tunnel")
                return None
            
            # Use config file if it exists, otherwise use credentials file
            if config_file.exists():
                cmd = [
                    cloudflared_path,
                    "tunnel",
                    "--no-autoupdate",
                    "--config", str(config_file),
                    "run"
                ]
            else:
                cmd = [
                    cloudflared_path,
                    "tunnel",
                    "--no-autoupdate",
                    "--credentials-file", str(creds_file),
                    "run",
                    tunnel_id
                ]
            
            # Start tunnel process
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            print("⏳ Waiting for tunnel to connect...")
            time.sleep(5)
            
            if self.tunnel_process.poll() is None:
                print("✅ Tunnel is running!")
                print(f"📌 Device ID: {self.clean_device_id}")
                print(f"📌 Jupyter URL: {self.jupyter_url}")
                print(f"📌 SSH hostname: {self.ssh_hostname}")
                print(f"📌 SSH command: ssh -o ProxyCommand='cloudflared access ssh --hostname {self.ssh_hostname}' user@localhost")
                return self.tunnel_process
            else:
                output = self.tunnel_process.stdout.read() if self.tunnel_process.stdout else ""
                print(f"❌ Tunnel failed to start: {output}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting tunnel: {e}")
            return None
    
    def setup(self, jupyter_port=8888):
        """
        Setup and start tunnel (maintains compatibility)
        """
        return self.start_tunnel_with_token()
    
    def stop(self):
        """
        Stop the tunnel if running
        """
        if self.tunnel_process and self.tunnel_process.poll() is None:
            print("Stopping tunnel...")
            self.tunnel_process.terminate()
            try:
                self.tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tunnel_process.kill()
            print("Tunnel stopped")
    
    def _ensure_cloudflared(self):
        """
        Ensure cloudflared binary is available
        """
        print("🔍 Checking for cloudflared binary...")
        
        # Try binary manager first
        if self.binary_manager:
            try:
                path = self.binary_manager.get_binary_path()
                print(f"✅ Using cloudflared from binary manager: {path}")
                return path
            except Exception as e:
                print(f"⚠️  Binary manager failed: {e}")
        
        # Fallback to system cloudflared
        try:
            result = subprocess.run(['which', 'cloudflared'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"✅ Found system cloudflared: {path}")
                return path
        except:
            pass
        
        print("❌ cloudflared not found")
        return None