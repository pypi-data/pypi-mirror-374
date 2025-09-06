"""
Utility functions for SimpleLinks SDK
"""

import os
import platform
import socket
import subprocess
import hashlib
import uuid
from typing import Optional


def get_machine_id() -> str:
    """
    Get unique machine identifier for this system
    Falls back through multiple methods to ensure we get a stable ID
    
    DEPRECATED: Use get_client_id() instead for better uniqueness
    """
    machine_id = None
    
    # Try /etc/machine-id (Linux)
    if os.path.exists('/etc/machine-id'):
        try:
            with open('/etc/machine-id', 'r') as f:
                machine_id = f.read().strip()
        except:
            pass
    
    # Try /var/lib/dbus/machine-id (Linux)
    if not machine_id and os.path.exists('/var/lib/dbus/machine-id'):
        try:
            with open('/var/lib/dbus/machine-id', 'r') as f:
                machine_id = f.read().strip()
        except:
            pass
    
    # Try macOS hardware UUID
    if not machine_id and platform.system() == 'Darwin':
        try:
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType'], 
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Hardware UUID' in line:
                    machine_id = line.split(':')[-1].strip()
                    break
        except:
            pass
    
    # Try Windows machine GUID
    if not machine_id and platform.system() == 'Windows':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Cryptography") as key:
                machine_id = winreg.QueryValueEx(key, "MachineGuid")[0]
        except:
            pass
    
    # Fallback: Generate from hostname + MAC address
    if not machine_id:
        try:
            hostname = socket.gethostname()
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                           for i in range(0, 48, 8)][::-1])
            machine_id = hashlib.sha256(f"{hostname}:{mac}".encode()).hexdigest()[:32]
        except:
            pass
    
    # Final fallback: Generate random UUID
    if not machine_id:
        machine_id = str(uuid.uuid4()).replace('-', '')
    
    return machine_id


def get_client_id() -> str:
    """
    Get unique client identifier based on public_ip + private_ip + hostname
    This approach provides better uniqueness and avoids VM cloning issues
    
    Returns:
        MD5 hash of "public_ip|private_ip|hostname" combination
    """
    try:
        # Get components
        public_ip = get_public_ip() or "unknown_public"
        private_ip = get_local_ip() or "unknown_private"
        hostname = get_hostname() or "unknown_host"
        
        # Create composite identifier
        composite = f"{public_ip}|{private_ip}|{hostname}"
        
        # Generate MD5 hash for global uniqueness
        client_id = hashlib.md5(composite.encode()).hexdigest()
        
        return client_id
        
    except Exception as e:
        # Fallback to old machine_id method if something fails
        print(f"Warning: get_client_id failed ({e}), falling back to machine_id")
        return get_machine_id()


def get_hostname() -> str:
    """Get system hostname"""
    try:
        return socket.gethostname()
    except:
        return "unknown"


def get_local_ip() -> Optional[str]:
    """Get local/private IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except:
        return None


def get_public_ip() -> Optional[str]:
    """
    Get public IP address using devnull.cn service
    Note: This requires internet connection and external service
    """
    import urllib.request
    import json
    
    # Try primary service: devnull.cn
    try:
        with urllib.request.urlopen('https://devnull.cn/ip', timeout=5) as response:
            data = json.loads(response.read().decode())
            return data.get('origin')
    except Exception as e:
        pass
    
    # Fallback to ipify.org if primary fails
    try:
        with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5) as response:
            data = json.loads(response.read().decode())
            return data.get('ip')
    except Exception as e:
        pass
    
    return None


def check_root_privileges() -> bool:
    """Check if running with root privileges"""
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False


def check_tun_support() -> bool:
    """Check if TUN/TAP interfaces are supported"""
    if platform.system() == 'Linux':
        return os.path.exists('/dev/net/tun')
    elif platform.system() == 'Darwin':
        # Check for utun interfaces or TunTap kernel extension
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            return 'utun' in result.stdout or os.path.exists('/dev/tap0')
        except:
            return False
    return False


def validate_ip(ip: str) -> bool:
    """Validate IP address format"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_port(port: int) -> bool:
    """Validate port number"""
    return 1 <= port <= 65535
