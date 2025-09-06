"""
SimpleLinks Web API Module

Provides HTTP REST API for server status and client information
With access code authentication for security
"""

import json
import time
import ssl
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import logging

class SimpleLinksAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for SimpleLinks API"""
    
    def __init__(self, server_instance, *args, **kwargs):
        self.server_instance = server_instance
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger = logging.getLogger("simplelinks.webapi")
        logger.info(format % args)
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, access_code')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - only for HTML pages with login"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/status.html' or path == '/':
                self.handle_status_page_with_login()
            elif path.startswith('/static/'):
                self.handle_static_file(path)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger = logging.getLogger("simplelinks.webapi")
            logger.error(f"Web error: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests - for API endpoints with access_code verification"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            # Verify access code in headers
            access_code = self.headers.get('access_code')
            if not self.verify_access_code(access_code):
                self.send_json_response({"error": "Invalid access code"}, status=401)
                return
            
            if path == '/api/status':
                self.handle_api_status()
            elif path == '/api/clients':
                self.handle_api_clients()
            elif path == '/api/info':
                self.handle_api_info()
            elif path == '/api/login':
                self.handle_api_login()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger = logging.getLogger("simplelinks.webapi")
            logger.error(f"API error: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def verify_access_code(self, access_code):
        """Verify access code against server secret"""
        if not access_code or not self.server_instance:
            return False
        return access_code == self.server_instance.secret
    
    def handle_api_login(self):
        """Handle /api/login endpoint for access code verification"""
        # This endpoint also requires access_code, but it's for frontend verification
        response = {"success": True, "message": "Access code valid"}
        self.send_json_response(response)
    
    def handle_status_page_with_login(self):
        """Handle /status.html with login form"""
        html_content = self.generate_login_page()
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_static_file(self, path):
        """Handle static file requests"""
        # Remove /static/ prefix and get the relative file path
        file_path = path[8:]  # Remove '/static/' prefix
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        full_path = os.path.join(static_dir, file_path)
        
        # Security check - ensure the file is within static directory
        if not os.path.abspath(full_path).startswith(os.path.abspath(static_dir)):
            self.send_error(403, "Forbidden")
            return
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            self.send_error(404, "File not found")
            return
        
        try:
            # Determine content type based on file extension
            content_type = 'application/octet-stream'  # default
            if full_path.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'
            elif full_path.endswith('.css'):
                content_type = 'text/css; charset=utf-8'
            elif full_path.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif full_path.endswith('.json'):
                content_type = 'application/json; charset=utf-8'
            elif full_path.endswith('.png'):
                content_type = 'image/png'
            elif full_path.endswith('.jpg') or full_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            
            # Read and serve the file
            with open(full_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')  # For CORS if needed
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logger = logging.getLogger("simplelinks.webapi")
            logger.error(f"Error serving static file {full_path}: {e}")
            self.send_error(500, "Internal Server Error")
    
    def generate_login_page(self):
        """Generate HTML login page using external template"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'login.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # Fallback to a simple page if template not found
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SimpleLinks Server Status</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>SimpleLinks Server</h1>
                <p>Template not found. Error: {}</p>
            </body>
            </html>
            """.format(str(e))
    
    def handle_api_status(self):
        """Handle /api/status endpoint"""
        if not self.server_instance or not self.server_instance.running:
            response = {"error": "Server not running"}
        else:
            response = {
                "status": "running",
                "server_info": self.server_instance.get_web_info(),
                "clients": self.server_instance.list_clients(),
                "timestamp": int(time.time())
            }
        
        self.send_json_response(response)
    
    def handle_api_clients(self):
        """Handle /api/clients endpoint"""
        if not self.server_instance or not self.server_instance.running:
            response = {"error": "Server not running"}
        else:
            clients = self.server_instance.list_clients()
            # Enhance client data with formatted timestamps
            for client in clients:
                client['first_seen_formatted'] = datetime.fromtimestamp(client['first_seen']).strftime('%Y-%m-%d %H:%M:%S')
                client['last_seen_formatted'] = datetime.fromtimestamp(client['last_seen']).strftime('%Y-%m-%d %H:%M:%S')
                client['online_duration'] = int(time.time()) - client['first_seen']
                client['status'] = "Online" if client['is_online'] else "Offline"
            
            response = {
                "clients": clients,
                "total_clients": len(clients),
                "online_clients": len([c for c in clients if c['is_online']]),
                "timestamp": int(time.time())
            }
        
        self.send_json_response(response)
    
    def handle_api_info(self):
        """Handle /api/info endpoint"""
        if not self.server_instance or not self.server_instance.running:
            response = {"error": "Server not running"}
        else:
            response = self.server_instance.get_info()
        
        self.send_json_response(response)
    
    def handle_status_page(self):
        """Handle /status.html endpoint"""
        html_content = self.generate_status_html()
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')  # For CORS if needed
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))
    
    def generate_status_html(self):
        """Generate HTML status page"""
        if not self.server_instance or not self.server_instance.running:
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SimpleLinks Status</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>SimpleLinks Server Status</h1>
                <p style="color: red;">Server not running</p>
            </body>
            </html>
            """
        
        # This method is deprecated and not used - always redirect to login page
        return self.generate_login_page()

