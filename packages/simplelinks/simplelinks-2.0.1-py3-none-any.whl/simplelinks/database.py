"""
Database management for SimpleLinks server
Handles client registration and virtual IP allocation
"""

import sqlite3
import os
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class ClientDatabase:
    """Manages client information and virtual IP allocation"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            # Default to ~/.simplelinks/clients.db
            home_dir = Path.home()
            simplelinks_dir = home_dir / ".simplelinks"
            simplelinks_dir.mkdir(exist_ok=True)
            # Also create certs subdirectory
            certs_dir = simplelinks_dir / "certs"
            certs_dir.mkdir(exist_ok=True)
            db_path = simplelinks_dir / "clients.db"
        
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        with self.conn:
            # Create table with original structure first
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    machine_id TEXT PRIMARY KEY,
                    virtual_ip TEXT UNIQUE NOT NULL,
                    public_ip TEXT,
                    private_ip TEXT,
                    hostname TEXT,
                    secret_hash TEXT NOT NULL,
                    first_seen INTEGER NOT NULL,
                    last_seen INTEGER NOT NULL,
                    is_online INTEGER DEFAULT 0,
                    session_id TEXT
                )
            """)
            
            # Check if secret column exists, add it if missing
            cursor = self.conn.execute("PRAGMA table_info(clients)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'secret' not in columns:
                try:
                    self.conn.execute("ALTER TABLE clients ADD COLUMN secret TEXT")
                    print("Added secret column to clients table")
                except Exception as e:
                    print(f"Note: Could not add secret column: {e}")
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Initialize default network configuration
            self.conn.execute("""
                INSERT OR IGNORE INTO server_config (key, value)
                VALUES ('network_base', '10.254.254.0/29')
            """)
            
            self.conn.execute("""
                INSERT OR IGNORE INTO server_config (key, value)
                VALUES ('max_clients', '6')
            """)
    
    def get_network_config(self) -> Dict[str, str]:
        """Get network configuration"""
        cursor = self.conn.execute("""
            SELECT key, value FROM server_config 
            WHERE key IN ('network_base', 'max_clients')
        """)
        return {row['key']: row['value'] for row in cursor.fetchall()}
    
    def _hash_secret(self, secret: str) -> str:
        """Hash secret for storage"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def _get_next_virtual_ip(self) -> Optional[str]:
        """Get next available virtual IP from 10.254.254.1 to 10.254.254.6"""
        base_ip = "10.254.254"
        
        cursor = self.conn.execute("""
            SELECT virtual_ip FROM clients ORDER BY virtual_ip
        """)
        used_ips = {row['virtual_ip'] for row in cursor.fetchall()}
        
        for i in range(1, 7):  # 10.254.254.1 to 10.254.254.6
            candidate_ip = f"{base_ip}.{i}"
            if candidate_ip not in used_ips:
                return candidate_ip
        
        return None  # All IPs are taken
    
    def register_client(self, machine_id: str, secret: str, 
                       public_ip: str = None, private_ip: str = None, 
                       hostname: str = None, session_id: str = None) -> Dict:
        """
        Register or update client information
        Returns dict with client info or error
        """
        try:
            secret_hash = self._hash_secret(secret)
            current_time = int(time.time())
            
            print(f"DEBUG: register_client called with machine_id={machine_id}, public_ip={public_ip}")
            
            with self.conn:
                # Check if client exists
                cursor = self.conn.execute("""
                    SELECT * FROM clients WHERE machine_id = ?
                """, (machine_id,))
                existing_client = cursor.fetchone()
                
                if existing_client:
                    # Verify secret
                    if existing_client['secret_hash'] != secret_hash:
                        return {"error": "Invalid secret", "code": 401}
                    
                    # Update existing client
                    self.conn.execute("""
                        UPDATE clients 
                        SET public_ip = COALESCE(?, public_ip),
                            private_ip = COALESCE(?, private_ip),
                            hostname = COALESCE(?, hostname),
                            secret = ?,
                            last_seen = ?,
                            is_online = 1,
                            session_id = ?
                        WHERE machine_id = ?
                    """, (public_ip, private_ip, hostname, secret, current_time, 
                          session_id, machine_id))
                    
                    # Return updated client info
                    cursor = self.conn.execute("""
                        SELECT * FROM clients WHERE machine_id = ?
                    """, (machine_id,))
                    client = cursor.fetchone()
                    
                    return {
                        "machine_id": client['machine_id'],
                        "virtual_ip": client['virtual_ip'],
                        "public_ip": client['public_ip'],
                        "private_ip": client['private_ip'],
                        "hostname": client['hostname'],
                        "secret": secret,  # Include the original secret for heartbeat processing
                        "first_seen": client['first_seen'],
                        "last_seen": client['last_seen'],
                        "session_id": client['session_id']
                    }
                
                else:
                    # New client - check if we have space
                    cursor = self.conn.execute("""
                        SELECT COUNT(*) as count FROM clients
                    """)
                    client_count = cursor.fetchone()['count']
                    
                    if client_count >= 6:
                        return {"error": "Maximum client limit reached (6). Please contact server administrator.", "code": 403}
                    
                    # Assign virtual IP
                    virtual_ip = self._get_next_virtual_ip()
                    if virtual_ip is None:
                        return {"error": "No available virtual IP addresses", "code": 503}
                    
                    # Insert new client
                    self.conn.execute("""
                        INSERT INTO clients 
                        (machine_id, virtual_ip, public_ip, private_ip, hostname, 
                         secret, secret_hash, first_seen, last_seen, is_online, session_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """, (machine_id, virtual_ip, public_ip, private_ip, hostname,
                          secret, secret_hash, current_time, current_time, session_id))
                    
                    return {
                        "machine_id": machine_id,
                        "virtual_ip": virtual_ip,
                        "public_ip": public_ip,
                        "private_ip": private_ip,
                        "hostname": hostname,
                        "secret": secret,  # Include the original secret for heartbeat processing
                        "first_seen": current_time,
                        "last_seen": current_time,
                        "session_id": session_id
                    }
        
        except Exception as e:
            print(f"DEBUG: Database error: {e}")
            return {"error": f"Database error: {e}", "code": 500}
    
    def update_client_heartbeat(self, session_id: str):
        """Update client last_seen timestamp for heartbeat"""
        current_time = int(time.time())
        with self.conn:
            self.conn.execute("""
                UPDATE clients SET last_seen = ? WHERE session_id = ?
            """, (current_time, session_id))
    
    def set_client_offline(self, machine_id: str = None, session_id: str = None):
        """Mark client as offline"""
        with self.conn:
            if machine_id:
                self.conn.execute("""
                    UPDATE clients SET is_online = 0, session_id = NULL 
                    WHERE machine_id = ?
                """, (machine_id,))
            elif session_id:
                self.conn.execute("""
                    UPDATE clients SET is_online = 0, session_id = NULL 
                    WHERE session_id = ?
                """, (session_id,))
    
    def get_client_by_virtual_ip(self, virtual_ip: str) -> Optional[Dict]:
        """Get client info by virtual IP"""
        cursor = self.conn.execute("""
            SELECT * FROM clients WHERE virtual_ip = ?
        """, (virtual_ip,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_client_by_machine_id(self, machine_id: str) -> Optional[Dict]:
        """Get client info by machine ID"""
        cursor = self.conn.execute("""
            SELECT * FROM clients WHERE machine_id = ?
        """, (machine_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_client_by_session_id(self, session_id: str) -> Optional[Dict]:
        """Get client info by session ID"""
        cursor = self.conn.execute("""
            SELECT * FROM clients WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def list_clients(self) -> List[Dict]:
        """List all registered clients"""
        cursor = self.conn.execute("""
            SELECT machine_id, virtual_ip, public_ip, private_ip, hostname,
                   first_seen, last_seen, is_online
            FROM clients 
            ORDER BY virtual_ip
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_online_clients(self) -> List[Dict]:
        """Get list of currently online clients"""
        cursor = self.conn.execute("""
            SELECT * FROM clients WHERE is_online = 1 ORDER BY virtual_ip
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_stale_clients(self, timeout_seconds: int = 300):
        """Mark clients as offline if they haven't been seen recently"""
        cutoff_time = int(time.time()) - timeout_seconds
        with self.conn:
            self.conn.execute("""
                UPDATE clients 
                SET is_online = 0, session_id = NULL 
                WHERE last_seen < ? AND is_online = 1
            """, (cutoff_time,))
    
    def reset_database(self) -> bool:
        """Reset database - clear all client data and bindings"""
        try:
            with self.conn:
                # Delete all client records
                self.conn.execute("DELETE FROM clients")
                
                # Reset any auto-increment sequences if they exist (only if the table exists)
                cursor = self.conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='sqlite_sequence'
                """)
                if cursor.fetchone():
                    self.conn.execute("DELETE FROM sqlite_sequence WHERE name='clients'")
                
                print("Database reset completed - all client records cleared")
                return True
                
        except Exception as e:
            print(f"Database reset failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        self.conn.close()
