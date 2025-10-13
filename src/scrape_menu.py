from .base_menu import BaseMenu
from rich.console import Console
import time

console = Console()

class ScrapeMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- SCRAPE DATA ---", style="bold magenta")
        console.print("Starting scraping workflow...", style="cyan")
        time.sleep(0.5)
        console.print("Step 1: Collecting job URLs", style="yellow")
        time.sleep(1)
        console.print("Step 2: Scraping job details", style="yellow")
        time.sleep(1)
        console.print("Scraping completed successfully!", style="bold green")
        self.wait_for_input()
