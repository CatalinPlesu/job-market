"""
Rich-based logging and progress tracking for scraping operations.
Provides colorful, interactive live views with progress bars and status panels.
"""
from rich.console import Console
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn
)
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from datetime import datetime
from typing import Dict, Optional
import threading


class RichLogger:
    """
    Rich-based logger for scraping operations with live progress tracking.
    Provides colorful console output, progress bars, and live status panels.
    """
    
    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=False
        )
        
        # Track tasks by site and stage
        self.tasks: Dict[str, Dict[str, int]] = {}
        self.task_lock = threading.Lock()
        
        # Track site status
        self.site_status: Dict[str, Dict] = {}
        self.status_lock = threading.Lock()
        
        # Live display
        self.live: Optional[Live] = None
        self.is_live = False
    
    def print_header(self, title: str, subtitle: str = ""):
        """Print a formatted header."""
        self.console.print()
        self.console.rule(f"[bold cyan]{title}", style="cyan")
        if subtitle:
            self.console.print(f"[dim]{subtitle}[/dim]", justify="center")
        self.console.print()
    
    def print_section(self, title: str):
        """Print a section header."""
        self.console.print()
        self.console.print(f"[bold yellow]▶[/bold yellow] {title}")
        self.console.print()
    
    def print_info(self, message: str, prefix: str = ""):
        """Print an info message."""
        if prefix:
            self.console.print(f"[blue]•[/blue] [bold]{prefix}:[/bold] {message}")
        else:
            self.console.print(f"[blue]•[/blue] {message}")
    
    def print_success(self, message: str, prefix: str = ""):
        """Print a success message."""
        if prefix:
            self.console.print(f"[green]✓[/green] [bold]{prefix}:[/bold] {message}")
        else:
            self.console.print(f"[green]✓[/green] {message}")
    
    def print_warning(self, message: str, prefix: str = ""):
        """Print a warning message."""
        if prefix:
            self.console.print(f"[yellow]⚠[/yellow] [bold]{prefix}:[/bold] {message}")
        else:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
    
    def print_error(self, message: str, prefix: str = ""):
        """Print an error message."""
        if prefix:
            self.console.print(f"[red]✗[/red] [bold]{prefix}:[/bold] {message}")
        else:
            self.console.print(f"[red]✗[/red] {message}")
    
    def start_stage(self, stage_name: str, site_name: str, total_items: int = 0) -> int:
        """
        Start tracking a stage for a site.
        
        Args:
            stage_name: Name of the stage (e.g., "Stage 1", "Stage 2")
            site_name: Name of the site
            total_items: Total number of items to process (0 for indeterminate)
        
        Returns:
            Task ID for progress tracking
        """
        description = f"[{stage_name}] {site_name}"
        
        with self.task_lock:
            if site_name not in self.tasks:
                self.tasks[site_name] = {}
            
            if total_items > 0:
                task_id = self.progress.add_task(description, total=total_items)
            else:
                task_id = self.progress.add_task(description, total=None)
            
            self.tasks[site_name][stage_name] = task_id
        
        # Update site status
        with self.status_lock:
            if site_name not in self.site_status:
                self.site_status[site_name] = {}
            self.site_status[site_name][stage_name] = {
                'status': 'running',
                'started_at': datetime.now(),
                'completed': 0,
                'total': total_items
            }
        
        return task_id
    
    def update_progress(self, site_name: str, stage_name: str, advance: int = 1):
        """Update progress for a stage."""
        with self.task_lock:
            if site_name in self.tasks and stage_name in self.tasks[site_name]:
                task_id = self.tasks[site_name][stage_name]
                self.progress.update(task_id, advance=advance)
        
        with self.status_lock:
            if site_name in self.site_status and stage_name in self.site_status[site_name]:
                self.site_status[site_name][stage_name]['completed'] += advance
    
    def complete_stage(self, site_name: str, stage_name: str, status: str = "success"):
        """
        Mark a stage as complete.
        
        Args:
            site_name: Name of the site
            stage_name: Name of the stage
            status: Completion status ('success', 'error', 'warning')
        """
        with self.task_lock:
            if site_name in self.tasks and stage_name in self.tasks[site_name]:
                task_id = self.tasks[site_name][stage_name]
                self.progress.update(task_id, completed=True)
        
        with self.status_lock:
            if site_name in self.site_status and stage_name in self.site_status[site_name]:
                self.site_status[site_name][stage_name]['status'] = status
                self.site_status[site_name][stage_name]['completed_at'] = datetime.now()
    
    def set_stage_status_message(self, site_name: str, stage_name: str, message: str):
        """Set a status message for a stage."""
        with self.status_lock:
            if site_name in self.site_status and stage_name in self.site_status[site_name]:
                self.site_status[site_name][stage_name]['message'] = message
    
    def get_status_table(self) -> Table:
        """Generate a status table showing all sites and their stages."""
        table = Table(title="Scraping Status", show_header=True, header_style="bold magenta")
        table.add_column("Site", style="cyan", no_wrap=True)
        table.add_column("Stage", style="yellow")
        table.add_column("Status", justify="center")
        table.add_column("Progress", justify="right")
        table.add_column("Time", justify="right")
        
        with self.status_lock:
            for site_name in sorted(self.site_status.keys()):
                for stage_name in sorted(self.site_status[site_name].keys()):
                    stage_info = self.site_status[site_name][stage_name]
                    
                    # Status icon
                    status = stage_info['status']
                    if status == 'running':
                        status_icon = "[yellow]⟳[/yellow]"
                    elif status == 'success':
                        status_icon = "[green]✓[/green]"
                    elif status == 'error':
                        status_icon = "[red]✗[/red]"
                    else:
                        status_icon = "[yellow]⚠[/yellow]"
                    
                    # Progress
                    completed = stage_info['completed']
                    total = stage_info['total']
                    if total > 0:
                        progress_pct = (completed / total) * 100
                        progress_str = f"{completed}/{total} ({progress_pct:.1f}%)"
                    else:
                        progress_str = str(completed) if completed > 0 else "..."
                    
                    # Time elapsed
                    started_at = stage_info['started_at']
                    if 'completed_at' in stage_info:
                        elapsed = stage_info['completed_at'] - started_at
                    else:
                        elapsed = datetime.now() - started_at
                    elapsed_str = f"{int(elapsed.total_seconds())}s"
                    
                    table.add_row(site_name, stage_name, status_icon, progress_str, elapsed_str)
        
        return table
    
    def start_live_display(self):
        """Start live display mode with progress bars."""
        if not self.is_live:
            self.live = Live(self.progress, console=self.console, refresh_per_second=4)
            self.live.start()
            self.is_live = True
    
    def stop_live_display(self):
        """Stop live display mode."""
        if self.is_live and self.live:
            self.live.stop()
            self.is_live = False
    
    def print_summary(self, title: str, stats: Dict):
        """Print a summary table with statistics."""
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="yellow", no_wrap=True)
        table.add_column("Value", justify="right", style="green")
        
        for key, value in stats.items():
            # Format key (convert snake_case to Title Case)
            formatted_key = key.replace('_', ' ').title()
            table.add_row(formatted_key, str(value))
        
        self.console.print(table)
        self.console.print()


# Global logger instance
_global_rich_logger: Optional[RichLogger] = None


def get_rich_logger() -> RichLogger:
    """
    Get or create the global rich logger instance.
    
    Returns:
        RichLogger instance
    """
    global _global_rich_logger
    
    if _global_rich_logger is None:
        _global_rich_logger = RichLogger()
    
    return _global_rich_logger
