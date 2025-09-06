"""
SimpleLinks Server Module

Provides high-level functions to start and manage secure network servers
"""

import asyncio
import websockets
import json
import uuid
import time
import logging
import signal
import threading
import hashlib
import subprocess
import ssl
import os
from pathlib import Path
from typing import Dict, Set, Optional, List
from datetime import datetime
from .database import ClientDatabase
from .utils import validate_ip, validate_port, get_local_ip, get_hostname
from .rate_limiter import RateLimiter, RATE_PRESETS
from .web_api import SimpleLinksWebAPI

# Global server state
_server_instance = None
_server_task = None
_server_loop = None

class SimpleLinksServer:
    """SimpleLinks Network Server"""
    
    def __init__(self, port: int, server_secret: str = None, host: str = "0.0.0.0", 
                 ssl_cert: str = None, ssl_key: str = None, rate_limit: str = "512k"):
        self.host = host
        self.port = port
        # Server authentication secret - defaults to hostname md5
        if server_secret is None:
            hostname = get_hostname()
            self.server_secret = hashlib.md5(hostname.encode()).hexdigest()
        else:
            self.server_secret = server_secret
        
        self.clients = {}  # session_id -> websocket
        self.client_ips = {}  # virtual_ip -> session_id
        self.db = ClientDatabase()
        self.server = None
        self.running = False
        
        # Store server secret for web API access
        self.secret = self.server_secret
        
        # SSL certificate paths
        if ssl_cert is None:
            home_dir = Path.home()
            cert_dir = home_dir / ".simplelinks" / "certs"
            self.ssl_cert = str(cert_dir / "fullchain.pem")
        else:
            self.ssl_cert = ssl_cert
        
        if ssl_key is None:
            home_dir = Path.home()
            cert_dir = home_dir / ".simplelinks" / "certs"
            self.ssl_key = str(cert_dir / "privkey.pem")
        else:
            self.ssl_key = ssl_key
        
        # Setup rate limiter
        if rate_limit in RATE_PRESETS:
            rate_bps = RATE_PRESETS[rate_limit]
        else:
            # Try to parse as number (bytes per second)
            try:
                rate_bps = int(rate_limit)
            except ValueError:
                rate_bps = RATE_PRESETS["512k"]  # Default fallback
        
        self.rate_limiter = RateLimiter(default_rate_bps=rate_bps)
        
        # Web API server
        self.web_api = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("simplelinks.server")
    
    async def register_client(self, websocket, message: dict) -> dict:
        """Handle client registration with dual authentication"""
        try:
            self.logger.info(f"Registration request received: {message}")
            
            machine_id = message.get('machine_id')
            server_secret = message.get('server_secret')
            subnet = message.get('subnet')
            public_ip = message.get('public_ip')
            private_ip = message.get('private_ip')
            hostname = message.get('hostname')
            
            # Validate required fields
            if not machine_id:
                return {
                    "type": "registration_response",
                    "success": False,
                    "error": "Missing machine_id"
                }
            
            # First layer: Server authentication
            if not server_secret:
                return {
                    "type": "registration_response",
                    "success": False,
                    "error": "Missing server_secret"
                }
            
            # Debug logging for secret comparison
            self.logger.info(f"Secret validation: client='{server_secret}' server='{self.server_secret}' match={server_secret == self.server_secret}")
                
            if server_secret != self.server_secret:
                return {
                    "type": "registration_response", 
                    "success": False,
                    "error": "Invalid server_secret"
                }
            
            # Second layer: Subnet grouping (default to 'default' if not specified)
            if not subnet:
                subnet = 'default'
            
            session_id = str(uuid.uuid4())
            
            # Register with database using subnet for grouping
            # Handle None values defensively
            public_ip_safe = public_ip if public_ip else None
            private_ip_safe = private_ip if private_ip else None
            hostname_safe = hostname if hostname else None
            
            self.logger.info(f"Calling db.register_client with machine_id={machine_id}, secret={subnet}, public_ip={public_ip_safe}")
            result = self.db.register_client(
                machine_id=machine_id,
                secret=subnet,  # Use subnet as the grouping key
                public_ip=public_ip_safe,
                private_ip=private_ip_safe,
                hostname=hostname_safe,
                session_id=session_id
            )
            
            self.logger.info(f"Database registration result: {result}")
            
            if "error" in result:
                error_response = {
                    "type": "registration_response",
                    "success": False,
                    "error": result["error"],
                    "code": result.get("code", 500)
                }
                self.logger.info(f"Returning error response: {error_response}")
                return error_response
            
            # Store session
            self.clients[session_id] = websocket
            self.client_ips[result["virtual_ip"]] = session_id
            
            self.logger.info(f"Client registered: {hostname or machine_id} -> {result['virtual_ip']} (subnet: {subnet})")
            
            success_response = {
                "type": "registration_response",
                "success": True,
                "virtual_ip": result["virtual_ip"],
                "network": "10.254.254.0/29",
                "subnet": subnet,
                "session_id": session_id
            }
            
            self.logger.info(f"Returning success response: {success_response}")
            return success_response
            
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return {
                "type": "registration_response",
                "success": False,
                "error": "Internal server error"
            }
    
    async def handle_packet(self, websocket, message: dict):
        """Handle packet forwarding between clients with rate limiting"""
        try:
            session_id = None
            for sid, ws in self.clients.items():
                if ws == websocket:
                    session_id = sid
                    break
            
            if not session_id:
                return
            
            sender_client = self.db.get_client_by_session_id(session_id)
            if not sender_client:
                return
            
            target_ip = message.get('target_ip')
            packet_data = message.get('data')
            
            if not target_ip or not packet_data:
                return
            
            # Calculate packet size
            try:
                packet_bytes = len(bytes.fromhex(packet_data))
            except ValueError:
                self.logger.warning(f"Invalid packet data from {sender_client['virtual_ip']}")
                return
            
            # Check rate limit for sender
            sender_id = sender_client['virtual_ip']
            if not self.rate_limiter.can_send(sender_id, packet_bytes):
                # Packet rate limited
                self.logger.debug(f"Rate limited packet from {sender_id} ({packet_bytes} bytes)")
                return
            
            # Find target client
            target_client = self.db.get_client_by_virtual_ip(target_ip)
            if not target_client or not target_client.get('is_online'):
                self.logger.warning(f"TARGET NOT FOUND: {target_ip}")
                return
            
            target_session_id = target_client.get('session_id')
            target_websocket = self.clients.get(target_session_id)
            
            if target_websocket:
                try:
                    await target_websocket.send(json.dumps({
                        "type": "packet",
                        "source_ip": sender_client['virtual_ip'],
                        "data": packet_data
                    }))
                    self.logger.debug(f"Forwarded packet: {sender_id} -> {target_ip} ({packet_bytes} bytes)")
                except websockets.exceptions.ConnectionClosed:
                    # Clean up disconnected client
                    await self.cleanup_client(target_session_id)
                    
        except Exception as e:
            self.logger.error(f"Packet handling error: {e}")
    
    def get_client_ip(self, websocket):
        """Get client IP address from websocket connection"""
        try:
            return websocket.remote_address[0] if websocket.remote_address else "unknown"
        except:
            return "unknown"
    
    def log_security_event(self, event_type: str, client_ip: str, details: str = ""):
        """Log security-related events with timestamp and IP"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.warning(f"[SECURITY] {timestamp} - {event_type} from {client_ip}: {details}")
    
    async def handle_client(self, websocket, path):
        """Handle individual client connection"""
        session_id = None
        client_ip = self.get_client_ip(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'register':
                        response = await self.register_client(websocket, data)
                        if response.get('success'):
                            session_id = response.get('session_id')
                        await websocket.send(json.dumps(response))
                    
                    elif msg_type == 'packet':
                        await self.handle_packet(websocket, data)
                    
                    elif msg_type == 'heartbeat':
                        # Update last seen timestamp
                        if session_id:
                            client = self.db.get_client_by_session_id(session_id)
                            if client:
                                # Just update the last_seen timestamp without full registration
                                self.db.update_client_heartbeat(session_id)
                                self.logger.debug(f"Heartbeat from client {client.get('hostname', 'unknown')} ({client_ip})")
                            else:
                                self.log_security_event("INVALID_HEARTBEAT", client_ip, "session not found")
                        else:
                            self.log_security_event("HEARTBEAT_NO_SESSION", client_ip, "no active session")
                        
                        await websocket.send(json.dumps({
                            "type": "heartbeat_response"
                        }))
                    
                    else:
                        # Unknown message type - could be scanning attempt
                        self.log_security_event("UNKNOWN_MESSAGE_TYPE", client_ip, f"type: {msg_type}")
                        
                except json.JSONDecodeError as e:
                    self.log_security_event("INVALID_JSON", client_ip, f"malformed data: {str(e)[:100]}")
                except KeyError as e:
                    self.log_security_event("MISSING_FIELD", client_ip, f"missing key: {e}")
                except Exception as e:
                    self.log_security_event("MESSAGE_ERROR", client_ip, f"error: {str(e)[:100]}")
                    
        except websockets.exceptions.ConnectionClosed:
            if session_id:
                self.logger.info(f"Client {client_ip} disconnected normally")
            else:
                self.log_security_event("PREMATURE_DISCONNECT", client_ip, "connection closed without registration")
        except websockets.exceptions.InvalidMessage as e:
            self.log_security_event("INVALID_WEBSOCKET", client_ip, f"invalid websocket message: {str(e)[:100]}")
        except Exception as e:
            self.log_security_event("CLIENT_HANDLER_ERROR", client_ip, f"unexpected error: {str(e)[:100]}")
        finally:
            if session_id:
                await self.cleanup_client(session_id)
    
    async def cleanup_client(self, session_id: str):
        """Clean up disconnected client"""
        try:
            if session_id in self.clients:
                client = self.db.get_client_by_session_id(session_id)
                if client:
                    self.client_ips.pop(client['virtual_ip'], None)
                    # Remove from rate limiter
                    self.rate_limiter.remove_client(client['virtual_ip'])
                    self.logger.info(f"Client disconnected: {client.get('hostname', 'unknown')}")
                
                del self.clients[session_id]
                self.db.set_client_offline(session_id=session_id)
                
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    async def start_server(self):
        """Start the secure server"""
        try:
            self.logger.info(f"Starting SimpleLinks server on {self.host}:{self.port}")
            
            # Setup SSL context if certificates exist
            ssl_context = None
            if os.path.exists(self.ssl_cert) and os.path.exists(self.ssl_key):
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(self.ssl_cert, self.ssl_key)
                self.logger.info(f"SSL certificates loaded from {self.ssl_cert}")
            else:
                self.logger.warning(f"SSL certificates not found at {self.ssl_cert}, {self.ssl_key}")
                self.logger.warning("Server will run without SSL encryption (not recommended for production)")
            
            self.server = await websockets.serve(
                self.handle_client, 
                self.host, 
                self.port,
                ssl=ssl_context,
                ping_interval=30,
                ping_timeout=10
            )
            self.running = True
            self.logger.info(f"Server started successfully on {self.host}:{self.port}")
            
            # Periodic cleanup of stale clients
            asyncio.create_task(self.periodic_cleanup())
            
            await self.server.wait_closed()
            
        except Exception as e:
            self.logger.error(f"Server start error: {e}")
            raise
    
    async def periodic_cleanup(self):
        """Periodically clean up stale clients"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Run every minute
                self.db.cleanup_stale_clients(timeout_seconds=300)  # 5 minutes timeout
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
    
    def start_web_api(self):
        """Start the Web API server"""
        # Always recreate the web API instance to ensure correct configuration
        self.web_api = SimpleLinksWebAPI(
            server_instance=self,
            host='0.0.0.0',  # Allow all IPs
            ssl_cert=self.ssl_cert,
            ssl_key=self.ssl_key
        )
        
        if not self.web_api.running:
            try:
                self.web_api.start()
                protocol = "https" if self.web_api.use_ssl else "http"
                self.logger.info(f"Web API started on {protocol}://{self.web_api.host}:{self.web_api.port}")
            except Exception as e:
                self.logger.error(f"Failed to start Web API: {e}")
    
    def stop_web_api(self):
        """Stop the Web API server"""
        if self.web_api and self.web_api.running:
            self.web_api.stop()
            self.logger.info("Web API stopped")
    
    def stop_server(self):
        """Stop the server"""
        # Stop Web API first
        self.stop_web_api()
        
        if self.server:
            self.running = False
            self.server.close()
    
    def get_info(self) -> dict:
        """Get server information"""
        config = self.db.get_network_config()
        rate_stats = self.rate_limiter.get_all_stats()
        
        # Check SSL status
        ssl_enabled = (os.path.exists(self.ssl_cert) and os.path.exists(self.ssl_key))
        protocol = "wss" if ssl_enabled else "ws"
        
        # Get local IP for display
        local_ip = get_local_ip()
        
        return {
            "host": self.host,
            "port": self.port,
            "network": config.get('network_base', '10.254.254.0/29'),
            "max_clients": int(config.get('max_clients', '6')),
            "connected_clients": len(self.clients),
            "running": self.running,
            "protocol": protocol,
            "listening_on": f"{protocol}://{self.host}:{self.port}",
            "local_access": f"{protocol}://{local_ip}:{self.port}" if local_ip and self.host in ["0.0.0.0", "::"] else None,
            "server_secret": self.server_secret,
            "database": "~/.simplelinks/clients.db",
            "ssl": {
                "enabled": ssl_enabled,
                "cert_path": self.ssl_cert if ssl_enabled else None
            },
            "rate_limiting": {
                "enabled": rate_stats['enabled'],
                "default_rate_kbps": rate_stats['default_rate_kbps'],
                "active_clients": rate_stats['active_clients']
            }
        }
    
    def get_web_info(self) -> dict:
        """Get filtered server information for web API (excludes sensitive data)"""
        config = self.db.get_network_config()
        rate_stats = self.rate_limiter.get_all_stats()
        
        # Check SSL status
        ssl_enabled = (os.path.exists(self.ssl_cert) and os.path.exists(self.ssl_key))
        protocol = "wss" if ssl_enabled else "ws"
        
        return {
            "host": self.host,
            "port": self.port,
            "network": config.get('network_base', '10.254.254.0/29'),
            "max_clients": int(config.get('max_clients', '6')),
            "connected_clients": len(self.clients),
            "running": self.running,
            "protocol": protocol,
            "listening_on": f"{protocol}://{self.host}:{self.port}",
            "ssl": {
                "enabled": ssl_enabled
            },
            "rate_limiting": {
                "enabled": rate_stats['enabled'],
                "default_rate_kbps": rate_stats['default_rate_kbps'],
                "active_clients": rate_stats['active_clients']
            }
        }
    
    def list_clients(self) -> List[dict]:
        """List all registered clients"""
        return self.db.list_clients()


