"""
Database upload operations module.
Handles uploading database files to the custom server.
"""

import requests
from pathlib import Path
from config.settings import Config
from src.error_logger import get_logger
import os


def upload_databases_to_server(server_url: str = None, password: str = None) -> bool:
    """
    Upload database files to the custom server.
    
    Args:
        server_url: Server URL (if None, uses Config.db_server_url)
        password: Upload password (if None, uses Config.db_server_password)
    
    Returns:
        True if successful, False otherwise
    """
    logger = get_logger()
    
    print("\n" + "="*80)
    print("UPLOAD DATABASES TO SERVER")
    print("="*80)
    print()
    
    # Use provided values or fall back to config
    if server_url is None:
        server_url = getattr(Config, 'db_server_url', os.getenv('DB_SERVER_URL', ''))
    
    if password is None:
        password = getattr(Config, 'db_server_password', os.getenv('DB_SERVER_PASSWORD', ''))
    
    # Validate configuration
    if not server_url:
        logger.error("No server URL configured for database upload")
        print("✗ No server URL configured!")
        print("Please set DB_SERVER_URL in your environment or .env file")
        print("Example: export DB_SERVER_URL='https://db.example.com'")
        return False
    
    if not password:
        logger.error("No password configured for database upload")
        print("✗ No upload password configured!")
        print("Please set DB_SERVER_PASSWORD in your environment or .env file")
        print("Example: export DB_SERVER_PASSWORD='your_secure_password'")
        return False
    
    print(f"Server URL: {server_url}")
    print()
    
    # Prepare database files for upload
    db_files = [
        ("scrape.db", Config.scrape_db_path),
        ("data.db", Config.data_db_path)
    ]
    
    # Check files exist
    for name, path in db_files:
        file_path = Path(path)
        if not file_path.exists():
            logger.error(f"Database file not found: {path}")
            print(f"✗ Database file not found: {name}")
            return False
        
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"Found {name}: {size_mb:.2f} MB")
    
    print()
    
    # Upload files
    try:
        print("Uploading database files...")
        
        # Prepare multipart form data with context managers
        files_to_upload = []
        try:
            for name, path in db_files:
                files_to_upload.append(('files', (name, open(path, 'rb'), 'application/octet-stream')))
            
            # Prepare headers with authentication
            headers = {
                'Authorization': f'Bearer {password}'
            }
            
            # Make the upload request
            upload_url = f"{server_url.rstrip('/')}/upload"
            print(f"Uploading to: {upload_url}")
            
            response = requests.post(
                upload_url,
                files=files_to_upload,
                headers=headers,
                timeout=300  # 5 minutes timeout for large files
            )
        finally:
            # Close file handles
            for _, (_, file_handle, _) in files_to_upload:
                try:
                    file_handle.close()
                except:
                    pass
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Upload successful!")
            
            if 'files' in result:
                print("\nUploaded files:")
                for file_info in result['files']:
                    size_mb = file_info.get('size', 0) / (1024 * 1024)
                    print(f"  • {file_info['filename']}: {size_mb:.2f} MB")
            
            return True
        else:
            # Try to parse JSON error message
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('application/json'):
                try:
                    error_msg = response.json().get('error', 'Unknown error')
                except:
                    error_msg = response.text
            else:
                error_msg = response.text
                
            logger.error(f"Upload failed: HTTP {response.status_code} - {error_msg}")
            print(f"\n✗ Upload failed: HTTP {response.status_code}")
            print(f"Error: {error_msg}")
            return False
    
    except requests.exceptions.Timeout:
        logger.exception("Upload timed out")
        print("\n✗ Upload timed out after 5 minutes")
        return False
    
    except requests.exceptions.ConnectionError as e:
        logger.exception(f"Connection error: {e}")
        print(f"\n✗ Connection error: {e}")
        print("Please check that the server is running and accessible")
        return False
    
    except Exception as e:
        logger.exception(f"Upload failed: {e}")
        print(f"\n✗ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False
