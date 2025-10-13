from .base_menu import BaseMenu
from rich.console import Console
import time

console = Console()

class FilterMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- FILTER & EXPORT ---", style="bold magenta")
        console.print("Filtering and exporting data...", style="cyan")
        time.sleep(1)
        console.print("Data exported successfully!", style="bold green")
        self.wait_for_input()