def start(port: int = 20001, secret: str = None, host: str = "0.0.0.0", 
          ssl_cert: str = None, ssl_key: str = None, rate_limit: str = "512k") -> None:
    """
    Start SimpleLinks server
    
    Args:
        port: Port to listen on (default: 20001)
        secret: Server authentication secret (defaults to hostname MD5)
        host: Host to bind to (default: "0.0.0.0")
        ssl_cert: Path to SSL certificate file (default: ~/.simplelinks/certs/fullchain.pem)
        ssl_key: Path to SSL private key file (default: ~/.simplelinks/certs/privkey.pem)
        rate_limit: Rate limit per client (default: "512k", options: "128k", "256k", "512k", "1m", "2m", "5m", "10m")
    """
    global _server_instance, _server_task, _server_loop
    
    # Show version info
    from . import __version__
    print(f"🚀 Starting SimpleLinks Server v{__version__}")
    
    if not validate_port(port):
        raise ValueError(f"Invalid port number: {port}")
    
    if _server_instance and _server_instance.running:
        print(f"Server already running on port {_server_instance.port}")
        return
    
    _server_instance = SimpleLinksServer(port=port, server_secret=secret, host=host, 
                                         ssl_cert=ssl_cert, ssl_key=ssl_key, rate_limit=rate_limit)
    
    def run_server():
        global _server_loop
        _server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_server_loop)
        try:
            _server_loop.run_until_complete(_server_instance.start_server())
        except KeyboardInterrupt:
            pass
        finally:
            if _server_loop and not _server_loop.is_closed():
                _server_loop.close()
    
    _server_task = threading.Thread(target=run_server, daemon=True)
    _server_task.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    
    if _server_instance.running:
        local_ip = get_local_ip()
        # Check if SSL is enabled
        ssl_enabled = (os.path.exists(_server_instance.ssl_cert) and 
                      os.path.exists(_server_instance.ssl_key))
        protocol = "wss" if ssl_enabled else "ws"
        
        print(f"✓ SimpleLinks server started successfully!")
        print(f"  Listening on: {protocol}://{host}:{port}")
        if local_ip and host in ["0.0.0.0", "::"]:
            print(f"  Local access: {protocol}://{local_ip}:{port}")
        print(f"  Network: 10.254.254.0/29 (max 6 clients)")
        print(f"  Server Secret: {_server_instance.server_secret}")
        print(f"  Database: ~/.simplelinks/clients.db")
        print(f"  Rate Limit: {_server_instance.rate_limiter.default_rate / 1024:.0f} KB/s per client")
        if ssl_enabled:
            print(f"  SSL: Enabled ({_server_instance.ssl_cert})")
        else:
            print(f"  SSL: Disabled (certificates not found)")
        print()
        print("Server is running in the background. Use Ctrl+C to stop.")
    else:
        raise RuntimeError("Failed to start server")


