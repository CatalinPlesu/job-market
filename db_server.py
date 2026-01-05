#!/usr/bin/env python3
"""
Database File Server - Standalone, Zero Dependencies

A lightweight server for receiving and serving database files.

Features:
- POST endpoint with password authentication for uploading DB files
- GET endpoint for public access to DB files
- File validation and secure storage
- Uses ONLY Python standard library - no pip install required!

Usage:
    export DB_UPLOAD_PASSWORD="your_password"
    export DB_FILES_DIR="./db_files"
    python3 db_server.py
"""

import os
import hashlib
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuration
SERVER_HOST = os.getenv("DB_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("DB_SERVER_PORT", "8081"))
DB_FILES_DIR = os.getenv("DB_FILES_DIR", "/var/db_files")
UPLOAD_PASSWORD = os.getenv("DB_UPLOAD_PASSWORD")

# Validate password is set
if not UPLOAD_PASSWORD:
    print("WARNING: DB_UPLOAD_PASSWORD environment variable is not set!")
    print("Using insecure default password 'change_me_in_production'")
    print("Set DB_UPLOAD_PASSWORD before deploying to production!")
    UPLOAD_PASSWORD = "change_me_in_production"

# Ensure DB files directory exists
Path(DB_FILES_DIR).mkdir(parents=True, exist_ok=True)

# Allowed database files
ALLOWED_FILES = ["data.db", "scrape.db"]
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


class DBFileHandler(BaseHTTPRequestHandler):
    """HTTP request handler for database file operations"""
    
    def log_message(self, format, *args):
        """Custom logging with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def _send_cors_headers(self):
        """Send CORS headers for cross-origin requests"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    
    def _send_json_response(self, status_code, data):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests for database files"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Health check endpoint
        if path == "/health":
            self._send_json_response(200, {"status": "ok"})
            return
        
        # List available files
        if path == "/db" or path == "/db/":
            files = []
            for filename in ALLOWED_FILES:
                file_path = Path(DB_FILES_DIR) / filename
                if file_path.exists():
                    stat = file_path.stat()
                    files.append({
                        "name": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            self._send_json_response(200, {"files": files})
            return
        
        # Serve specific database file
        if path.startswith("/db/"):
            filename = path[4:]  # Remove '/db/' prefix
            
            if filename not in ALLOWED_FILES:
                self._send_json_response(403, {"error": "File not allowed"})
                return
            
            file_path = Path(DB_FILES_DIR) / filename
            if not file_path.exists():
                self._send_json_response(404, {"error": "File not found"})
                return
            
            # Serve the file
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self._send_cors_headers()
                self.end_headers()
                
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                
                self.log_message(f"Served {filename} ({file_path.stat().st_size} bytes)")
                return
                
            except Exception as e:
                self.log_message(f"Error serving file: {e}")
                self._send_json_response(500, {"error": "Internal server error"})
                return
        
        # Default response
        self._send_json_response(404, {"error": "Not found"})
    
    def do_POST(self):
        """Handle POST requests for uploading database files"""
        
        # Only allow /upload endpoint
        if self.path != "/upload":
            self._send_json_response(404, {"error": "Not found"})
            return
        
        # Check authentication
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            self._send_json_response(401, {"error": "Missing or invalid authorization header"})
            return
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        if token != UPLOAD_PASSWORD:
            self.log_message("Authentication failed: invalid password")
            self._send_json_response(403, {"error": "Invalid password"})
            return
        
        # Check content type
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self._send_json_response(400, {"error": "Content-Type must be multipart/form-data"})
            return
        
        # Extract boundary from Content-Type
        if "boundary=" not in content_type:
            self._send_json_response(400, {"error": "Missing boundary in Content-Type header"})
            return
        
        try:
            boundary = content_type.split("boundary=")[1].encode()
        except IndexError:
            self._send_json_response(400, {"error": "Invalid Content-Type header format"})
            return
        
        # Parse multipart form data
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            
            if content_length > MAX_FILE_SIZE:
                self._send_json_response(413, {"error": f"File too large (max {MAX_FILE_SIZE} bytes)"})
                return
            
            # Read the body
            body = self.rfile.read(content_length)
            
            # Note: This is a simplified multipart form parser
            # For production use, consider using python-multipart library for better robustness
            # Split body by boundary
            parts = body.split(b"--" + boundary)
            
            uploaded_files = []
            
            for part in parts:
                if b"Content-Disposition" not in part:
                    continue
                
                # Extract filename from Content-Disposition header
                lines = part.split(b"\r\n")
                disposition_line = None
                for line in lines:
                    if b"Content-Disposition" in line:
                        disposition_line = line.decode()
                        break
                
                if not disposition_line:
                    continue
                
                # Parse filename
                if 'filename="' not in disposition_line:
                    continue
                
                filename = disposition_line.split('filename="')[1].split('"')[0]
                
                if filename not in ALLOWED_FILES:
                    self.log_message(f"Rejected upload: {filename} not in allowed files")
                    continue
                
                # Extract file content (after double CRLF)
                content_start = part.find(b"\r\n\r\n") + 4
                content_end = len(part) - 2  # Remove trailing CRLF
                file_content = part[content_start:content_end]
                
                # Validate it's a SQLite database file
                if not file_content.startswith(b"SQLite format 3"):
                    self.log_message(f"Rejected upload: {filename} is not a valid SQLite database")
                    continue
                
                # Save the file
                file_path = Path(DB_FILES_DIR) / filename
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                file_size = len(file_content)
                self.log_message(f"Saved {filename} ({file_size} bytes)")
                
                uploaded_files.append({
                    "filename": filename,
                    "size": file_size,
                    "path": str(file_path)
                })
            
            if uploaded_files:
                self._send_json_response(200, {
                    "success": True,
                    "message": "Files uploaded successfully",
                    "files": uploaded_files
                })
            else:
                self._send_json_response(400, {"error": "No valid files uploaded"})
        
        except Exception as e:
            self.log_message(f"Upload error: {e}")
            import traceback
            traceback.print_exc()
            self._send_json_response(500, {"error": f"Upload failed: {str(e)}"})


def run_server():
    """Start the HTTP server"""
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DBFileHandler)
    
    print("=" * 80)
    print("DATABASE FILE SERVER")
    print("=" * 80)
    print(f"Server running on http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"Database files directory: {DB_FILES_DIR}")
    print(f"Allowed files: {', '.join(ALLOWED_FILES)}")
    print()
    print("Endpoints:")
    print(f"  GET  /health          - Health check")
    print(f"  GET  /db/             - List available files")
    print(f"  GET  /db/data.db      - Download data.db")
    print(f"  GET  /db/scrape.db    - Download scrape.db")
    print(f"  POST /upload          - Upload database files (requires password)")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
