from .base_menu import BaseMenu
from rich.console import Console
from rich.table import Table

console = Console()

class ResultsMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- VIEW RESULTS ---", style="bold magenta")
        
        table = Table(title="Recent Jobs", show_header=True, header_style="bold magenta")
        table.add_column("Title", style="dim", width=25)
        table.add_column("Company", style="dim", width=20)
        table.add_column("Location", style="dim", width=15)
        table.add_column("Date", style="dim", width=10)
        
        # Sample job data
        jobs = [
            ("Software Engineer", "Tech Corp", "New York", "2023-10-15"),
            ("Data Analyst", "Data Inc", "San Francisco", "2023-10-14"),
            ("Product Manager", "Prod Co", "Austin", "2023-10-13"),
            ("UX Designer", "Design Ltd", "Remote", "2023-10-12"),
            ("DevOps Engineer", "Cloud Sys", "Seattle", "2023-10-11")
        ]
        
        for job in jobs:
            table.add_row(job[0], job[1], job[2], job[3])
        
        console.print(table)
        console.print(f"Total jobs: {len(jobs)}", style="bold green")
        self.wait_for_input()
