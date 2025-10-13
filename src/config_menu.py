import json
from .base_menu import BaseMenu
from rich.console import Console
from config.settings import Config

console = Console()


class ConfigMenu(BaseMenu):
    def execute(self):
        self.clear_screen()
        console.print("--- PRINT CONFIG ---", style="bold magenta")

        console.print("\nConfiguration from config.py:", style="bold cyan")
        console.print(f"Job Sites:", style="yellow")
        for site in Config.job_sites:
            console.print(f"  - {site.strip()}")
        console.print(f"LLM API: {Config.llm_api.strip()}")
        console.print(f"LLM Model: {Config.llm_model}")

        # API Key status with color coding
        api_key_status = "SET" if Config.llm_api_key else "EMPTY"
        api_key_style = "bold green" if Config.llm_api_key else "bold red"
        console.print(f"LLM API Key: {api_key_status}", style=api_key_style)

        console.print("\nContents of scraper_rules.json:", style="bold cyan")
        try:
            with open(Config.scraper_rules, 'r') as f:
                data = json.load(f)
                console.print_json(data=data)  # Use the data parameter
        except FileNotFoundError:
            console.print(f"{Config.scraper_rules} not found", style="red")

        self.wait_for_input()
