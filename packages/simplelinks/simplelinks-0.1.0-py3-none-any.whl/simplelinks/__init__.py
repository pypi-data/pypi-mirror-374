"""
SimpleLinks - Secure Network SDK

A lightweight network connectivity solution that allows you to create
secure network connections using encrypted HTTPS-based communication.

Usage:
    from simplelinks import server, client
    
    # Start server
    server.start(port=20001)
    
    # Join network from client
    client.join(host='server_ip', port=20001, secret='your_secret')
    
    # Server management
    server.info()              # Show server status
    server.list_clients()      # List connected clients
"""

__version__ = "1.1.0"
__author__ = "SimpleLinks Team"
__email__ = "contact@simplelinks.cn"

from . import server
from . import client

__all__ = ["server", "client"]
