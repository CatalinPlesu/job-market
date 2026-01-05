# Database Server Setup Guide

This guide explains how to set up and use the custom database server for hosting large SQLite database files.

## Quick Start (TL;DR)

```bash
# 1. Copy db_server.py to your VPS
scp db_server.py your-server:~/

# 2. On your VPS, create .env file
cat > .env << 'EOF'
DB_SERVER_HOST=0.0.0.0
DB_SERVER_PORT=8081
DB_FILES_DIR=/var/db_files
DB_UPLOAD_PASSWORD=your_secure_password_here
CORS_ALLOW_ORIGIN=*
EOF

# 3. Source config and run the server
source .env
python3 db_server.py

# 4. Put Caddy on top (see Caddyfile) - that's it!
```

The server has **zero external dependencies** - it uses only Python standard library.

**Configuration:** All settings are in `.env` files to avoid mismatches:
- `.env` on your main machine (client config: `DB_SERVER_URL`, `DB_SERVER_PASSWORD`)
- `.env` on your VPS (server config: `DB_UPLOAD_PASSWORD`, `CORS_ALLOW_ORIGIN=*`)
- CORS is set to `*` to allow GitHub Pages from any URL pattern


## Overview

The custom database server provides:
- **Password-protected POST endpoint** for uploading database files
- **Public GET endpoint** for serving database files to the frontend
- **CORS support** for cross-origin requests
- **File validation** to ensure only valid SQLite databases are uploaded
- **Zero external dependencies** - uses only Python standard library

**`db_server.py` is completely standalone!** Just copy it to your server and run it with Python 3.6+. No pip install needed for the server itself.

This solution works around GitHub Pages limitations with large files (>100MB) and browser CORS restrictions in Chrome/Edge.

## Components

1. **Caddy Server** (`Caddyfile`) - Reverse proxy and static file server
2. **Python Server** (`db_server.py`) - Database file upload and serving
3. **Upload Module** (`src/db_upload.py`) - Python code to push databases to server
4. **Frontend Config** (`frontend/js/config.js`) - JavaScript configuration for custom server

## Setup Instructions

### 1. Install Dependencies

#### Install Caddy
```bash
# Ubuntu/Debian
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# macOS
brew install caddy

# Or download from https://caddyserver.com/download
```

#### Python Server Dependencies

**`db_server.py` has NO external dependencies!** It uses only Python standard library modules.

Simply copy `db_server.py` to your server and run it:
```bash
# Copy the file
scp db_server.py your-server:~/

# Run it (Python 3.6+ required)
python3 db_server.py
```

#### Python Client Dependencies (optional - only needed for uploading from scraper)

If you want to use the Python upload client (`src/db_upload.py`) from the scraper:
```bash
pip install requests python-dotenv
```

Note: You can also upload files manually using `curl` without any Python dependencies.

### 2. Configure Environment Variables

#### Client Configuration (on your main machine/scraper)

Edit your main `.env` file (use `.env.example` as template):

```bash
# Custom Database Server Configuration
DB_SERVER_URL=https://database.catalinplesu.xyz
DB_SERVER_PASSWORD=your_secure_password_here
```

#### Server Configuration (on your VPS)

Create a `.env` file on your VPS with the server configuration:

```bash
# On your VPS
nano ~/.env  # Create and edit the file
```

Example VPS `.env` content:
```bash
DB_SERVER_HOST=0.0.0.0
DB_SERVER_PORT=8081
DB_FILES_DIR=/var/db_files
DB_UPLOAD_PASSWORD=your_secure_password_here
CORS_ALLOW_ORIGIN=*
```

**Important:** 
- `DB_SERVER_PASSWORD` (client) and `DB_UPLOAD_PASSWORD` (server) must match **exactly**!
- **No quotes needed** in `.env` files - use `PASSWORD=mypassword` not `PASSWORD="mypassword"`
- Whitespace is automatically trimmed from passwords to prevent authentication issues
- If authentication fails, check the server logs for password length comparison
- `CORS_ALLOW_ORIGIN=*` allows access from any origin (needed for GitHub Pages which can be at different URLs)
  - Works with `https://catalinplesu.github.io`
  - Works with `https://catalinplesu.github.io/Job-Market-Frontend`
  - Works with custom domains
- The `.env` approach prevents configuration mismatches between client and server

### 3. Deploy the Server

#### Production Deployment on database.catalinplesu.xyz

1. Create the database files directory on your server:
```bash
sudo mkdir -p /var/db_files
sudo chown $USER:$USER /var/db_files
```

2. Copy files to your server:
```bash
scp Caddyfile your-server:/etc/caddy/Caddyfile
scp db_server.py your-server:~/db_server.py
```

3. Create a systemd service for the Python server:

```ini
# /etc/systemd/system/db-server.service
[Unit]
Description=Database File Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user
Environment="DB_FILES_DIR=/var/db_files"
Environment="DB_UPLOAD_PASSWORD=your_secure_password"
Environment="DB_SERVER_PORT=8081"
ExecStart=/usr/bin/python3 /home/your-user/db_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

4. Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now db-server
sudo systemctl enable --now caddy
```

5. Update Caddyfile for production with SSL:
```caddyfile
db.example.com {
    # CORS headers
    header Access-Control-Allow-Origin *
    header Access-Control-Allow-Methods "GET, POST, OPTIONS"
    header Access-Control-Allow-Headers "Content-Type, Authorization"
    
    # Handle preflight
    @options {
        method OPTIONS
    }
    handle @options {
        respond 200
    }
    
    # Public GET endpoint
    handle /db/* {
        method GET
        root * /var/db_files
        rewrite /db/* /
        file_server
    }
    
    # Password-protected POST endpoint
    handle /upload {
        method POST
        reverse_proxy localhost:8081
    }
    
    # Health check
    handle /health {
        respond "OK" 200
    }
}
```

