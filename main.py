from src.scrape_jobs_list import scrape_jobs_list
from src.scrape_job_details import scrape_job_details
from src.scrape_job_recheck import recheck_alive_jobs, recheck_all_jobs
from src.structure_data_with_llm import structure_data_with_llm
from src.process_data import process_data
from src.generate_html_page import generate_html_page
from src.menu import Menu


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


# Main run function
def run():
    menu = Menu()
    menu.set_menu_title("DATA PROCESSING CONSOLE APP")
    menu.set_header("Job Scraping and Processing Pipeline")
    menu.set_footer("Enter to select")
    
    # Register all menu items
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
