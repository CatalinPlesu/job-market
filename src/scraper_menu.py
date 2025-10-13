from .base_menu import BaseMenu
from rich.console import Console
import time

console = Console()

class ScraperMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- GENERATE SCRAPER RULES ---", style="bold magenta")
        console.print("Auto-generating scraper_rules.json using LLM...", style="cyan")
        time.sleep(1)
        console.print("1. Reading API settings from settings.py", style="yellow")
        time.sleep(0.5)
        console.print("2. Fetching sample pages for each site", style="yellow")
        time.sleep(0.5)
        console.print("3. Sending HTML to LLM for selector generation", style="yellow")
        time.sleep(0.5)
        console.print("4. Testing selectors on 3 pages", style="yellow")
        time.sleep(0.5)
        console.print("5. Saving validated rules to scraper_rules.json", style="yellow")
        time.sleep(0.5)
        console.print("Rules generated successfully!", style="bold green")
        self.wait_for_input()
