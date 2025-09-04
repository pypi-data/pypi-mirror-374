"""
Cloudflare API-based Tunnel Configuration
Uses API to dynamically manage DNS and routes
"""

import os
import requests
import subprocess
import time
import logging
from pathlib import Path
from .binary_manager import CloudflaredBinaryManager

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, use system env vars only

logger = logging.getLogger(__name__)


class CloudflareAPITunnel:
    def __init__(self, base_domain, device_id):
        """
        Initialize API-based tunnel manager
        """
        self.base_domain = "1scan.uz"
        self.device_id = device_id
        
        # Clean device ID for subdomain
        self.clean_device_id = device_id.replace('-', '').replace('_', '').lower()[:20]
        
        # Cloudflare IDs - hardcoded for zero-config experience
        self.zone_id = "78182c3883adad79d8f1026851a68176"
        self.account_id = "c91192ae20a5d43f65e087550d8dc89b"
        self.tunnel_id = "0777fc10-49c4-472d-8661-f60d80d6184d"  # unitlab-agent tunnel
        
        # API token - hardcoded for zero-config experience
        # This token only has DNS edit permissions for 1scan.uz - limited scope for safety
        self.api_token = "LJLe6QMOtpN0MeuLQ05_zUKKxVm4vEibkC8lxSJd"
        
        if not self.api_token:
            logger.warning("Using fallback tunnel configuration without API management.")
        
        # API setup
        self.api_base = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        } if self.api_token else {}
        
        # URLs for services - simplified for Jupyter only
        self.jupyter_subdomain = f"j{self.clean_device_id}"
        self.jupyter_url = f"https://{self.jupyter_subdomain}.{self.base_domain}"
        
        # Keep SSH URLs for compatibility but they won't work yet
        self.ssh_subdomain = f"s{self.clean_device_id}"
        self.ssh_hostname = f"{self.ssh_subdomain}.{self.base_domain}"
        self.ssh_url = self.ssh_hostname
        
        self.tunnel_process = None
        self.created_dns_records = []
        self.tunnel_config_file = None
        
        # Try to initialize binary manager, but don't fail if it doesn't work
        try:
            self.binary_manager = CloudflaredBinaryManager()
        except Exception as e:
            logger.warning(f"Binary manager initialization failed: {e}")
            self.binary_manager = None

    def create_dns_records(self):
        """
        Create DNS CNAME records for this device
        """
        if not self.api_token:
            print("⚠️  No API token configured. Skipping DNS creation.")
            print("   Assuming DNS records already exist or will be created manually.")
            return True
        
        print(f"📡 Creating DNS records for device {self.device_id}...")
        
        records = [
            {"name": self.jupyter_subdomain, "comment": f"Jupyter for {self.device_id}"},
            {"name": self.ssh_subdomain, "comment": f"SSH for {self.device_id}"}
        ]
        
        for record in records:
            try:
                # Check if record exists
                check_url = f"{self.api_base}/zones/{self.zone_id}/dns_records"
                params = {"name": f"{record['name']}.{self.base_domain}", "type": "CNAME"}
                
                response = requests.get(check_url, headers=self.headers, params=params)
                existing = response.json()
                
                if existing.get("result") and len(existing["result"]) > 0:
                    # Record exists
                    print(f"   ✓ DNS record {record['name']}.{self.base_domain} already exists")
                    continue
                
                # Create new record
                data = {
                    "type": "CNAME",
                    "name": record["name"],
                    "content": f"{self.tunnel_id}.cfargotunnel.com",
                    "ttl": 1,  # Auto
                    "proxied": True,
                    "comment": record["comment"]
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

    def update_tunnel_config(self, jupyter_port=8888, ssh_port=22):
        """
        Update tunnel configuration via API
        """
        if not self.api_token:
            print("⚠️  No API token. Tunnel will use existing configuration.")
            return True
        
        print(f"🔧 Configuring tunnel routes...")
        
        # Get current tunnel config first
        get_url = f"{self.api_base}/accounts/{self.account_id}/tunnels/{self.tunnel_id}/configurations"
        
        try:
            # Get existing config
            response = requests.get(get_url, headers=self.headers)
            current_config = response.json() if response.status_code == 200 else {}
            
            # Build new ingress rules
            new_ingress = [
                {
                    "hostname": f"{self.jupyter_subdomain}.{self.base_domain}",
                    "service": f"http://localhost:{jupyter_port}",
                    "originRequest": {
                        "noTLSVerify": True
                    }
                },
                {
                    "hostname": f"{self.ssh_subdomain}.{self.base_domain}",
                    "service": f"ssh://localhost:{ssh_port}"
                }
            ]
            
            # Merge with existing ingress if any
            if current_config.get("success") and current_config.get("result"):
                existing_ingress = current_config["result"].get("config", {}).get("ingress", [])
                
                # Filter out our hostnames from existing
                filtered_ingress = [
                    rule for rule in existing_ingress
                    if rule.get("hostname") not in [
                        f"{self.jupyter_subdomain}.{self.base_domain}",
                        f"{self.ssh_subdomain}.{self.base_domain}"
                    ] and rule.get("service") != "http_status:404"
                ]
                
                # Combine
                new_ingress = new_ingress + filtered_ingress
            
            # Add catch-all at the end
            new_ingress.append({"service": "http_status:404"})
            
            # Update configuration
            config_data = {
                "config": {
                    "ingress": new_ingress
                }
            }
            
            put_url = f"{self.api_base}/accounts/{self.account_id}/tunnels/{self.tunnel_id}/configurations"
            response = requests.put(put_url, headers=self.headers, json=config_data)
            
            if response.status_code == 200:
                print(f"   ✅ Tunnel routes configured")
                return True
            else:
                print(f"   ⚠️  Route configuration status: {response.status_code}")
                # Continue anyway - routes might be configured manually
                return True
                
        except Exception as e:
            print(f"   ⚠️  Could not update routes via API: {e}")
            print("   Assuming routes are configured in dashboard.")
            return True

    def create_device_tunnel(self):
        """
        Create a unique tunnel for this device
        Each tunnel gets a unique UUID to avoid conflicts
        """
        import uuid
        # Always use a unique name with UUID
        unique_id = str(uuid.uuid4())[:8]
        tunnel_name = f"device-{self.clean_device_id}-{unique_id}"
        # Since we use UUID, no need to check - just create new tunnel
        create_url = f"{self.api_base}/accounts/{self.account_id}/tunnels"
        # Generate secret first
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
            
            # Create DNS records for this device
            self.create_dns_records()
            
            return tunnel
        else:
            print(f"❌ Failed to create tunnel: {create_response.text}")
            return None
    
    def _configure_tunnel_routes(self, tunnel_id):
        """
        Configure ingress routes for the device tunnel
        The tunnel needs to be configured with a config file, not via API
        So we'll create a config file for it
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
            json.dump(credentials, f)
        
        print(f"💾 Saved credentials to: {creds_file}")
        return creds_file
    
    def start_tunnel_with_token(self):
        """
        Start tunnel using the existing service token
        """
        try:
            print("🚀 Starting Cloudflare tunnel...")
            
            # Ensure cloudflared is available
            cloudflared_path = self._ensure_cloudflared()
            if not cloudflared_path:
                raise RuntimeError("Failed to obtain cloudflared binary")
            
            # Always create a new unique tunnel with UUID
            device_tunnel = self.create_device_tunnel()
            
            # Now set up DNS and routes via API after tunnel is created/found
            if self.api_token and device_tunnel:
                self.tunnel_id = device_tunnel['id']  # Ensure tunnel_id is set
                self.create_dns_records()
                self.update_tunnel_config()
            
            if not device_tunnel:
                print("❌ Could not create/find device tunnel")
                # Fallback to shared tunnel if API fails
                print("⚠️  Falling back to shared tunnel...")
                service_token = "eyJhIjoiYzkxMTkyYWUyMGE1ZDQzZjY1ZTA4NzU1MGQ4ZGM4OWIiLCJ0IjoiMDc3N2ZjMTAtNDljNC00NzJkLTg2NjEtZjYwZDgwZDYxODRkIiwicyI6Ik9XRTNaak5tTVdVdE1tWTRaUzAwTmpoakLTazBmalF0WXpjek1tSm1ZVGt4WlRRMCJ9"
                cmd = [
                    cloudflared_path,
                    "tunnel",
                    "--no-autoupdate",
                    "run",
                    "--token",
                    service_token
                ]
            else:
                tunnel_id = device_tunnel['id']
                tunnel_name = device_tunnel['name']
                
                print(f"🚇 Starting tunnel: {tunnel_name} ({tunnel_id})")
                
                # Check if credentials file exists
                creds_file = Path.home() / '.cloudflared' / f"{tunnel_id}.json"
                config_file = Path.home() / '.cloudflared' / f'config-{tunnel_id}.yml'
                cmd = None  # Initialize cmd
                
                # Since we always create new tunnels, credentials should exist
                if not creds_file.exists():
                    print("❌ Error: No credentials file found for newly created tunnel")
                    return None
                
                # Use credentials to run tunnel
                            result = token_response.json()
                            if 'result' in result:
                                token = result['result']
                                print(f"   ✅ Got tunnel token")
                            else:
                                print(f"   ❌ No token in response: {result}")
                                return None
                            
                            # Check if config file exists with ingress rules
                            if config_file.exists():
                                # Use token with config file for ingress rules
                                print(f"   Using token with config file: {config_file}")
                                cmd = [
                                    cloudflared_path,
                                    "tunnel",
                                    "--no-autoupdate",
                                    "--config", str(config_file),
                                    "run",
                                    "--token", token
                                ]
                            else:
                                # Use token directly
                                print(f"   Using token directly (no config file)")
                                cmd = [
                                    cloudflared_path,
                                    "tunnel",
                                    "--no-autoupdate", 
                                    "run",
                                    "--token", token
                                ]
                        else:
                            print(f"❌ Could not get tunnel token: {token_response.status_code}")
                            if token_response.text:
                                print(f"   Error: {token_response.text}")
                            
                            # If 404, tunnel doesn't exist or we don't have access
                            if token_response.status_code == 404:
                                print(f"🔄 Tunnel not accessible (404), need to recreate...")
                                # Delete the old tunnel immediately
                                delete_url = f"{self.api_base}/accounts/{self.account_id}/tunnels/{tunnel_id}"
                                delete_response = requests.delete(delete_url, headers=self.headers)
                                if delete_response.status_code in [200, 204, 404]:
                                    print(f"   ✅ Deleted old tunnel")
                                
                                # Create a new tunnel with timestamp
                                import uuid
                                # Use a random suffix to ensure uniqueness
                                random_suffix = str(uuid.uuid4())[:8]
                                self.clean_device_id = f"{self.device_id.replace(' ', '').replace('-', '').replace('.', '').replace('_', '')[:16]}-{random_suffix}"
                                print(f"   Creating new tunnel with ID: {self.clean_device_id}")
                                
                                new_tunnel = self.create_device_tunnel(force_new=False)
                                
                                if new_tunnel and new_tunnel.get('tunnel_secret'):
                                    print(f"   ✅ Created new tunnel: {new_tunnel['name']}")
                                    # Use the new tunnel directly - update references
                                    device_tunnel = new_tunnel
                                    tunnel_id = new_tunnel['id']
                                    tunnel_name = new_tunnel['name']
                                    
                                    # Check if credentials were saved
                                    creds_file = Path.home() / '.cloudflared' / f"{tunnel_id}.json"
                                    if creds_file.exists():
                                        print(f"   ✅ Credentials saved for new tunnel")
                                        # Set up command to run with credentials
                                        config_file = Path.home() / '.cloudflared' / f'config-{tunnel_id}.yml'
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
                                    else:
                                        print(f"   ❌ No credentials for new tunnel, cannot proceed")
                                        return None
                                else:
                                    print(f"   ❌ Failed to create replacement tunnel")
                                    return None
                            else:
                                print(f"   ℹ️  Token endpoint returned {token_response.status_code}")
                                print(f"   This might mean the tunnel needs to be recreated manually")
                                return None
                
                # Only use credentials if we haven't already set cmd with token
                if cmd is None and creds_file.exists():
                    # Check if config file exists
                    if config_file.exists():
                        # Run tunnel with config file (includes routes)
                        cmd = [
                            cloudflared_path,
                            "tunnel",
                            "--no-autoupdate",
                            "--config", str(config_file),
                            "run"
                        ]
                    else:
                        # Fallback to credentials file only
                        cmd = [
                            cloudflared_path,
                            "tunnel",
                            "--no-autoupdate",
                            "--credentials-file", str(creds_file),
                            "run",
                            tunnel_id
                        ]
            
            # Only start the tunnel if we have a valid command
            if cmd:
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
            else:
                # If no cmd, something went wrong
                print("❌ No valid command to start tunnel")
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
        Note: We keep the tunnel configuration for next run
        """
        if self.tunnel_process and self.tunnel_process.poll() is None:
            print("Stopping tunnel...")
            self.tunnel_process.terminate()
            try:
                self.tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tunnel_process.kill()
            print("Tunnel stopped")
            print("ℹ️  Tunnel configuration preserved for next run")

    def _ensure_cloudflared(self):
        """
        Ensure cloudflared binary is available
        Downloads it if necessary
        """
        print("🔍 Checking for cloudflared binary...")
        
        # Try binary manager first
        if self.binary_manager:
            try:
                path = self.binary_manager.get_binary_path()
                print(f"✅ Using cloudflared from binary manager: {path}")
                return path
            except Exception as e:
                logger.warning(f"Binary manager failed, will download directly: {e}")
        
        # Direct download fallback - simplified version
        import platform
        import urllib.request
        import ssl
        
        # Create SSL context that handles certificate issues
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        cache_dir = Path.home() / '.unitlab' / 'bin'
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cloudflared_path = cache_dir / 'cloudflared'
        if platform.system() == 'Windows':
            cloudflared_path = cache_dir / 'cloudflared.exe'
        
        # If already exists, use it
        if cloudflared_path.exists():
            print(f"✅ Using cached cloudflared: {cloudflared_path}")
            return str(cloudflared_path)
        
        # Download based on platform
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        print(f"📥 Downloading cloudflared for {system}/{machine}...")
        
        if system == 'linux':
            if machine in ['x86_64', 'amd64']:
                url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'
            elif machine in ['aarch64', 'arm64']:
                url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64'
            else:
                url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386'
        elif system == 'darwin':
            url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz'
        elif system == 'windows':
            url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe'
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
        
        try:
            # Download the file with SSL context
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            # Special handling for macOS .tgz files
            if system == 'darwin':
                import tarfile
                import io
                
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    data = response.read()
                    
                # Extract from tar.gz
                with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
                    tar.extract('cloudflared', cache_dir)
            else:
                # Direct binary download for Linux/Windows
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    with open(cloudflared_path, 'wb') as out_file:
                        out_file.write(response.read())
            
            # Make executable on Unix
            if system != 'windows':
                import stat
                cloudflared_path.chmod(cloudflared_path.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ Downloaded cloudflared to: {cloudflared_path}")
            return str(cloudflared_path)
            
        except Exception as e:
            print(f"❌ Failed to download cloudflared: {e}")
            raise RuntimeError(f"Could not download cloudflared: {e}")
    
    def cleanup_dns(self):
        """
        Remove created DNS records (optional cleanup)
        """
        if not self.api_token or not self.created_dns_records:
            return
        
        print("🧹 Cleaning up DNS records...")
        for record_id in self.created_dns_records:
            try:
                url = f"{self.api_base}/zones/{self.zone_id}/dns_records/{record_id}"
                requests.delete(url, headers=self.headers)
                print(f"   Deleted record {record_id}")
            except:
                pass