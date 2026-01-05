# Standalone Database Server - Quick Start

The `db_server.py` is completely standalone with **zero external dependencies**. It uses only Python standard library modules.

## Running the Server (3 Simple Steps)

### 1. Copy the file to your server
```bash
scp db_server.py your-server:~/
```

### 2. Run it
```bash
# Set environment variables
export DB_UPLOAD_PASSWORD="your_secure_password"
export DB_FILES_DIR="./db_files"  # or /var/db_files

# Run the server (Python 3.6+ required)
python3 db_server.py
```

### 3. Put Caddy on top (optional but recommended)
```bash
# Copy Caddyfile to /etc/caddy/Caddyfile
caddy run
```

That's it! No pip install, no virtualenv, no requirements.txt needed.

## What's Included

All imports are from Python standard library:
- `os` - Environment variables and file operations
- `pathlib` - Path handling
- `http.server` - HTTP server
- `json` - JSON encoding/decoding
- `urllib.parse` - URL parsing
- `datetime` - Timestamps
- `hashlib` - (imported but could be removed if not used)

## Testing

```bash
# Health check
curl http://localhost:8081/health

# Upload a database (from another machine)
curl -X POST \
  -H "Authorization: ******" \
  -F "files=@data.db" \
  http://your-server:8081/upload

# Download a database
curl -O http://your-server:8081/db/data.db
```

## With Caddy (recommended)

Caddy adds:
- Automatic HTTPS
- Better static file serving
- Load balancing (if needed)
- Access logs

But `db_server.py` works perfectly fine standalone for testing or small deployments!

## No Docker, No Dependencies

Unlike most Python web servers that require:
- Flask/FastAPI/Django + dependencies
- uvicorn/gunicorn
- requests/httpx for clients
- python-multipart
- ...and more

`db_server.py` requires **nothing** except Python itself. Just copy and run.
