from src.scrape_jobs_list import scrape_jobs_list
from src.scrape_job_details import scrape_job_details
from src.scrape_job_recheck import recheck_alive_jobs, recheck_all_jobs
from src.structure_data_with_llm import structure_data_with_llm
from src.process_data import process_data
from src.generate_html_page import generate_html_page
from src.menu import Menu
from src.scheduled_scraper import run_all_stages_scheduled
from src.scheduler import Scheduler


# Menu Item Classes
class ScrapeJobsListItem:
    def get_item_description(self):
        return "Scrape Job Listings (Stage 1)"
    
    def execute(self):
        scrape_jobs_list()
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


class ScheduledScrapingItem:
    def get_item_description(self):
        return "Run All Stages on Schedule (with Logging & Reports)"
    
    def execute(self):
        print("\n" + "="*80)
        print("SCHEDULED SCRAPING - SELF-MANAGED SCHEDULER")
        print("="*80)
        print("\nThis will run all 3 scraping stages:")
        print("  1. Stage 1: Scrape job listings")
        print("  2. Stage 2: Get job details")
        print("  3. Stage 3: Re-check alive jobs")
        print("\nFeatures:")
        print("  • Database backup before each run (keeps last 3 days)")
        print("  • Error-only logging (weekly log files)")
        print("  • Daily reports with statistics per site and aggregated")
        print("\nSchedule: Daily at 00:00 (midnight)")
        print("\nOptions:")
        print("  1. Run once NOW")
        print("  2. Start scheduler (will wait for scheduled time)")
        print("  0. Cancel")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            # Run immediately
            print("\nRunning all stages immediately...")
            try:
                run_all_stages_scheduled()
                print("\n✓ All stages completed successfully!")
            except Exception as e:
                print(f"\n✗ Error during execution: {e}")
        
        elif choice == "2":
            # Start scheduler
            print("\nStarting scheduler...")
            print("The scheduler will monitor the schedule and run automatically at 00:00.")
            print("Press Ctrl+C to stop.\n")
            
            scheduler = Scheduler(schedule_time_hour=0, schedule_time_minute=0)
            try:
                scheduler.run_with_monitoring(
                    task=run_all_stages_scheduled,
                    task_name="Scheduled Scraping (All Stages)",
                    check_interval=60  # Check every minute
                )
            except KeyboardInterrupt:
                print("\nScheduler stopped by user.")
        
        else:
            print("\nCancelled.")
        
        return True


# Main run function
def run():
    menu = Menu()
    menu.set_menu_title("DATA PROCESSING CONSOLE APP")
    menu.set_header("Job Scraping and Processing Pipeline")
    menu.set_footer("Enter to select")
    
    # Register all menu items
    menu.register_item(ScheduledScrapingItem())  # New scheduled scraping option
    menu.register_item(ScrapeJobsListItem())
    menu.register_item(ScrapeJobDetailsItem())
    menu.register_item(RecheckAliveJobsItem())
    menu.register_item(RecheckAllJobsItem())
    menu.register_item(StructureDataItem())
    menu.register_item(ProcessDataItem())
    menu.register_item(GenerateHtmlItem())
    
    # Run the menu
    menu.run()


if __name__ == "__main__":
    run()
