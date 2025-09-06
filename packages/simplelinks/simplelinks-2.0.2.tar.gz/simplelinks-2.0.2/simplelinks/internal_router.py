"""
SimpleLinks Internal Network Router v2.0

Provides intelligent routing to optimize local network traffic by bypassing
central server when clients are on the same internal network.
"""

import asyncio
import socket
import json
import time
import logging
import ipaddress
import subprocess
import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PeerInfo:
    """Internal peer information"""
    virtual_ip: str
    private_ip: str
    hostname: str
    last_seen: float = 0
    is_reachable: bool = False
    failed_attempts: int = 0


class NetworkConnectivityTester:
    """Test network connectivity between peers"""
    
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self.logger = logging.getLogger("simplelinks.connectivity")
    
    async def test_connectivity(self, target_ip: str) -> bool:
        """Test if target IP is reachable via internal network"""
        
        # Method 1: ICMP ping test
        if await self._ping_test(target_ip):
            return True
        
        # Method 2: TCP connection test on common ports
        common_ports = [22, 80, 443, 8080]
        for port in common_ports:
            if await self._tcp_test(target_ip, port):
                return True
        
        # Method 3: UDP connectivity test
        if await self._udp_test(target_ip):
            return True
        
        return False
    
    async def _ping_test(self, target_ip: str) -> bool:
        """Test connectivity using ICMP ping"""
        try:
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', '2000', target_ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return_code = await process.wait()
            return return_code == 0
        except Exception:
            return False
    
    async def _tcp_test(self, target_ip: str, port: int) -> bool:
        """Test TCP connectivity"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target_ip, port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
    
    async def _udp_test(self, target_ip: str, port: int = 53) -> bool:
        """Test UDP connectivity"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.sendto(b"PROBE", (target_ip, port))
            return True
        except socket.timeout:
            return False
        except socket.error as e:
            # Network unreachable
            if e.errno == 113:
                return False
            return True  # Other errors may still indicate reachability
        except Exception:
            return False


