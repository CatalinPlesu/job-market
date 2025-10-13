from rich.console import Console
from src.config_menu import ConfigMenu
from src.scraper_menu import ScraperMenu
from src.debug_menu import DebugMenu
from src.scrape_menu import ScrapeMenu
from src.filter_menu import FilterMenu
from src.results_menu import ResultsMenu

console = Console()


class MenuManager:
    def __init__(self):
        # Single source of truth for menu options
        self.menu_options = [
            {"key": "1", "label": "Print Config", "handler": ConfigMenu()},
            {"key": "2", "label": "Generate Scraper Rules", "handler": ScraperMenu()},
            {"key": "3", "label": "Generate Debug JavaScript", "handler": DebugMenu()},
            {"key": "4", "label": "Scrape Data", "handler": ScrapeMenu()},
            {"key": "5", "label": "Filter & Export", "handler": FilterMenu()},
            {"key": "6", "label": "View Results", "handler": ResultsMenu()},
        ]

        # Create menu dictionary from the list
        self.menus = {opt["key"]: opt["handler"] for opt in self.menu_options}

    def print_menu(self):
        console.clear()
        console.print("="*50, style="bold blue")
        console.print("JOB SCRAPER CONSOLE APP", style="bold yellow")
        console.print("="*50, style="bold blue")

        for option in self.menu_options:
            console.print(f"{option['key']}. {option['label']}", style="green")

        console.print("0. Exit", style="red")
        console.print("-"*50, style="bold blue")

    def run(self):
        while True:
            self.print_menu()
            choice = input("Select an option (0-6): ").strip()

            if choice in self.menus:
                self.menus[choice].execute()
            elif choice == '0':
                console.print("Exiting...", style="bold red")
                break
            else:
                console.print("Invalid option. Please try again.", style="red")
                import time
                time.sleep(1)


if __name__ == "__main__":
    app = MenuManager()
    app.run()
