from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Select, Label, Input, TextArea
from textual.screen import Screen
from textual.reactive import reactive
import json
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "scraping_targets": [
                {
                    "name": "Moldova Job Board",
                    "url": "https://example.com/jobs",
                    "selectors": {
                        "job_title": ".job-title",
                        "company": ".company-name",
                        "location": ".job-location",
                        "salary": ".salary",
                        "description": ".job-description",
                        "date_posted": ".post-date"
                    }
                }
            ],
            "analysis_settings": {
                "salary_analysis": True,
                "location_analysis": True,
                "company_analysis": True,
                "skill_extraction": True
            },
            "output_settings": {
                "html_template": "default_template.html",
                "output_dir": "output",
                "include_charts": True
            }
        }
    
    def save_config(self) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_scraping_targets(self) -> list:
        """Get list of scraping targets"""
        return self.config.get("scraping_targets", [])
    
    def add_scraping_target(self, target: Dict[str, Any]) -> None:
        """Add a new scraping target"""
        if "scraping_targets" not in self.config:
            self.config["scraping_targets"] = []
        self.config["scraping_targets"].append(target)
    
    def remove_scraping_target(self, index: int) -> None:
        """Remove a scraping target by index"""
        if "scraping_targets" in self.config and 0 <= index < len(self.config["scraping_targets"]):
            self.config["scraping_targets"].pop(index)
    
    def get_analysis_settings(self) -> Dict[str, Any]:
        """Get analysis settings"""
        return self.config.get("analysis_settings", {})
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get output settings"""
        return self.config.get("output_settings", {})


class ConfigScreen(Screen):
    """Screen for viewing configuration"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Configuration", classes="title"),
            Container(
                Label("Scraping Targets:"),
                TextArea(json.dumps(config.get_scraping_targets(), indent=2), id="view-targets", language="json", read_only=True),
                classes="config-container"
            ),
            Container(
                Label("Analysis Settings:"),
                TextArea(json.dumps(config.get_analysis_settings(), indent=2), id="view-analysis", language="json", read_only=True),
                classes="config-container"
            ),
            Container(
                Button("Back", id="back-config"),
                classes="button-container"
            ),
            classes="config-screen"
        )

class MenuScreen(Screen):
    """Main menu screen"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Job Market Analysis", classes="title"),
            Container(
                Button("View Configuration", id="view-config", variant="default"),
                Button("Scrape Data", id="scrape-data", variant="default"),
                Button("Analyze Data", id="analyze-data", variant="default"),
                Button("Generate HTML Site", id="generate-html", variant="default"),
                Button("Quit", id="quit-app", variant="primary"),
                classes="menu-buttons"
            ),
            classes="menu-container"
        )

class JobMarketApp(App):
    """Main application"""
    
    CSS_PATH = "styles.tcss"
    config = Config()
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield MenuScreen()
        yield Footer()
    
    def action_quit(self) -> None:
        self.exit()
    
    def action_back(self) -> None:
        # Implementation for back navigation
        pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        button_id = event.button.id
        
        if button_id == "view-config":
            self.push_screen(ConfigScreen())
        elif button_id == "scrape-data":
            self.action_scrape()
        elif button_id == "analyze-data":
            self.action_analyze()
        elif button_id == "generate-html":
            self.action_generate()
        elif button_id == "quit-app":
            self.action_quit()
        elif button_id == "back-config":
            self.pop_screen()
    
    def action_scrape(self) -> None:
        """Scrape data from configured targets"""
        targets = self.config.get_scraping_targets()
        if not targets:
            self.notify("No scraping targets configured", severity="warning")
            return
        
        # Placeholder for scraping logic
        self.notify(f"Scraping {len(targets)} targets...")
    
    def action_analyze(self) -> None:
        """Analyze scraped data"""
        # Placeholder for analysis logic
        self.notify("Analyzing data...")
    
    def action_generate(self) -> None:
        """Generate HTML site"""
        # Placeholder for HTML generation logic
        self.notify("Generating HTML site...")

if __name__ == "__main__":
    app = JobMarketApp()
    app.run()
