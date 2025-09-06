# SimpleLinks - Secure Network Connectivity

A lightweight network connectivity solution that creates encrypted connections between devices through a central server based on secure HTTPS.

## Features

- Secure encrypted communication with SSL/TLS protection
- Virtual network interface management
- Client-server architecture with group-based connectivity
- Cross-platform support (Linux/macOS)

## Requirements

- Python 3.7+
- Network connectivity libraries
- Administrative privileges (for network interface management)

## Installation

```bash
pip3 install simplelinks
```

## Usage

### Server

1. Place your SSL certificate files in `~/.simplelinks/certs/`:
   - `~/.simplelinks/certs/fullchain.pem` (certificate)
   - `~/.simplelinks/certs/privkey.pem` (private key)

2. Run the server:

```bash
slink-server start --secret your_secret
```

**Custom certificate paths:**
```bash
slink-server start --secret your_secret --ssl-cert /path/to/cert.pem --ssl-key /path/to/key.pem
```

**Without SSL (development only):**
```bash
# Server will run without SSL if certificates are not found
slink-server start --secret your_secret
```

### Client

#### Linux Client

Connect a Linux client to the server:

```bash
slink-client join your-server.com --secret mysecret
```

#### macOS Client

**Full Functionality (Recommended):**
Install network driver first, then use the standard client:
```bash
# Install network driver
brew install --cask tuntap
# Reboot required after installation

# Use standard client
slink-client join your-server.com --secret mysecret
```

**Testing Only (Limited functionality):**
```bash
python3 client/client_macos_minimal.py --host your-server.com:20001 -s mysecret -i 10.0.0.104
```

> 📖 See [MACOS_SETUP.md](MACOS_SETUP.md) for detailed setup instructions

#### Parameters:
- `--host`: Server address
- `-s, --secret`: Shared secret for group authentication
- `-i, --ip`: Virtual IP address for this client
- `-d, --debug`: Enable debug logging (optional)

## Platform Differences

### Linux
- Uses standard network interface devices
- Configures interface with system network tools
- Standard interface without additional headers

### macOS
- Uses system userspace network interfaces
- Configures interface with system network commands
- Includes protocol header in data packets
- Automatically assigns interface identifiers

## Architecture

- **Server**: Manages secure connections and routes traffic between clients in the same group
- **Client**: Creates network interface and forwards traffic through encrypted connection
- **Groups**: Clients with the same secret form a group and can communicate with each other

## Security Notes

- Development mode may skip certificate verification for testing
- Production deployment should enable full certificate validation
- Requires administrative privileges for network interface management

## License

SimpleLinks is dual-licensed:
- **Community Edition**: AGPL-3.0 (for open source projects, personal use, and non-commercial applications)
- **Commercial Edition**: Available for commercial use, proprietary applications, and when AGPL requirements cannot be met

For commercial licensing, please contact: contact@simplelinks.cn

See [LICENSE](LICENSE) for full details.
