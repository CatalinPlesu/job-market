from src.scrape_jobs_list import scrape_jobs_list
from src.scrape_job_details import scrape_job_details
from src.scrape_job_recheck import recheck_alive_jobs, recheck_all_jobs
from src.structure_data_with_llm import structure_data_with_llm
from src.process_data import process_data
from src.menu import Menu
from src.scheduled_scraper import run_all_stages_scheduled
from src.scheduler import Scheduler
from src.database_backup import DatabaseBackup
from config.settings import Config
from datetime import datetime
from pathlib import Path
import shutil


# Menu Item Classes
class ScrapeJobsListItem:
    def get_item_description(self):
        return "Scrape Job Listings (Stage 1 - Smart Mode)"
    
    def execute(self):
        scrape_jobs_list(full_scrape=False)
        return True


class ScrapeJobsListFullItem:
    def get_item_description(self):
        return "Scrape Job Listings (Stage 1 - Full Scrape)"
    
    def execute(self):
        scrape_jobs_list(full_scrape=True)
        return True


class ScrapeJobDetailsItem:
    def get_item_description(self):
        return "Scrape Job Details (Stage 2)"
    
    def execute(self):
        scrape_job_details()
        return True


class RecheckAliveJobsItem:
    def get_item_description(self):
        return "Re-check Alive Jobs"
    
    def execute(self):
        recheck_alive_jobs()
        return True


class RecheckAllJobsItem:
    def get_item_description(self):
        return "Re-check All (Including Rotten) Jobs"
    
    def execute(self):
        recheck_all_jobs()
        return True


class StructureDataItem:
    def get_item_description(self):
        return "Structure Data with LLM"
    
    def execute(self):
        structure_data_with_llm()
        return True





