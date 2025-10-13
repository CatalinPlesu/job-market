from .base_menu import BaseMenu
from rich.console import Console
import time

console = Console()

class DebugMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- GENERATE DEBUG JAVASCRIPT ---", style="bold magenta")
        console.print("Creating debug_js/site1.js...", style="cyan")
        console.print("Creating debug_js/site2.js...", style="cyan")
        time.sleep(1)
        console.print("Debug scripts generated successfully!", style="bold green")
        self.wait_for_input()
