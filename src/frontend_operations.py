"""
Frontend operations module.
Handles copying databases to frontend and pushing to git.
"""
import shutil
from pathlib import Path
from datetime import datetime
from config.settings import Config
from src.frontend_git_operations import FrontendGitOperations
from src.error_logger import get_logger


def copy_databases_to_frontend(dest_dir: str = "frontend/api") -> bool:
    """
    Copy both database files to the frontend/api directory.
    
    Args:
        dest_dir: Destination directory path (default: frontend/api)
    
    Returns:
        True if successful, False otherwise
    """
    logger = get_logger()
    dest_path = Path(dest_dir)
    
    try:
        # Create destination directory if it doesn't exist
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Copy scrape.db
        source_scrape = Path(Config.scrape_db_path)
        dest_scrape = dest_path / "scrape.db"
        
        if not source_scrape.exists():
            logger.error(f"Source database not found: {source_scrape}")
            print(f"✗ Source database not found: {source_scrape}")
            return False
        
        print(f"Copying {source_scrape.name}...")
        shutil.copy2(source_scrape, dest_scrape)
        size_mb = source_scrape.stat().st_size / (1024 * 1024)
        print(f"✓ {source_scrape.name} copied ({size_mb:.2f} MB)")
        
        # Copy data.db
        source_data = Path(Config.data_db_path)
        dest_data = dest_path / "data.db"
        
        if not source_data.exists():
            logger.error(f"Source database not found: {source_data}")
            print(f"✗ Source database not found: {source_data}")
            return False
        
        print(f"Copying {source_data.name}...")
        shutil.copy2(source_data, dest_data)
        size_mb = source_data.stat().st_size / (1024 * 1024)
        print(f"✓ {source_data.name} copied ({size_mb:.2f} MB)")
        
        print(f"\n✓ Database files copied successfully to {dest_path}/")
        return True
    
    except Exception as e:
        logger.exception(f"Failed to copy databases: {e}")
        print(f"\n✗ Error copying databases: {e}")
        return False


def copy_databases_and_push(remote_url: str = None) -> bool:
    """
    Copy databases to frontend and push to git repository.
    
    This function:
    1. Copies database files to frontend/api
    2. Initializes/updates git repository in frontend
    3. Commits and pushes changes to remote
    
    Args:
        remote_url: Git remote URL (if None, uses Config.frontend_git_remote_url)
    
    Returns:
        True if successful, False otherwise
    """
    logger = get_logger()
    
    print("\n" + "="*80)
    print("COPY DATABASES AND PUSH TO GIT")
    print("="*80)
    print()
    
    # Use provided remote_url or fall back to config
    if remote_url is None:
        remote_url = Config.frontend_git_remote_url
    
    # Validate remote URL
    if not remote_url:
        logger.error("No remote URL configured for frontend git operations")
        print("✗ No remote URL configured!")
        print("Please set FRONTEND_GIT_REMOTE_URL in your environment")
        return False
    
    # Step 1: Copy databases
    print("Step 1: Copying databases to frontend/api...")
    if not copy_databases_to_frontend():
        return False
    
    print()
    
    # Step 2: Git operations
    print("Step 2: Pushing to git...")
    print(f"Remote: {remote_url}")
    print(f"Branch: {Config.frontend_git_branch}")
    print(f"Approach: {'Fresh (force push)' if Config.frontend_git_use_fresh_approach else 'Incremental'}")
    print()
    
    try:
        git_ops = FrontendGitOperations(frontend_dir="frontend")
        
        # Generate commit message with timestamp
        commit_message = f"Update databases - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Choose approach based on configuration
        if Config.frontend_git_use_fresh_approach:
            # Fresh approach: remove .git, init, add, commit, force push
            print("Using fresh approach (smaller repo size)...")
            success, message = git_ops.add_commit_push_fresh(
                commit_message=commit_message,
                remote_url=remote_url,
                branch=Config.frontend_git_branch
            )
        else:
            # Incremental approach: add, commit, push
            print("Using incremental approach...")
            success, message = git_ops.add_commit_push_incremental(
                commit_message=commit_message,
                remote_url=remote_url,
                branch=Config.frontend_git_branch
            )
        
        if success:
            print(f"✓ {message}")
            return True
        else:
            print(f"✗ {message}")
            logger.error(f"Failed to push frontend: {message}")
            return False
    
    except Exception as e:
        logger.exception(f"Failed to push frontend: {e}")
        print(f"✗ Error: {e}")
        return False
