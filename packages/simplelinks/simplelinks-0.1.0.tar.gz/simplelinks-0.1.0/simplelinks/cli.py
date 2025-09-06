"""
Command-line interface for SimpleLinks

Provides CLI commands for server and client operations
"""

import argparse
import sys
import time
from . import server, client


def server_cli():
    """CLI for server operations"""
    parser = argparse.ArgumentParser(
        description="SimpleLinks Network Server",
        prog="slink-server"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start server command
    start_parser = subparsers.add_parser('start', help='Start network server')
    start_parser.add_argument(
        '--port', '-p', type=int, default=20001,
        help='Port to listen on (default: 20001)'
    )
    start_parser.add_argument(
        '--host', default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    start_parser.add_argument(
        '--secret', '-s', required=True,
        help='Shared secret for client authentication'
    )
    start_parser.add_argument(
        '--ssl-cert', type=str,
        help='Path to SSL certificate file (default: ~/.simplelinks/certs/fullchain.pem)'
    )
    start_parser.add_argument(
        '--ssl-key', type=str,
        help='Path to SSL private key file (default: ~/.simplelinks/certs/privkey.pem)'
    )
    start_parser.add_argument(
        '--rate-limit', '-r', type=str, default='512k',
        help='Rate limit per client (default: 512k, options: 128k, 256k, 512k, 1m, 2m, 5m, 10m)'
    )
    
    # Status command
    subparsers.add_parser('status', help='Show server status')
    
    # List clients command
    subparsers.add_parser('clients', help='List registered clients')
    
    # Stop server command
    subparsers.add_parser('stop', help='Stop server')
    
    # Info command
    subparsers.add_parser('info', help='Show server information')
    
    # Traffic stats command
    subparsers.add_parser('traffic', help='Show traffic statistics')
    
    # Reset database command
    subparsers.add_parser('reset', help='Reset database - clear all client records and bindings')
    
    # Restart server command
    subparsers.add_parser('restart', help='Restart server with same configuration')
    
    # Web API commands
    subparsers.add_parser('web-start', help='Start Web API server for status monitoring')
    subparsers.add_parser('web-stop', help='Stop Web API server')
    subparsers.add_parser('web-status', help='Show Web API status and URLs')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        try:
            server.start(port=args.port, host=args.host, secret=args.secret,
                        ssl_cert=args.ssl_cert, ssl_key=args.ssl_key, rate_limit=args.rate_limit)
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            print("\nServer stopped.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == 'status':
        server.status()
    
    elif args.command == 'clients':
        clients = server.list_clients()
        if clients:
            print("Registered Clients:")
            for client in clients:
                status_str = "Online" if client['is_online'] else "Offline"
                hostname = client.get('hostname', 'Unknown')
                print(f"  {client['virtual_ip']} - {hostname} ({status_str})")
        else:
            print("No registered clients.")
    
    elif args.command == 'stop':
        server.stop()
    
    elif args.command == 'info':
        info = server.info()
        if 'error' in info:
            print(f"Error: {info['error']}")
        else:
            print(f"Server: {info['host']}:{info['port']}")
            print(f"Network: {info['network']}")
            print(f"Connected: {info['connected_clients']}/{info['max_clients']}")
            print(f"Status: {'Running' if info['running'] else 'Stopped'}")
            if 'rate_limiting' in info:
                rl = info['rate_limiting']
                print(f"Rate Limit: {'Enabled' if rl['enabled'] else 'Disabled'} ({rl['default_rate_kbps']:.0f} KB/s per client)")
                print(f"Active Rate Limiters: {rl['active_clients']}")
    
    elif args.command == 'traffic':
        try:
            # Get traffic statistics from server
            from . import server as srv
            if srv._server_instance and srv._server_instance.running:
                stats = srv._server_instance.rate_limiter.get_all_stats()
                
                print("=== Traffic Statistics ===")
                print(f"Rate Limiting: {'Enabled' if stats['enabled'] else 'Disabled'}")
                print(f"Default Rate: {stats['default_rate_kbps']:.0f} KB/s")
                print(f"Active Clients: {stats['active_clients']}")
                print()
                
                if stats['clients']:
                    print(f"{'Client IP':<12} {'Uptime':<8} {'Sent MB':<8} {'Packets':<8} {'Drops':<6} {'Drop%':<6} {'Avg KB/s':<8}")
                    print("-" * 70)
                    
                    for client_id, client_stats in stats['clients'].items():
                        if 'error' not in client_stats:
                            uptime = f"{client_stats['uptime_seconds']//60}m"
                            sent_mb = client_stats['total_bytes'] / (1024*1024)
                            avg_kbps = client_stats['avg_throughput_kbps']
                            drop_pct = client_stats['drop_rate_pct']
                            
                            print(f"{client_id:<12} {uptime:<8} {sent_mb:<8.2f} {client_stats['packets_sent']:<8} {client_stats['packets_dropped']:<6} {drop_pct:<6.1f} {avg_kbps:<8.1f}")
                else:
                    print("No active clients with traffic data.")
            else:
                print("Error: Server not running")
        except Exception as e:
            print(f"Error getting traffic stats: {e}")
    
    elif args.command == 'reset':
        try:
            # Confirm the reset operation
            print("⚠️  WARNING: This will delete ALL client records and bindings!")
            print("All registered clients will need to reconnect.")
            
            confirm = input("Are you sure you want to reset the database? (yes/no): ")
            if confirm.lower() == 'yes':
                result = server.reset()
                if result:
                    print("✓ Database reset completed successfully")
                else:
                    print("✗ Database reset failed")
                    sys.exit(1)
            else:
                print("Reset cancelled.")
        except KeyboardInterrupt:
            print("\nReset cancelled.")
        except Exception as e:
            print(f"Error during reset: {e}")
            sys.exit(1)
    
    elif args.command == 'restart':
        try:
            server.restart()
        except KeyboardInterrupt:
            print("\nRestart cancelled.")
        except Exception as e:
            print(f"Error during restart: {e}")
            sys.exit(1)
    
    elif args.command == 'web-start':
        server.start_web_api()
    
    elif args.command == 'web-stop':
        server.stop_web_api()
    
    elif args.command == 'web-status':
        server.web_status()
    
    else:
        parser.print_help()


def client_cli():
    """CLI for client operations"""
    parser = argparse.ArgumentParser(
        description="SimpleLinks Network Client",
        prog="slink-client"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Join network command
    join_parser = subparsers.add_parser('join', help='Join network')
    join_parser.add_argument(
        'host', help='Server IP address or hostname'
    )
    join_parser.add_argument(
        '--port', '-p', type=int, default=20001,
        help='Server port (default: 20001)'
    )
    join_parser.add_argument(
        '--secret', '-s', required=True,
        help='Shared secret for authentication'
    )
    join_parser.add_argument(
        '--subnet', default='default',
        help='Subnet identifier (default: default)'
    )
    join_parser.add_argument(
        '--no-reconnect', action='store_true',
        help='Disable automatic reconnection on connection loss'
    )
    
    # Status command
    subparsers.add_parser('status', help='Show client status')
    
    # Info command
    subparsers.add_parser('info', help='Show client information')
    
    # Disconnect command
    subparsers.add_parser('disconnect', help='Disconnect from network')
    
    args = parser.parse_args()
    
    if args.command == 'join':
        try:
            auto_reconnect = not args.no_reconnect
            client.join(host=args.host, port=args.port, secret=args.secret, 
                       subnet=args.subnet, auto_reconnect=auto_reconnect)
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
            print("\nDisconnected")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == 'status':
        status = client.status()
        if 'error' in status:
            print(f"Error: {status['error']}")
        else:
            print(f"Server: {status['server']}")
            print(f"Status: {'Connected' if status['connected'] else 'Disconnected'}")
            print(f"Virtual IP: {status.get('virtual_ip', 'Not assigned')}")
            print(f"Network: {status.get('network', 'Unknown')}")
    
    elif args.command == 'info':
        client.info()
    
    elif args.command == 'disconnect':
        client.disconnect()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    if sys.argv[0].endswith('server'):
        server_cli()
    else:
        client_cli()
