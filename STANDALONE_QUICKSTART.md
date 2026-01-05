# Standalone Database Server - Quick Start

The `db_server.py` is completely standalone with **zero external dependencies**. It uses only Python standard library modules.

## Running the Server (3 Simple Steps)

### 1. Copy db_server.py to your VPS
```bash
scp db_server.py your-server:~/
```

### 2. Configure and run it
```bash
# On your VPS, create .env file
cat > .env << 'EOF'
DB_SERVER_HOST=0.0.0.0
DB_SERVER_PORT=8081
DB_FILES_DIR=/var/db_files
DB_UPLOAD_PASSWORD=your_secure_password
CORS_ALLOW_ORIGIN=*
EOF

# Source the config and run (Python 3.6+ required)
source .env
python3 db_server.py
```

**Why `CORS_ALLOW_ORIGIN=*`?**
- Allows access from any origin
- GitHub Pages can be at different URLs:
  - `https://catalinplesu.github.io`
  - `https://catalinplesu.github.io/Job-Market-Frontend`
  - Custom domains
- Database is public (read-only), so CORS `*` is safe

### 3. Put Caddy on top (optional but recommended)
```bash
# Copy Caddyfile to /etc/caddy/Caddyfile
caddy run
```

That's it! No pip install, no virtualenv, no requirements.txt needed.

## Configuration Files

All configuration is in `.env` files to prevent mismatches:
- **Client `.env`**: `DB_SERVER_URL=https://database.catalinplesu.xyz` and `DB_SERVER_PASSWORD`
- **Server `.env`**: `DB_UPLOAD_PASSWORD` and `CORS_ALLOW_ORIGIN=*`

CORS is set to `*` to allow GitHub Pages from any URL (with or without repo name).

The passwords must match between client and server!

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
# Note: Replace "your_password" with your actual DB_UPLOAD_PASSWORD
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