def stop() -> None:
    """Stop the running server"""
    global _server_instance, _server_task, _server_loop
    
    if _server_instance:
        _server_instance.stop_server()
        print("Server stopped.")
        
    # Wait for thread to finish
    if _server_task and _server_task.is_alive():
        try:
            _server_task.join(timeout=5.0)
        except Exception:
            pass
        
    if _server_loop and not _server_loop.is_closed():
        try:
            _server_loop.call_soon_threadsafe(_server_loop.stop)
        except Exception:
            pass
    
    _server_instance = None
    _server_task = None
    _server_loop = None


def info() -> dict:
    """Get server information"""
    global _server_instance
    
    if not _server_instance:
        return {"error": "Server not running"}
    
    return _server_instance.get_info()


def list_clients() -> List[dict]:
    """List all registered clients"""
    global _server_instance
    
    if not _server_instance:
        return []
    
    return _server_instance.list_clients()


def traffic() -> dict:
    """Get traffic statistics from server"""
    global _server_instance
    
    if not _server_instance or not _server_instance.running:
        return {"error": "Server not running"}
    
    try:
        return _server_instance.rate_limiter.get_all_stats()
    except Exception as e:
        return {"error": str(e)}


def reset() -> bool:
    """Reset server database - clear all client bindings and records"""
    global _server_instance
    
    if not _server_instance:
        # Create a temporary database connection to reset even if server isn't running
        from .database import ClientDatabase
        temp_db = ClientDatabase()
        result = temp_db.reset_database()
        temp_db.close()
        print("✓ Database reset completed (server was not running)")
        return result
    
    try:
        # Clear active connections
        _server_instance.clients.clear()
        _server_instance.client_ips.clear()
        
        # Clear rate limiter data
        _server_instance.rate_limiter.client_buckets.clear()
        
        # Reset database
        result = _server_instance.db.reset_database()
        
        if result:
            print("✓ Server reset completed - all client data cleared")
            print("  - Active connections terminated")
            print("  - Database records cleared")
            print("  - Rate limiter data cleared")
        else:
            print("✗ Server reset failed")
        
        return result
        
    except Exception as e:
        print(f"✗ Server reset error: {e}")
        return False


