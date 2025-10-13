from rich.console import Console
import os
import time

console = Console()

class BaseMenu:
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def execute(self):
        raise NotImplementedError("Subclasses must implement execute method")
    
    def wait_for_input(self):
        input("\nPress Enter to return to menu...")