class InternalRouter:
    """Intelligent internal network router"""
    
    def __init__(self, direct_comm_port: int = 20099):
        self.direct_comm_port = direct_comm_port
        self.internal_peers: Dict[str, PeerInfo] = {}
        self.external_peers: Dict[str, PeerInfo] = {}
        self.connectivity_tester = NetworkConnectivityTester()
        self.direct_socket = None
        self.running = False
        
        # Statistics
        self.stats = {
            'internal_packets_sent': 0,
            'internal_packets_received': 0,
            'server_packets_sent': 0,
            'internal_failures': 0,
            'route_discoveries': 0
        }
        
        self.logger = logging.getLogger("simplelinks.internal_router")
    
    async def initialize_peer_routes(self, all_peers: List[Dict]) -> None:
        """Initialize routing table by testing connectivity to all peers"""
        
        self.logger.info(f"🔍 Discovering internal network routes for {len(all_peers)} peers...")
        
        for peer_data in all_peers:
            virtual_ip = peer_data['virtual_ip']
            private_ip = peer_data.get('private_ip')
            hostname = peer_data.get('hostname', 'unknown')
            
            if not private_ip or virtual_ip == getattr(self, 'local_virtual_ip', None):
                continue
            
            peer = PeerInfo(
                virtual_ip=virtual_ip,
                private_ip=private_ip,
                hostname=hostname,
                last_seen=time.time()
            )
            
            # Test internal connectivity
            self.logger.debug(f"Testing connectivity to {hostname} ({private_ip})")
            
            is_reachable = await self.connectivity_tester.test_connectivity(private_ip)
            peer.is_reachable = is_reachable
            
            if is_reachable:
                self.internal_peers[virtual_ip] = peer
                self.logger.info(f"✅ Internal route: {virtual_ip} → {private_ip} ({hostname})")
            else:
                self.external_peers[virtual_ip] = peer
                self.logger.debug(f"🌐 Server route: {virtual_ip} ({hostname})")
        
        internal_count = len(self.internal_peers)
        external_count = len(self.external_peers)
        self.stats['route_discoveries'] += 1
        
        self.logger.info(f"📊 Route discovery complete: {internal_count} internal, {external_count} external")
    
    def should_use_internal_route(self, target_virtual_ip: str) -> bool:
        """Determine if internal routing should be used"""
        peer = self.internal_peers.get(target_virtual_ip)
        if not peer:
            return False
        
        # Skip if too many recent failures
        if peer.failed_attempts >= 3:
            if time.time() - peer.last_seen < 300:  # 5 minutes cooldown
                return False
        
        return peer.is_reachable
    
    async def send_via_internal(self, target_virtual_ip: str, packet_data: str) -> bool:
        """Send packet via internal network"""
        peer = self.internal_peers.get(target_virtual_ip)
        if not peer:
            return False
        
        try:
            # Create internal protocol packet
            internal_packet = {
                'protocol': 'simplelinks_v2_internal',
                'version': '2.0',
                'source_virtual_ip': getattr(self, 'local_virtual_ip', 'unknown'),
                'target_virtual_ip': target_virtual_ip,
                'packet_data': packet_data,
                'timestamp': time.time()
            }
            
            # Serialize and send via UDP
            packet_bytes = json.dumps(internal_packet).encode('utf-8')
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3.0)
            sock.sendto(packet_bytes, (peer.private_ip, self.direct_comm_port))
            sock.close()
            
            # Update statistics
            self.stats['internal_packets_sent'] += 1
            peer.last_seen = time.time()
            peer.failed_attempts = 0  # Reset failure counter on success
            
            self.logger.debug(f"📡 Internal packet sent: {target_virtual_ip} via {peer.private_ip}")
            return True
            
        except Exception as e:
            self.logger.debug(f"Internal send failed to {target_virtual_ip}: {e}")
            
            # Mark as failed and potentially move to external routing
            peer.failed_attempts += 1
            self.stats['internal_failures'] += 1
            
            if peer.failed_attempts >= 3:
                self.logger.warning(f"Moving {target_virtual_ip} to external routing due to failures")
                self.external_peers[target_virtual_ip] = peer
                del self.internal_peers[target_virtual_ip]
            
            return False
    
    async def start_internal_listener(self) -> None:
        """Start listening for internal network packets"""
        try:
            self.direct_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.direct_socket.bind(('0.0.0.0', self.direct_comm_port))
            self.direct_socket.setblocking(False)
            self.running = True
            
            self.logger.info(f"📡 Internal communication listener started on port {self.direct_comm_port}")
            
            while self.running:
                try:
                    data, addr = await asyncio.get_event_loop().sock_recvfrom(
                        self.direct_socket, 4096
                    )
                    
                    await self._handle_internal_packet(data, addr)
                    
                except Exception as e:
                    if self.running:
                        self.logger.debug(f"Internal listener error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to start internal listener: {e}")
    
    async def _handle_internal_packet(self, data: bytes, sender_addr: Tuple) -> None:
        """Handle received internal network packet"""
        try:
            # Parse packet
            packet = json.loads(data.decode('utf-8'))
            
            # Validate packet structure
            if not self._validate_internal_packet(packet, sender_addr):
                return
            
            # Extract packet data and inject into TUN interface
            packet_data = packet['packet_data']
            source_virtual_ip = packet['source_virtual_ip']
            
            # This will be called from the main client instance
            if hasattr(self, 'packet_handler') and self.packet_handler:
                await self.packet_handler(packet_data)
            
            # Update statistics
            self.stats['internal_packets_received'] += 1
            
            self.logger.debug(f"📡 Internal packet received from {source_virtual_ip}")
            
        except Exception as e:
            self.logger.debug(f"Error handling internal packet: {e}")
    
    def _validate_internal_packet(self, packet: Dict, sender_addr: Tuple) -> bool:
        """Validate received internal packet"""
        try:
            # Check required fields
            required_fields = ['protocol', 'version', 'source_virtual_ip', 
                             'target_virtual_ip', 'packet_data', 'timestamp']
            
            for field in required_fields:
                if field not in packet:
                    self.logger.warning(f"Invalid packet: missing {field}")
                    return False
            
            # Check protocol and version
            if packet['protocol'] != 'simplelinks_v2_internal':
                return False
            
            if packet['version'] != '2.0':
                return False
            
            # Check timestamp (reject packets older than 30 seconds)
            age = time.time() - packet['timestamp']
            if age > 30 or age < -5:  # Allow small clock skew
                self.logger.debug(f"Packet too old or from future: {age}s")
                return False
            
            # Verify sender IP matches expected peer
            source_virtual = packet['source_virtual_ip']
            if source_virtual in self.internal_peers:
                expected_ip = self.internal_peers[source_virtual].private_ip
                if sender_addr[0] != expected_ip:
                    self.logger.warning(f"IP mismatch: expected {expected_ip}, got {sender_addr[0]}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Packet validation error: {e}")
            return False
    
    async def periodic_route_optimization(self) -> None:
        """Periodically optimize routing table"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Re-test failed external routes
                failed_peers = list(self.external_peers.keys())
                recovered_count = 0
                
                for virtual_ip in failed_peers:
                    peer = self.external_peers[virtual_ip]
                    
                    # Re-test connectivity
                    is_reachable = await self.connectivity_tester.test_connectivity(peer.private_ip)
                    
                    if is_reachable:
                        # Move back to internal routing
                        peer.is_reachable = True
                        peer.failed_attempts = 0
                        self.internal_peers[virtual_ip] = peer
                        del self.external_peers[virtual_ip]
                        recovered_count += 1
                        
                        self.logger.info(f"✅ Route recovered: {virtual_ip} → internal")
                
                if recovered_count > 0:
                    self.logger.info(f"🔄 Route optimization: {recovered_count} routes recovered")
                    
            except Exception as e:
                self.logger.error(f"Route optimization error: {e}")
    
    def stop(self) -> None:
        """Stop internal router"""
        self.running = False
        if self.direct_socket:
            self.direct_socket.close()
    
    def get_stats(self) -> Dict:
        """Get routing statistics"""
        return {
            **self.stats,
            'internal_peers': len(self.internal_peers),
            'external_peers': len(self.external_peers),
            'total_peers': len(self.internal_peers) + len(self.external_peers)
        }
