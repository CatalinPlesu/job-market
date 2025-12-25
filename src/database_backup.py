"""
Database backup module.
Handles database backups and cleanup of old backups for both scrape.db and data.db.
"""
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from config.settings import Config


class DatabaseBackup:
    """
    Manages database backups with automatic cleanup.
    Keeps only the specified number of most recent backups.
    """
    
    def __init__(self, db_path: str, backup_dir: str = "backups", keep_days: int = 3):
        """
        Initialize database backup manager.
        
        Args:
            db_path: Path to the database file to backup
            backup_dir: Directory to store backups (default: "backups")
            keep_days: Number of days of backups to keep (default: 3)
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.keep_days = keep_days
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> Path:
        """
        Create a backup of the database.
        
        Returns:
            Path to the created backup file
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            IOError: If backup creation fails
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"{self.db_path.stem}_backup_{timestamp}{self.db_path.suffix}"
        backup_path = self.backup_dir / backup_filename
        
        # Copy database file to backup
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"✓ Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            raise IOError(f"Failed to create backup: {e}")
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backup files older than keep_days.
        
        Returns:
            Number of backups deleted
        """
        if not self.backup_dir.exists():
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=self.keep_days)
        deleted_count = 0
        
        # Find all backup files for this database
        pattern = f"{self.db_path.stem}_backup_*{self.db_path.suffix}"
        backup_files = list(self.backup_dir.glob(pattern))
        
        for backup_file in backup_files:
            try:
                # Get file modification time
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    print(f"✓ Removed old backup: {backup_file.name}")
            
            except Exception as e:
                print(f"Warning: Could not remove backup {backup_file.name}: {e}")
                continue
        
        return deleted_count
    
    def list_backups(self) -> List[Path]:
        """
        List all backup files for this database, sorted by date (newest first).
        
        Returns:
            List of backup file paths
        """
        if not self.backup_dir.exists():
            return []
        
        pattern = f"{self.db_path.stem}_backup_*{self.db_path.suffix}"
        backup_files = list(self.backup_dir.glob(pattern))
        
        # Sort by modification time, newest first
        backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        return backup_files
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to the backup file to restore
            
        Returns:
            True if restore was successful
            
        Raises:
            FileNotFoundError: If backup file doesn't exist
            IOError: If restore fails
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        try:
            # Create a backup of current database before restoring
            if self.db_path.exists():
                pre_restore_backup = self.backup_dir / f"{self.db_path.stem}_pre_restore_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{self.db_path.suffix}"
                shutil.copy2(self.db_path, pre_restore_backup)
                print(f"✓ Created pre-restore backup: {pre_restore_backup.name}")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            print(f"✓ Database restored from: {backup_path.name}")
            return True
        
        except Exception as e:
            raise IOError(f"Failed to restore backup: {e}")
    
    def backup_and_cleanup(self) -> Path:
        """
        Create a backup and clean up old backups in one operation.
        
        Returns:
            Path to the created backup file
        """
        # Create new backup
        backup_path = self.create_backup()
        
        # Clean up old backups
        deleted = self.cleanup_old_backups()
        if deleted > 0:
            print(f"✓ Cleaned up {deleted} old backup(s)")
        
        return backup_path


def backup_all_databases(backup_dir: str = "backups", keep_days: int = 3):
    """
    Backup both scrape.db and data.db databases.
    
    Args:
        backup_dir: Directory to store backups
        keep_days: Number of days of backups to keep
    
    Returns:
        Tuple of (scrape_backup_path, data_backup_path)
    """
    scrape_backup = DatabaseBackup(Config.scrape_db_path, backup_dir, keep_days)
    data_backup = DatabaseBackup(Config.data_db_path, backup_dir, keep_days)
    
    scrape_path = None
    data_path = None
    
    # Backup scrape.db if it exists
    if Path(Config.scrape_db_path).exists():
        scrape_path = scrape_backup.backup_and_cleanup()
    else:
        print(f"⚠ Scrape database not found: {Config.scrape_db_path}")
    
    # Backup data.db if it exists
    if Path(Config.data_db_path).exists():
        data_path = data_backup.backup_and_cleanup()
    else:
        print(f"⚠ Data database not found: {Config.data_db_path}")
    
    return scrape_path, data_path