### 4. Configure the Frontend

Edit `frontend/js/config.js` to use your custom server:

```javascript
const API_CONFIG = {
    type: "custom-server",  // Change from "github-lfs-proxy" to "custom-server"
    
    customServer: {
        url: "https://db.example.com",  // Your server URL
        path: "/db"
    },
    
    // Keep other configurations...
};
```

### 5. Upload Databases

Use the menu option in `main.py`:

```bash
python main.py
# Select option: "Upload Database Files to Server"
```

Or use the API directly:

```bash
curl -X POST \
  -H "Authorization: Bearer your_secure_password" \
  -F "files=@databases/data.db" \
  -F "files=@databases/scrape.db" \
  https://db.example.com/upload
```

## API Endpoints

### GET /db/
List available database files
```bash
curl https://db.example.com/db/
```

Response:
```json
{
  "files": [
    {
      "name": "data.db",
      "size": 150000000,
      "modified": "2025-01-05T13:00:00"
    },
    {
      "name": "scrape.db",
      "size": 50000000,
      "modified": "2025-01-05T13:00:00"
    }
  ]
}
```

### GET /db/data.db
Download the data.db file
```bash
curl -O https://db.example.com/db/data.db
```

### GET /db/scrape.db
Download the scrape.db file
```bash
curl -O https://db.example.com/db/scrape.db
```

### POST /upload
Upload database files (requires authentication)
```bash
curl -X POST \
  -H "Authorization: Bearer your_password" \
  -F "files=@databases/data.db" \
  https://db.example.com/upload
```

Response:
```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "files": [
    {
      "filename": "data.db",
      "size": 150000000,
      "path": "/var/db_files/data.db"
    }
  ]
}
```

### GET /health
Health check endpoint
```bash
curl https://db.example.com/health
```

Response:
```json
{"status": "ok"}
```

## Security Considerations

1. **Password Protection**: The upload endpoint requires a password via the `Authorization: Bearer` header
2. **Mandatory Password**: The server warns if DB_UPLOAD_PASSWORD is not set and uses an insecure default. Always set a strong password in production.
3. **File Validation**: Only valid SQLite database files are accepted
4. **File Size Limit**: Maximum file size is 500 MB (configurable)
5. **Allowed Files**: Only `data.db` and `scrape.db` are accepted
6. **HTTPS**: Use HTTPS in production (Caddy provides automatic HTTPS)
7. **Multipart Parsing**: The current implementation uses simplified multipart parsing. For production, consider using `python-multipart` library for better robustness.

## Production Deployment Notes

1. **Always set DB_UPLOAD_PASSWORD**: Never rely on the default password in production
2. **Use HTTPS**: Configure Caddy with a proper domain for automatic HTTPS
3. **Firewall**: Restrict access to port 8081 (only allow localhost)
4. **Rate Limiting**: Consider adding rate limiting in Caddy for the upload endpoint
5. **Monitoring**: Set up monitoring for disk space and server health
6. **Backups**: Regularly backup the database files directory

## Troubleshooting

### Authentication Failed: Invalid Password

If you see `Authentication failed: invalid password` in the server logs:

1. **Check password length in logs**: The server now logs password lengths for debugging
   ```
   [2026-01-05 19:28:28] Authentication failed: invalid password (received length: 15, expected length: 14)
   ```

2. **Common causes**:
   - **Quotes in .env file**: Don't use quotes! Use `PASSWORD=mypass` not `PASSWORD="mypass"`
   - **Trailing whitespace**: Check for spaces after the password in your `.env` file
   - **Different passwords**: Ensure `DB_SERVER_PASSWORD` (client) matches `DB_UPLOAD_PASSWORD` (server)
   - **Not sourced**: Remember to `source .env` on the VPS before running `db_server.py`

3. **Verification steps**:
   ```bash
   # On client machine
   echo "Password length: ${#DB_SERVER_PASSWORD}"
   
   # On VPS
   echo "Password length: ${#DB_UPLOAD_PASSWORD}"
   ```
   Both should show the same length!

4. **Client output**: Check for "Password configured: X characters" in upload output

### Connection Refused
- Check if services are running: `systemctl status db-server caddy`
- Check firewall: `sudo ufw allow 80 && sudo ufw allow 443`

### Upload Fails
- Verify password matches between client and server (see above)
- Check server logs: `journalctl -u db-server -f`
- Verify file is a valid SQLite database

### CORS Errors
- Ensure Caddy CORS headers are configured correctly
- Check browser console for specific CORS error messages

### Large File Upload Timeout
- Increase timeout in `src/db_upload.py` (default: 300 seconds)
- Check server network bandwidth

## Automated Deployment

To automatically upload databases after scraping:

1. Configure environment variables in `.env`
2. Run scheduled scraping
3. After Stage 3 completes, add upload to `src/multi_scheduler.py`

Example modification to scheduler:
```python
# After Stage 3 completes
from src.db_upload import upload_databases_to_server
upload_databases_to_server()
```

## Monitoring

Check server logs:
```bash
# Python server logs
journalctl -u db-server -f

# Caddy logs
journalctl -u caddy -f
```

Check disk space:
```bash
df -h /var/db_files
```

## Backup

Backup the database files directory:
```bash
rsync -avz /var/db_files/ backup-location/db_files/
```
