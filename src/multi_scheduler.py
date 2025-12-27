"""
Multi-scheduler module for running multiple tasks on different schedules.
Coordinates multiple schedulers to run different tasks at different intervals.
"""
import threading
from typing import List, Tuple, Callable
from src.scheduler import Scheduler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class MultiScheduler:
    """
    Manages multiple schedulers running concurrently.
    Each scheduler can have its own schedule (daily, hourly, etc.).
    """
    
    def __init__(self):
        """Initialize the multi-scheduler."""
        self.schedulers: List[Tuple[Scheduler, Callable, str]] = []
        self.threads: List[threading.Thread] = []
        self.running = False
        self.console = Console()
    
    def add_schedule(self, scheduler: Scheduler, task: Callable, task_name: str):
        """
        Add a scheduled task.
        
        Args:
            scheduler: Scheduler instance with configured schedule
            task: Callable to execute
            task_name: Name of the task for logging
        """
        self.schedulers.append((scheduler, task, task_name))
    
    def start(self, check_interval: int = 60):
        """
        Start all schedulers.
        
        Args:
            check_interval: Seconds between schedule checks (default: 60)
        """
        self.running = True
        
        # Create a nice table showing the schedulers
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Task", style="cyan", no_wrap=True)
        table.add_column("Schedule", style="yellow")
        table.add_column("Status", justify="center")
        
        for scheduler, _, task_name in self.schedulers:
            if scheduler.interval_minutes:
                schedule_str = f"Every {scheduler.interval_minutes} minutes"
            else:
                schedule_str = f"Daily at {scheduler.schedule_time.strftime('%H:%M')}"
            
            table.add_row(task_name, schedule_str, "[green]⟳ Starting[/green]")
        
        panel = Panel(
            table,
            title="[bold cyan]Multi-Scheduler Started[/bold cyan]",
            subtitle=f"[dim]Managing {len(self.schedulers)} scheduled tasks[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        # Add spacing before panel
        self.console.print()
        self.console.print(panel)
        self.console.print("[dim]Press Ctrl+C to stop all schedulers[/dim]\n")
        
        # Start each scheduler in its own thread
        for scheduler, task, task_name in self.schedulers:
            thread = threading.Thread(
                target=scheduler.run_with_monitoring,
                args=(task, task_name, check_interval),
                daemon=False
            )
            thread.start()
            self.threads.append(thread)
    
    def stop(self):
        """Stop all schedulers."""
        self.console.print("\n[yellow]⚠ Stopping all schedulers...[/yellow]")
        self.running = False
        
        # Stop all schedulers
        for scheduler, _, _ in self.schedulers:
            scheduler.stop()
        
        # Wait for all threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        self.console.print("[green]✓ All schedulers stopped.[/green]\n")
    
    def wait(self):
        """Wait for all scheduler threads to complete."""
        try:
            for thread in self.threads:
                thread.join()
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]⚠ Stopping multi-scheduler...[/yellow]")
            self.stop()


def run_improved_scheduler():
    """
    Run the improved scheduler with separate schedules for different stages.
    - Stage 1 & 2: Every hour (fast with early stopping) - runs immediately on first startup
    - Stage 3: Once daily at midnight (slow)
    """
    from src.scheduled_scraper import run_stages_1_and_2, run_stage_3_only
    
    multi_scheduler = MultiScheduler()
    
    # Schedule Stage 1 & 2 to run every hour, with immediate first run
    hourly_scheduler = Scheduler(
        interval_minutes=60,
        state_file_name="scheduler_state_hourly.json",
        run_immediately=True  # Run stages 1 & 2 immediately on startup
    )
    multi_scheduler.add_schedule(
        hourly_scheduler,
        run_stages_1_and_2,
        "Stages 1 & 2 (Hourly)"
    )
    
    # Schedule Stage 3 to run daily at midnight (no immediate run)
    daily_scheduler = Scheduler(
        schedule_time_hour=0,
        schedule_time_minute=0,
        state_file_name="scheduler_state_daily.json",
        run_immediately=False  # Wait for scheduled time
    )
    multi_scheduler.add_schedule(
        daily_scheduler,
        run_stage_3_only,
        "Stage 3 (Daily)"
    )
    
    # Start all schedulers
    multi_scheduler.start(check_interval=60)
    multi_scheduler.wait()