class SimpleLinksWebAPI:
    """Web API server for SimpleLinks"""
    
    def __init__(self, server_instance, host='0.0.0.0', port=None, ssl_cert=None, ssl_key=None):
        self.server_instance = server_instance
        self.host = host  # Changed from 127.0.0.1 to 0.0.0.0 to allow all IPs
        # Use server port + 1 as default API port
        self.port = port or (server_instance.port + 1 if server_instance else 20002)
        self.ssl_cert = ssl_cert or (server_instance.ssl_cert if server_instance else None)
        self.ssl_key = ssl_key or (server_instance.ssl_key if server_instance else None)
        self.httpd = None
        self.thread = None
        self.running = False
        self.use_ssl = False
        
        # Setup logging
        self.logger = logging.getLogger("simplelinks.webapi")
        
        # Check if SSL should be enabled
        if self.ssl_cert and self.ssl_key and os.path.exists(self.ssl_cert) and os.path.exists(self.ssl_key):
            self.use_ssl = True
    
    def start(self):
        """Start the web API server"""
        if self.running:
            self.logger.warning("Web API server already running")
            return
        
        try:
            # Create handler class with server instance
            handler_class = lambda *args, **kwargs: SimpleLinksAPIHandler(self.server_instance, *args, **kwargs)
            
            self.httpd = HTTPServer((self.host, self.port), handler_class)
            
            # Setup SSL if certificates are available
            if self.use_ssl:
                try:
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    context.load_cert_chain(self.ssl_cert, self.ssl_key)
                    self.httpd.socket = context.wrap_socket(self.httpd.socket, server_side=True)
                    self.logger.info(f"SSL enabled for Web API server using cert: {self.ssl_cert}")
                except Exception as e:
                    self.logger.warning(f"Failed to enable SSL for Web API: {e}, falling back to HTTP")
                    self.use_ssl = False
            
            self.running = True
            
            def run_server():
                protocol = "https" if self.use_ssl else "http"
                self.logger.info(f"Starting Web API server on {protocol}://{self.host}:{self.port}")
                try:
                    self.httpd.serve_forever()
                except Exception as e:
                    self.logger.error(f"Web API server error: {e}")
                finally:
                    self.running = False
            
            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()
            
            protocol = "https" if self.use_ssl else "http"
            self.logger.info(f"Web API server started successfully")
            self.logger.info(f"  Status page: {protocol}://{self.host}:{self.port}/status.html")
            self.logger.info(f"  API endpoints: {protocol}://{self.host}:{self.port}/api/status")
            
        except Exception as e:
            self.logger.error(f"Failed to start Web API server: {e}")
            self.running = False
            raise
    
    def stop(self):
        """Stop the web API server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3.0)
        
        self.running = False
        self.logger.info("Web API server stopped")
    
    def get_urls(self):
        """Get available URLs"""
        if not self.running:
            return []
        
        protocol = "https" if self.use_ssl else "http"
        base_url = f"{protocol}://{self.host}:{self.port}"
        return [
            f"{base_url}/status.html",
            f"{base_url}/api/status",
            f"{base_url}/api/clients", 
            f"{base_url}/api/info"
        ]