def restart() -> None:
    """Restart the server with same configuration"""
    global _server_instance
    
    if not _server_instance:
        print("❌ No running server to restart")
        print("Use server.start() to start a new server")
        return
    
    # Store current configuration
    prev_port = _server_instance.port
    prev_secret = _server_instance.server_secret
    prev_host = _server_instance.host
    prev_ssl_cert = _server_instance.ssl_cert
    prev_ssl_key = _server_instance.ssl_key
    prev_rate_limit = str(int(_server_instance.rate_limiter.default_rate))
    
    print(f"🔄 Restarting server on {prev_host}:{prev_port}...")
    
    # Stop current server
    stop()
    
    # Wait a moment for cleanup
    time.sleep(1)
    
    # Start with same configuration
    try:
        start(port=prev_port, secret=prev_secret, host=prev_host, 
              ssl_cert=prev_ssl_cert, ssl_key=prev_ssl_key, rate_limit=prev_rate_limit)
        print("✓ Server restart completed")
    except Exception as e:
        print(f"❌ Server restart failed: {e}")
        print("You may need to use server.start() manually")


def status() -> None:
    """Print server status"""
    global _server_instance
    
    if not _server_instance or not _server_instance.running:
        print("Server: Not running")
        return
    
    server_info = info()
    clients = list_clients()
    
    print("=== SimpleLinks Server Status ===")
    print(f"Host: {server_info['host']}:{server_info['port']}")
    print(f"Network: {server_info['network']}")
    print(f"Connected: {server_info['connected_clients']}/{server_info['max_clients']}")
    print()
    
    if clients:
        print("Registered Clients:")
        print(f"{'Virtual IP':<12} {'Hostname':<20} {'Status':<8} {'Last Seen'}")
        print("-" * 60)
        
        for client in clients:
            status_str = "Online" if client['is_online'] else "Offline"
            last_seen = time.strftime("%H:%M:%S", time.localtime(client['last_seen']))
            hostname = client.get('hostname', 'Unknown')[:19]
            
            print(f"{client['virtual_ip']:<12} {hostname:<20} {status_str:<8} {last_seen}")
    else:
        print("No registered clients.")


