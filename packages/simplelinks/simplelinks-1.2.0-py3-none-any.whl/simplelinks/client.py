"""
SimpleLinks Client Module

Provides high-level functions to join secure network connections
"""

import asyncio
import websockets
import json
import platform
import threading
import time
import logging
import signal
import os
import fcntl
import struct
import socket
from typing import Optional
from .utils import (
    get_machine_id, get_client_id, get_hostname, get_local_ip, get_public_ip,
    check_root_privileges, check_tun_support, validate_ip, validate_port
)

# Global client state
_client_instance = None
_client_task = None
_client_loop = None

# TUN device constants
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

class SimpleLinksClient:
    """SimpleLinks Network Client"""
    
    def __init__(self, host: str, port: int, server_secret: str, subnet: str = "default",
                 auto_reconnect: bool = True):
        self.host = host
        self.port = port
        self.server_secret = server_secret
        self.subnet = subnet
        self.auto_reconnect = auto_reconnect
        self.virtual_ip = None
        self.network = None
        self.session_id = None
        self.websocket = None
        self.running = False
        self.connected = False
        self.last_heartbeat = time.time()
        self.heartbeat_failed = False
        
        # Get system information
        self.client_id = get_client_id()  # New unique identifier based on IPs + hostname
        self.machine_id = get_machine_id()  # Keep for backward compatibility logging
        self.hostname = get_hostname()
        self.local_ip = get_local_ip()
        self.public_ip = None  # Will be fetched if possible
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("simplelinks.client")
        
        # Platform-specific settings
        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.has_tun = check_tun_support()
        self.has_root = check_root_privileges()
    
    async def register_with_server(self) -> bool:
        """Register with the server and get virtual IP assignment"""
        try:
            # Try to get public IP (optional, may fail)
            try:
                self.logger.info("Detecting public IP address...")
                self.public_ip = get_public_ip()
                if self.public_ip:
                    self.logger.info(f"Client public IP: {self.public_ip}")
                else:
                    self.logger.warning("Could not determine public IP address")
            except Exception as e:
                self.logger.warning(f"Public IP detection failed: {e}")
            
            registration_msg = {
                "type": "register",
                "machine_id": self.client_id,  # Use new client_id based on IPs + hostname
                "server_secret": self.server_secret,
                "subnet": self.subnet,
                "hostname": self.hostname,
                "private_ip": self.local_ip,
                "public_ip": self.public_ip
            }
            
            self.logger.info(f"Sending registration: {registration_msg}")
            await self.websocket.send(json.dumps(registration_msg))
            
            # Wait for registration response
            response_msg = await self.websocket.recv()
            self.logger.info(f"Received response: {response_msg}")
            response = json.loads(response_msg)
            self.logger.info(f"Parsed response: {response}")
            
            if response.get("success"):
                self.virtual_ip = response.get("virtual_ip")
                self.network = response.get("network")
                self.session_id = response.get("session_id")
                
                self.logger.info(f"Successfully registered with server")
                self.logger.info(f"Assigned virtual IP: {self.virtual_ip}")
                self.logger.info(f"Network: {self.network}")
                
                # Try to determine server's public IP
                try:
                    server_ip = socket.gethostbyname(self.host)
                    self.logger.info(f"Server public IP: {server_ip}")
                except Exception as e:
                    self.logger.debug(f"Could not resolve server IP: {e}")
                
                return True
            else:
                error = response.get("error", "Unknown error")
                code = response.get("code", 500)
                
                # Special handling for client limit errors
                if code == 403 and "Maximum client limit" in error:
                    self.logger.error(f"\n{'='*60}")
                    self.logger.error(f"SERVER FULL: Cannot join network")
                    self.logger.error(f"The server has reached its maximum capacity of 6 clients.")
                    self.logger.error(f"\nPossible solutions:")
                    self.logger.error(f"1. Wait for other clients to disconnect")
                    self.logger.error(f"2. Contact server administrator to increase capacity")
                    self.logger.error(f"3. Ask administrator to run 'server.reset()' to clear stale clients")
                    self.logger.error(f"{'='*60}")
                else:
                    self.logger.error(f"Registration failed ({code}): {error}")
                
                return False
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    async def setup_network_interface(self) -> bool:
        """Setup network interface (platform-specific)"""
        if not self.virtual_ip:
            return False
        
        try:
            if self.is_linux and self.has_tun and self.has_root:
                return await self.setup_linux_tun()
            elif self.is_macos:
                return await self.setup_macos_utun()
            else:
                self.logger.warning("Limited functionality: No TUN/TAP support or root privileges")
                self.logger.warning("Running in WebSocket-only mode (ping responses only)")
                return True  # Still allow connection for basic functionality
                
        except Exception as e:
            self.logger.error(f"Network interface setup failed: {e}")
            return False
    
    async def setup_linux_tun(self) -> bool:
        """Setup Linux TUN interface"""
        try:
            self.logger.info("Setting up Linux TUN interface...")
            
            # Clean up existing TUN device if any
            if hasattr(self, 'tun_fd') and self.tun_fd is not None:
                try:
                    os.close(self.tun_fd)
                except:
                    pass
                self.tun_fd = None
            
            # Remove existing interface if it exists
            try:
                os.system("ip link delete slink0 2>/dev/null")
            except:
                pass
            
            # Create TUN device
            self.tun_fd = os.open("/dev/net/tun", os.O_RDWR)
            ifr = struct.pack("16sH", b"slink0", IFF_TUN | IFF_NO_PI)
            ifname = fcntl.ioctl(self.tun_fd, TUNSETIFF, ifr)
            
            # Parse network to get netmask
            # Network format: "10.254.254.0/29"
            network_parts = self.network.split('/')
            prefix_len = int(network_parts[1]) if len(network_parts) > 1 else 24
            
            # Configure IP address
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, os.system, f"ip addr add {self.virtual_ip}/{prefix_len} dev slink0")
            await loop.run_in_executor(None, os.system, "ip link set slink0 up")
            
            self.logger.info(f"✓ Created TUN device slink0 with IP: {self.virtual_ip}/{prefix_len}")
            
            # Start TUN reader task
            asyncio.create_task(self.tun_reader())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create TUN device: {e}")
            return False
    
    async def setup_macos_utun(self) -> bool:
        """Setup macOS utun interface"""
        self.logger.info("Setting up macOS utun interface...")
        # This would import and use the existing macOS client logic
        # For now, return True as a placeholder
        return True
    
    def parse_ipv4_packet(self, data: bytes) -> Optional[str]:
        """Parse IPv4 packet and extract destination IP"""
        if len(data) < 20:
            return None
        
        try:
            # IPv4 header: destination IP is at bytes 16-19 (0-indexed)
            dst_ip_bytes = data[16:20]
            dst_ip = socket.inet_ntoa(dst_ip_bytes)
            return dst_ip
        except Exception:
            return None
    
    async def tun_reader(self):
        """Read packets from TUN interface and forward to server"""
        loop = asyncio.get_event_loop()
        while self.running and self.connected:
            try:
                # Read from TUN device
                data = await loop.run_in_executor(
                    None, 
                    lambda: os.read(self.tun_fd, 1500)  # MTU 1500
                )
                if not data:
                    break
                
                # Parse IPv4 packet to get destination IP
                target_ip = self.parse_ipv4_packet(data)
                if target_ip is None:
                    self.logger.debug("Failed to parse IPv4 packet, skipping")
                    continue
                
                # Only forward packets to VPN network (10.254.254.x)
                if not target_ip.startswith("10.254.254."):
                    self.logger.debug(f"Ignoring packet to {target_ip} (not in VPN network)")
                    continue
                
                # Forward packet to server
                await self.websocket.send(json.dumps({
                    "type": "packet",
                    "target_ip": target_ip,
                    "data": data.hex()
                }))
                
                self.logger.debug(f"Forwarded packet to {target_ip} ({len(data)} bytes)")
                
            except Exception as e:
                if self.running and self.connected:
                    # Only log errors if we should still be running
                    if "Bad file descriptor" not in str(e):
                        self.logger.error(f"TUN read error: {e}")
                break
    
    async def handle_server_messages(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'packet':
                        await self.handle_incoming_packet(data)
                    elif msg_type == 'heartbeat_response':
                        self.last_heartbeat = time.time()
                        self.heartbeat_failed = False
                        self.logger.debug("Heartbeat response received from server")
                    else:
                        self.logger.debug(f"Unknown message type: {msg_type}")
                        
                except json.JSONDecodeError:
                    self.logger.error("Invalid JSON received from server")
                except Exception as e:
                    self.logger.error(f"Message handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection to server closed")
            self.connected = False
        except Exception as e:
            self.logger.error(f"Server message handler error: {e}")
            self.connected = False
    
    async def handle_incoming_packet(self, data: dict):
        """Handle incoming packet from server"""
        try:
            source_ip = data.get('source_ip')
            packet_data = data.get('data')
            
            if not source_ip or not packet_data:
                return
            
            self.logger.debug(f"Received packet from {source_ip}")
            
            # For now, just log the packet
            # In a full implementation, this would:
            # 1. Decode the packet data
            # 2. Write it to the TUN interface (Linux)
            if hasattr(self, 'tun_fd') and self.tun_fd is not None:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: os.write(self.tun_fd, bytes.fromhex(packet_data))
                )
            # 3. Or handle it appropriately (macOS)
            
            # Simple ping response handling for demonstration
            if self.is_ping_request(packet_data):
                await self.send_ping_reply(source_ip, packet_data)
                
        except Exception as e:
            # Don't log errors for closed file descriptors during shutdown
            if self.running and self.connected and "Bad file descriptor" not in str(e):
                self.logger.error(f"Packet handling error: {e}")
    
    def is_ping_request(self, packet_data: str) -> bool:
        """Check if packet is an ICMP ping request"""
        try:
            # Simple check - in real implementation would parse packet properly
            return "icmp_type\":8" in packet_data.lower()
        except:
            return False
    
    async def send_ping_reply(self, target_ip: str, request_data: str):
        """Send ping reply packet"""
        try:
            # Create a simple ping reply
            # In real implementation, would craft proper ICMP reply
            reply_data = request_data.replace('"icmp_type":8', '"icmp_type":0')
            
            await self.websocket.send(json.dumps({
                "type": "packet",
                "target_ip": target_ip,
                "data": reply_data
            }))
            
            self.logger.debug(f"Sent ping reply to {target_ip}")
            
        except Exception as e:
            self.logger.error(f"Ping reply error: {e}")
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to server and monitor responses"""
        while self.connected and self.running:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                if self.websocket and self.connected:
                    self.logger.debug("Sending heartbeat to server")
                    await self.websocket.send(json.dumps({
                        "type": "heartbeat"
                    }))
                    
                    # Check if we've received a heartbeat response recently
                    if time.time() - self.last_heartbeat > 90:  # 3 missed heartbeats
                        self.logger.warning("No heartbeat response from server for 90 seconds, connection may be lost")
                        self.heartbeat_failed = True
                        self.connected = False
                        break
                        
            except (websockets.exceptions.ConnectionClosed, ConnectionResetError, BrokenPipeError) as e:
                self.logger.warning(f"Heartbeat failed - connection lost: {e}")
                self.connected = False
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                self.connected = False
                break
    
    async def connect_to_server(self) -> bool:
        """Connect to the secure server"""
        # Try both SSL and non-SSL connections
        protocols = ["wss", "ws"]  # Try SSL first
        
        for protocol in protocols:
            try:
                uri = f"{protocol}://{self.host}:{self.port}"
                self.logger.info(f"Connecting to {uri}...")
                
                # Show connection information
                self.logger.info(f"Client hostname: {self.hostname}")
                self.logger.info(f"Client private IP: {self.local_ip}")
                
                # Configure SSL context for wss connections
                ssl_context = None
                if protocol == "wss":
                    import ssl
                    ssl_context = ssl.create_default_context()
                    # For self-signed certificates or testing, you might need:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                self.websocket = await websockets.connect(
                    uri,
                    ssl=ssl_context,
                    ping_interval=30,
                    ping_timeout=10
                )
                
                self.connected = True
                self.logger.info(f"Connected to server using {protocol.upper()}")
                
                # Register with server
                if not await self.register_with_server():
                    return False
                
                # Setup network interface
                if not await self.setup_network_interface():
                    self.logger.warning("Network interface setup failed, continuing with limited functionality")
                
                # Reset heartbeat tracking
                self.last_heartbeat = time.time()
                self.heartbeat_failed = False
                
                # Start heartbeat
                asyncio.create_task(self.send_heartbeat())
                
                return True
                
            except Exception as e:
                self.logger.debug(f"Connection failed with {protocol}: {e}")
                if self.websocket:
                    try:
                        await self.websocket.close()
                    except:
                        pass
                    self.websocket = None
                self.connected = False
                
                # If this was the last protocol to try, log the error
                if protocol == protocols[-1]:
                    self.logger.error(f"Failed to connect with any protocol. Last error: {e}")
        
        return False
    
    async def start_client(self):
        """Start the network client and manage auto-reconnection"""
        self.running = True
        while self.running:
            self.logger.info("Starting client connection cycle...")
            try:
                if await self.connect_to_server():
                    self.logger.info("Client connection established, handling messages...")
                    await self.handle_server_messages()
                
            except Exception as e:
                self.logger.error(f"Client error in main loop: {e}")
            finally:
                await self.disconnect()
                self.logger.info("Client connection cycle ended.")

            if self.running and self.auto_reconnect:
                self.logger.info("Connection lost. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            elif not self.running:
                self.logger.info("Client shutdown complete.")
                break
            else:
                self.logger.info("Auto-reconnect disabled. Stopping client.")
                self.running = False
                break
    
    async def disconnect(self):
        """Disconnect from server (but keep running for auto-reconnect)"""
        self.connected = False
        
        # Close TUN device if open
        if hasattr(self, 'tun_fd') and self.tun_fd is not None:
            try:
                os.close(self.tun_fd)
                self.logger.debug("Closed TUN device")
            except Exception as e:
                self.logger.debug(f"TUN device close error: {e}")
            finally:
                self.tun_fd = None
        
        # Close websocket
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
            self.websocket = None
        
        self.logger.info("Disconnected from server")
    
    async def shutdown(self):
        """Completely shutdown the client (stops auto-reconnect)"""
        self.running = False
        await self.disconnect()
    
    def get_status(self) -> dict:
        """Get client status"""
        return {
            "connected": self.connected,
            "running": self.running,
            "virtual_ip": self.virtual_ip,
            "network": self.network,
            "server": f"{self.host}:{self.port}",
            "machine_id": self.machine_id,
            "hostname": self.hostname,
            "has_tun": self.has_tun,
            "has_root": self.has_root,
            "platform": platform.system()
        }


def join(host: str, secret: str, subnet: str = "default", port: int = 20001,
         auto_reconnect: bool = True) -> None:
    """
    Join SimpleLinks secure network
    
    Args:
        host: Server IP address or hostname
        secret: Server authentication secret (required)
        subnet: Subnet identifier for client grouping (default: "default")
        port: Server port (default: 20001)
    """
    global _client_instance, _client_task, _client_loop
    
    if not validate_ip(host) and not host.replace('.', '').replace('-', '').isalnum():
        raise ValueError(f"Invalid host: {host}")
    
    if not validate_port(port):
        raise ValueError(f"Invalid port: {port}")
    
    if not secret:
        raise ValueError("Server secret is required")
    
    if _client_instance and _client_instance.running:
        print(f"Client already running (connected to {_client_instance.host}:{_client_instance.port})")
        return
    
    _client_instance = SimpleLinksClient(host=host, port=port, server_secret=secret, subnet=subnet,
                                         auto_reconnect=auto_reconnect)
    
    def run_client():
        global _client_loop
        _client_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_client_loop)
        try:
            _client_loop.run_until_complete(_client_instance.start_client())
        except KeyboardInterrupt:
            pass
        finally:
            if _client_loop and not _client_loop.is_closed():
                _client_loop.close()
            _client_loop = None
    
    _client_task = threading.Thread(target=run_client, daemon=True)
    _client_task.start()
    
    # Wait a moment for client to connect
    time.sleep(2)
    
    if _client_instance and _client_instance.connected:
        # Try to resolve server IP
        try:
            server_public_ip = socket.gethostbyname(host)
        except:
            server_public_ip = "unknown"
        
        print(f"✓ Successfully joined secure network!")
        print(f"  Server: {host}:{port}")
        print(f"  Server public IP: {server_public_ip}")
        print(f"  Client public IP: {_client_instance.public_ip or 'unknown'}")
        print(f"  Client private IP: {_client_instance.local_ip or 'unknown'}")
        print(f"  Virtual IP: {_client_instance.virtual_ip}")
        print(f"  Network: {_client_instance.network}")
        print(f"  Subnet: {_client_instance.subnet}")
        print(f"  Machine ID: {_client_instance.machine_id}")
        print(f"  Hostname: {_client_instance.hostname}")
        
        if not _client_instance.has_root:
            print(f"  ⚠ Warning: Running without root privileges - limited functionality")
        
        if not _client_instance.has_tun:
            print(f"  ⚠ Warning: No TUN/TAP support detected - limited functionality")
        
        print()
        print("Client is running in the background. Use Ctrl+C to disconnect.")
    else:
        print("\n❌ Failed to connect to server")
        print("Please check:")
        print("  1. Server is running and accessible")
        print("  2. Correct host address and port")
        print("  3. Valid server secret")
        print("  4. Network connectivity")
        print("  5. Server capacity (maximum 6 clients)")
        
        _client_instance = None
        _client_task = None
        _client_loop = None


def disconnect() -> None:
    """Disconnect from secure network"""
    global _client_instance, _client_task, _client_loop
    
    if _client_instance:
        if _client_loop and not _client_loop.is_closed():
            try:
                # Schedule shutdown in the event loop (this stops auto-reconnect)
                future = asyncio.run_coroutine_threadsafe(_client_instance.shutdown(), _client_loop)
                # Wait for shutdown to complete
                future.result(timeout=5.0)
            except Exception as e:
                print(f"Warning: Disconnect cleanup error: {e}")
        print("Disconnected from secure network.")
    
    # Wait for thread to finish
    if _client_task and _client_task.is_alive():
        try:
            _client_task.join(timeout=3.0)
        except Exception:
            pass
    
    _client_instance = None
    _client_task = None
    _client_loop = None


def rejoin() -> None:
    """
    Rejoin secure network using previous connection parameters
    
    Disconnects from current server (if connected) and reconnects using
    the same host, secret, subnet, and port from the last join() call.
    """
    global _client_instance, _client_task, _client_loop
    
    if not _client_instance:
        print("❌ No previous connection found")
        print("Please use client.join() first to establish initial connection")
        return
    
    # Store previous connection parameters
    prev_host = _client_instance.host
    prev_port = _client_instance.port
    prev_secret = _client_instance.server_secret
    prev_subnet = _client_instance.subnet
    
    print(f"🔄 Rejoining network...")
    print(f"  Previous: {prev_host}:{prev_port} (subnet: {prev_subnet})")
    
    # Disconnect current connection
    disconnect()
    
    # Wait a moment for cleanup
    time.sleep(1)
    
    # Reconnect with same parameters
    try:
        join(host=prev_host, secret=prev_secret, subnet=prev_subnet, port=prev_port)
    except Exception as e:
        print(f"❌ Rejoin failed: {e}")
        print("You may need to use client.join() manually")


def status() -> dict:
    """Get client status"""
    global _client_instance
    
    if not _client_instance:
        return {"error": "Client not running"}
    
    return _client_instance.get_status()


def info() -> None:
    """Print client information"""
    global _client_instance
    
    if not _client_instance:
        print("Client: Not running")
        return
    
    client_status = status()
    
    print("=== SimpleLinks Client Status ===")
    print(f"Server: {client_status['server']}")
    print(f"Status: {'Connected' if client_status['connected'] else 'Disconnected'}")
    print(f"Virtual IP: {client_status.get('virtual_ip', 'Not assigned')}")
    print(f"Network: {client_status.get('network', 'Unknown')}")
    print(f"Hostname: {client_status['hostname']}")
    print(f"Platform: {client_status['platform']}")
    print(f"TUN Support: {'Yes' if client_status['has_tun'] else 'No'}")
    print(f"Root Privileges: {'Yes' if client_status['has_root'] else 'No'}")


# Handle Ctrl+C gracefully
def _signal_handler(signum, frame):
    print("\nDisconnecting from VPN...")
    disconnect()
    exit(0)

signal.signal(signal.SIGINT, _signal_handler)