class UploadDatabaseItem:
    def get_item_description(self):
        return "Upload Database Files to Server"
    
    def execute(self):
        from src.db_upload import upload_databases_to_server
        import os
        
        print("\n" + "="*80)
        print("UPLOAD DATABASES TO SERVER")
        print("="*80)
        print("\nThis will upload both database files to your custom server:")
        print("  • scrape.db (raw scraped data)")
        print("  • data.db (processed data)")
        print()
        
        # Check if server URL is configured
        server_url = os.getenv('DB_SERVER_URL', '')
        password = os.getenv('DB_SERVER_PASSWORD', '')
        
        if not server_url:
            print("⚠ Warning: No server URL configured!")
            print("Please set DB_SERVER_URL in your environment or .env file")
            print("Example: export DB_SERVER_URL='https://database.catalinplesu.xyz'")
            print()
            
            server_url = input("Enter server URL (or press Enter to skip): ").strip()
            if not server_url:
                print("\nCancelled.")
                return True
        else:
            print(f"Server URL: {server_url}")
        
        if not password:
            print("\n⚠ Warning: No upload password configured!")
            print("Please set DB_SERVER_PASSWORD in your environment or .env file")
            print()
            
            password = input("Enter upload password (or press Enter to skip): ").strip()
            if not password:
                print("\nCancelled.")
                return True
        
        print()
        confirm = input("Continue with upload? (yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            print("\nCancelled.")
            return True
        
        print()
        
        # Execute the upload
        try:
            success = upload_databases_to_server(server_url, password)
            if success:
                print("\n✓ Database files uploaded successfully!")
            else:
                print("\n✗ Failed to upload database files. Check logs for details.")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return True


class PushFrontendItem:
    def get_item_description(self):
        return "Push Frontend to Git"
    
    def execute(self):
        from src.frontend_operations import git_commit_and_push_only
        
        print("\n" + "="*80)
        print("PUSH FRONTEND TO GIT")
        print("="*80)
        print("\nThis will commit and push frontend changes to git")
        print("(Database files are uploaded separately to the server)")
        print()
        
        # Check if remote URL is configured
        if not Config.frontend_git_remote_url:
            print("⚠ Warning: No remote URL configured!")
            print("Please set FRONTEND_GIT_REMOTE_URL in your environment or .env file")
            print("Example: export FRONTEND_GIT_REMOTE_URL='https://github.com/user/repo.git'")
            print()
            
            remote_url = input("Enter remote URL (or press Enter to skip): ").strip()
            if not remote_url:
                print("\nCancelled.")
                return True
        else:
            remote_url = Config.frontend_git_remote_url
            print(f"Remote URL: {remote_url}")
            print(f"Branch: {Config.frontend_git_branch}")
            print(f"Approach: {'Fresh (force push)' if Config.frontend_git_use_fresh_approach else 'Incremental'}")
            print()
        
        confirm = input("Continue? (yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            print("\nCancelled.")
            return True
        
        print()
        
        # Execute the operation
        try:
            success = git_commit_and_push_only(remote_url)
            if success:
                print("\n✓ Frontend pushed successfully!")
            else:
                print("\n✗ Failed to push frontend. Check logs for details.")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return True


class DatabaseRollbackItem:
    def get_item_description(self):
        return "Database Rollback"
    
    def execute(self):
        print("\n" + "="*80)
        print("DATABASE ROLLBACK")
        print("="*80)
        print("\nRestore a database from a backup copy.")
        print()
        
        # Step 1: Choose database
        print("Select database to restore:")
        print("  1. scrape.db (raw scraped data)")
        print("  2. data.db (processed data)")
        print("  0. Cancel")
        
        db_choice = input("\nEnter choice: ").strip()
        
        if db_choice == "0":
            print("\nCancelled.")
            return True
        
        # Determine which database was selected
        if db_choice == "1":
            db_path = Config.scrape_db_path
            db_name = "scrape.db"
        elif db_choice == "2":
            db_path = Config.data_db_path
            db_name = "data.db"
        else:
            print("\n✗ Invalid choice.")
            return True
        
        # Step 2: List available backups
        backup_manager = DatabaseBackup(db_path, backup_dir="backups")
        backups = backup_manager.list_backups()
        
        if not backups:
            print(f"\n✗ No backups found for {db_name}")
            return True
        
        print(f"\nAvailable backups for {db_name}:")
        print("-" * 80)
        
        for idx, backup_path in enumerate(backups, start=1):
            # Get file stats
            stat_info = backup_path.stat()
            size_mb = stat_info.st_size / (1024 * 1024)
            created_time = datetime.fromtimestamp(stat_info.st_mtime)
            
            print(f"{idx}. {backup_path.name}")
            print(f"   Created: {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {size_mb:.2f} MB")
            print()
        
        print("0. Cancel")
        
        # Step 3: Select backup to restore
        backup_choice = input("\nSelect backup to restore: ").strip()
        
        if backup_choice == "0":
            print("\nCancelled.")
            return True
        
        try:
            backup_idx = int(backup_choice)
            if backup_idx < 1 or backup_idx > len(backups):
                print("\n✗ Invalid selection.")
                return True
            
            selected_backup = backups[backup_idx - 1]
            
            # Step 4: Confirm restoration
            print(f"\nYou are about to restore {db_name} from:")
            print(f"  {selected_backup.name}")
            
            confirm = input("\nAre you sure? This will overwrite the current database. (yes/no): ").strip().lower()
            
            if confirm not in ("yes", "y"):
                print("\nCancelled.")
                return True
            
            # Step 5: Perform restoration
            print("\nRestoring database...")
            backup_manager.restore_backup(selected_backup)
            print(f"\n✓ Successfully restored {db_name}!")
        
        except ValueError:
            print("\n✗ Invalid input. Please enter a number.")
        except (FileNotFoundError, IOError) as e:
            print(f"\n✗ Error during restoration: {e}")
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
        
        return True


class ScheduledScrapingItem:
    def get_item_description(self):
        return "Run Scheduled Scraping (Stages 1&2 hourly, Stage 3 daily)"
    
    def execute(self):
        print("\n" + "="*80)
        print("SCHEDULED SCRAPING")
        print("="*80)
        print("\nThis will run stages on optimized schedules:")
        print("  • Stage 1 & 2: Every HOUR (fast with early stopping)")
        print("    - Stage 1: Scrape job listings (stops at 100+ consecutive existing)")
        print("    - Stage 2: Get job details")
        print("  • Stage 3: Daily at 00:00 (complete workflow)")
        print("    - Stage 3a: Re-check alive jobs")
        print("    - Stage 3b: Process new jobs with LLM")
        print("    - Stage 3c: Copy databases to frontend")
        print("    - Stage 3d: Push to GitHub")
        print("\nFeatures:")
        print("  • Separate schedules optimized for each stage's speed")
        print("  • Database backup before each run (keeps last 3 days)")
        print("  • Error-only logging (weekly log files)")
        print("  • Daily reports with statistics per site")
        print("  • Full autonomy - no manual intervention required")
        print("\nPress Ctrl+C to stop the scheduler.\n")
        
        try:
            from src.multi_scheduler import run_improved_scheduler
            run_improved_scheduler()
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
        
        return True


# Main run function
def run():
    menu = Menu()
    menu.set_menu_title("DATA PROCESSING CONSOLE APP")
    menu.set_header("Job Scraping and Processing Pipeline")
    menu.set_footer("Enter to select")
    
    # Register all menu items
    menu.register_item(ScheduledScrapingItem())  # Hourly stages 1&2, daily stage 3
    menu.register_item(ScrapeJobsListItem())
    menu.register_item(ScrapeJobsListFullItem())  # Full scrape without early termination
    menu.register_item(ScrapeJobDetailsItem())
    menu.register_item(RecheckAliveJobsItem())
    menu.register_item(RecheckAllJobsItem())
    menu.register_item(StructureDataItem())
    menu.register_item(UploadDatabaseItem())  # Upload databases to custom server
    menu.register_item(PushFrontendItem())  # Push frontend to git (no DB files)
    menu.register_item(DatabaseRollbackItem())
    
    # Run the menu
    menu.run()


if __name__ == "__main__":
    run()