def start_web_api() -> None:
    """Start the Web API server"""
    global _server_instance
    
    if not _server_instance or not _server_instance.running:
        print("❌ Main server not running - start server first")
        return
    
    if _server_instance.web_api and _server_instance.web_api.running:
        print("Web API already running")
        api_port = _server_instance.web_api.port
        protocol = "https" if _server_instance.web_api.use_ssl else "http"
        host = _server_instance.web_api.host
        print(f"  Status page: {protocol}://{host}:{api_port}/status.html")
        print(f"  API endpoints: {protocol}://{host}:{api_port}/api/status")
        return
    
    try:
        _server_instance.start_web_api()
        if _server_instance.web_api and _server_instance.web_api.running:
            api_port = _server_instance.web_api.port
            protocol = "https" if _server_instance.web_api.use_ssl else "http"
            host = _server_instance.web_api.host
            print("✓ Web API started successfully!")
            print(f"  Status page: {protocol}://{host}:{api_port}/status.html")
            print(f"  API endpoints (require access code in header):")
            print(f"    - POST {protocol}://{host}:{api_port}/api/status")
            print(f"    - POST {protocol}://{host}:{api_port}/api/clients")
            print(f"    - POST {protocol}://{host}:{api_port}/api/info")
            print(f"  SSL: {'Enabled' if _server_instance.web_api.use_ssl else 'Disabled'}")
            print(f"  Access code: {_server_instance.server_secret}")
        else:
            print("❌ Failed to start Web API")
    except Exception as e:
        print(f"❌ Web API start error: {e}")


def stop_web_api() -> None:
    """Stop the Web API server"""
    global _server_instance
    
    if not _server_instance:
        print("Server not running")
        return
    
    if not (_server_instance.web_api and _server_instance.web_api.running):
        print("Web API not running")
        return
    
    try:
        _server_instance.stop_web_api()
        print("✓ Web API stopped")
    except Exception as e:
        print(f"❌ Web API stop error: {e}")


def web_status() -> None:
    """Get Web API status and URLs"""
    global _server_instance
    
    if not _server_instance or not _server_instance.running:
        print("Main server: Not running")
        return
    
    if not _server_instance.web_api:
        print("Web API: Not initialized")
        return
    
    if _server_instance.web_api.running:
        api_port = _server_instance.web_api.port
        print("=== Web API Status ===")
        print(f"Status: Running on port {api_port}")
        print(f"Available URLs:")
        for url in _server_instance.web_api.get_urls():
            print(f"  - {url}")
    else:
        print("Web API: Stopped")


# Handle Ctrl+C gracefully
def _signal_handler(signum, frame):
    print("\nShutting down server...")
    stop()
    exit(0)

signal.signal(signal.SIGINT, _signal_handler)
