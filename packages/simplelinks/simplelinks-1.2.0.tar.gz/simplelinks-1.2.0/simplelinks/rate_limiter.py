"""
Rate limiter for SimpleLinks traffic control
Uses token bucket algorithm for smooth traffic shaping
"""

import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ClientStats:
    """Statistics for a client connection"""
    total_bytes: int = 0
    packets_sent: int = 0
    packets_dropped: int = 0
    last_reset: float = 0


class TokenBucket:
    """Token bucket for rate limiting"""
    
    def __init__(self, rate_bps: int, burst_size: Optional[int] = None):
        """
        Initialize token bucket
        
        Args:
            rate_bps: Rate in bytes per second (e.g., 65536 for 512kbps)
            burst_size: Maximum burst size in bytes (default: 2x rate)
        """
        self.rate = rate_bps  # bytes per second
        self.burst_size = burst_size or (rate_bps * 2)  # Allow 2 seconds burst
        self.tokens = self.burst_size  # Start with full bucket
        self.last_update = time.time()
    
    def consume(self, bytes_requested: int) -> bool:
        """
        Try to consume tokens for the given number of bytes
        
        Args:
            bytes_requested: Number of bytes to send
            
        Returns:
            True if tokens were consumed, False if rate limited
        """
        now = time.time()
        
        # Add tokens based on elapsed time
        elapsed = now - self.last_update
        self.tokens = min(self.burst_size, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        # Check if we have enough tokens
        if self.tokens >= bytes_requested:
            self.tokens -= bytes_requested
            return True
        else:
            return False
    
    def get_status(self) -> Dict:
        """Get current bucket status"""
        now = time.time()
        elapsed = now - self.last_update
        current_tokens = min(self.burst_size, self.tokens + elapsed * self.rate)
        
        return {
            "rate_bps": self.rate,
            "rate_kbps": self.rate / 1024,
            "burst_size": self.burst_size,
            "current_tokens": int(current_tokens),
            "utilization_pct": ((self.burst_size - current_tokens) / self.burst_size) * 100
        }


class RateLimiter:
    """Rate limiter for multiple clients"""
    
    def __init__(self, default_rate_bps: int = 65536):  # 512 kbps default
        """
        Initialize rate limiter
        
        Args:
            default_rate_bps: Default rate limit in bytes per second
        """
        self.default_rate = default_rate_bps
        self.client_buckets: Dict[str, TokenBucket] = {}
        self.client_stats: Dict[str, ClientStats] = {}
        self.enabled = True
    
    def get_or_create_bucket(self, client_id: str, rate_bps: Optional[int] = None) -> TokenBucket:
        """Get or create token bucket for a client"""
        if client_id not in self.client_buckets:
            rate = rate_bps or self.default_rate
            self.client_buckets[client_id] = TokenBucket(rate)
            self.client_stats[client_id] = ClientStats(last_reset=time.time())
        
        return self.client_buckets[client_id]
    
    def can_send(self, client_id: str, packet_size: int) -> bool:
        """
        Check if client can send a packet of given size
        
        Args:
            client_id: Client identifier (session_id or virtual_ip)
            packet_size: Size of packet in bytes
            
        Returns:
            True if packet can be sent, False if rate limited
        """
        if not self.enabled:
            return True
        
        bucket = self.get_or_create_bucket(client_id)
        stats = self.client_stats[client_id]
        
        if bucket.consume(packet_size):
            # Packet allowed
            stats.total_bytes += packet_size
            stats.packets_sent += 1
            return True
        else:
            # Packet rate limited
            stats.packets_dropped += 1
            return False
    
    def get_client_stats(self, client_id: str) -> Dict:
        """Get statistics for a client"""
        if client_id not in self.client_stats:
            return {"error": "Client not found"}
        
        stats = self.client_stats[client_id]
        bucket = self.client_buckets[client_id]
        now = time.time()
        uptime = now - stats.last_reset
        
        return {
            "client_id": client_id,
            "uptime_seconds": int(uptime),
            "total_bytes": stats.total_bytes,
            "packets_sent": stats.packets_sent,
            "packets_dropped": stats.packets_dropped,
            "drop_rate_pct": (stats.packets_dropped / max(1, stats.packets_sent + stats.packets_dropped)) * 100,
            "avg_throughput_bps": stats.total_bytes / max(1, uptime),
            "avg_throughput_kbps": (stats.total_bytes / max(1, uptime)) / 1024,
            "bucket_status": bucket.get_status()
        }
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all clients"""
        return {
            "enabled": self.enabled,
            "default_rate_bps": self.default_rate,
            "default_rate_kbps": self.default_rate / 1024,
            "active_clients": len(self.client_buckets),
            "clients": {cid: self.get_client_stats(cid) for cid in self.client_stats.keys()}
        }
    
    def set_client_rate(self, client_id: str, rate_bps: int):
        """Set custom rate limit for a specific client"""
        if client_id in self.client_buckets:
            # Update existing bucket
            self.client_buckets[client_id] = TokenBucket(rate_bps)
        else:
            # Create new bucket with custom rate
            self.client_buckets[client_id] = TokenBucket(rate_bps)
            self.client_stats[client_id] = ClientStats(last_reset=time.time())
    
    def remove_client(self, client_id: str):
        """Remove client from rate limiter"""
        self.client_buckets.pop(client_id, None)
        self.client_stats.pop(client_id, None)
    
    def enable(self):
        """Enable rate limiting"""
        self.enabled = True
    
    def disable(self):
        """Disable rate limiting"""
        self.enabled = False


# Utility functions for common rate conversions
def kbps_to_bps(kbps: float) -> int:
    """Convert kilobits per second to bytes per second"""
    return int(kbps * 1024 / 8)

def mbps_to_bps(mbps: float) -> int:
    """Convert megabits per second to bytes per second"""
    return int(mbps * 1024 * 1024 / 8)

# Common rate presets
RATE_PRESETS = {
    "128k": kbps_to_bps(128),   # 16 KB/s
    "256k": kbps_to_bps(256),   # 32 KB/s  
    "512k": kbps_to_bps(512),   # 64 KB/s
    "1m": mbps_to_bps(1),       # 128 KB/s
    "2m": mbps_to_bps(2),       # 256 KB/s
    "5m": mbps_to_bps(5),       # 640 KB/s
    "10m": mbps_to_bps(10),     # 1280 KB/s
}
