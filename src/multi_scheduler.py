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
    - Stage 3: Once daily at midnight - complete workflow:
      * Recheck alive jobs
      * Process new jobs with LLM
      * Copy databases to frontend
      * Push to GitHub
    
    For testing, set DEBUG_RUN_STAGE3_NOW=true in .env to run Stage 3 immediately.
    """
    from src.scheduled_scraper import run_stages_1_and_2, run_stage_3_only
    from config.settings import Config
    
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
    
    # Schedule Stage 3 to run daily at midnight (or immediately if DEBUG_RUN_STAGE3_NOW is set)
    # Includes: recheck alive jobs, LLM processing, DB copy, and GitHub push
    run_stage3_immediately = Config.debug_run_stage3_now
    daily_scheduler = Scheduler(
        schedule_time_hour=0,
        schedule_time_minute=0,
        state_file_name="scheduler_state_daily.json",
        run_immediately=run_stage3_immediately  # Run immediately if debug flag is set
    )
    multi_scheduler.add_schedule(
        daily_scheduler,
        run_stage_3_only,
        "Stage 3 + LLM + Deploy (Daily)"
    )
    
    # Display debug info if enabled (before starting the scheduler)
    if run_stage3_immediately:
        multi_scheduler.console.print("\n[yellow]⚠ DEBUG MODE: Stage 3 will run immediately![/yellow]")
        multi_scheduler.console.print("[yellow]  Set DEBUG_RUN_STAGE3_NOW=false in .env to disable[/yellow]\n")
    
    # Start all schedulers
    multi_scheduler.start(check_interval=60)
    multi_scheduler.wait()
