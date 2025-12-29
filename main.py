from src.scrape_jobs_list import scrape_jobs_list
from src.scrape_job_details import scrape_job_details
from src.scrape_job_recheck import recheck_alive_jobs, recheck_all_jobs
from src.structure_data_with_llm import structure_data_with_llm
from src.process_data import process_data
from src.generate_html_page_fixed import generate_html_page
from src.menu import Menu
from src.scheduled_scraper import run_all_stages_scheduled
from src.scheduler import Scheduler
from src.database_backup import DatabaseBackup
from config.settings import Config
from datetime import datetime
from pathlib import Path


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


class ProcessDataItem:
    def get_item_description(self):
        return "Process Data"
    
    def execute(self):
        process_data()
        return True


class GenerateHtmlItem:
    def get_item_description(self):
        return "Generate HTML Page"
    
    def execute(self):
        generate_html_page()
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
        print("  • Stage 3: Daily at 00:00 (slow)")
        print("    - Stage 3: Re-check alive jobs")
        print("\nFeatures:")
        print("  • Separate schedules optimized for each stage's speed")
        print("  • Database backup before each run (keeps last 3 days)")
        print("  • Error-only logging (weekly log files)")
        print("  • Daily reports with statistics per site")
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
    menu.register_item(ProcessDataItem())
    menu.register_item(GenerateHtmlItem())
    menu.register_item(DatabaseRollbackItem())
    
    # Run the menu
    menu.run()


if __name__ == "__main__":
    run()
