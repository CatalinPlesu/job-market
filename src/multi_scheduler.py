"""
Multi-scheduler module for running multiple tasks on different schedules.
Coordinates multiple schedulers to run different tasks at different intervals.
"""
import threading
from typing import List, Tuple, Callable
from src.scheduler import Scheduler


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
        
        print("\n" + "="*80)
        print("MULTI-SCHEDULER STARTED")
        print("="*80)
        print(f"\nManaging {len(self.schedulers)} scheduled tasks:")
        for scheduler, _, task_name in self.schedulers:
            if scheduler.interval_minutes:
                print(f"  • {task_name}: Every {scheduler.interval_minutes} minutes")
            else:
                print(f"  • {task_name}: Daily at {scheduler.schedule_time.strftime('%H:%M')}")
        print("\nPress Ctrl+C to stop all schedulers")
        print("="*80 + "\n")
        
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
        print("\nStopping all schedulers...")
        self.running = False
        
        # Stop all schedulers
        for scheduler, _, _ in self.schedulers:
            scheduler.stop()
        
        # Wait for all threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
        
        print("All schedulers stopped.")
    
    def wait(self):
        """Wait for all scheduler threads to complete."""
        try:
            for thread in self.threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n\nStopping multi-scheduler...")
            self.stop()


def run_improved_scheduler():
    """
    Run the improved scheduler with separate schedules for different stages.
    - Stage 1 & 2: Every hour (fast with early stopping)
    - Stage 3: Once daily at midnight (slow)
    
    Note: On first startup, schedulers will wait until their scheduled time
    before running. To run immediately, use the menu options to execute
    stages manually, then start the scheduler.
    """
    from src.scheduled_scraper import run_stages_1_and_2, run_stage_3_only
    
    multi_scheduler = MultiScheduler()
    
    # Schedule Stage 1 & 2 to run every hour
    hourly_scheduler = Scheduler(
        interval_minutes=60,
        state_file_name="scheduler_state_hourly.json"
    )
    multi_scheduler.add_schedule(
        hourly_scheduler,
        run_stages_1_and_2,
        "Stages 1 & 2 (Hourly)"
    )
    
    # Schedule Stage 3 to run daily at midnight
    daily_scheduler = Scheduler(
        schedule_time_hour=0,
        schedule_time_minute=0,
        state_file_name="scheduler_state_daily.json"
    )
    multi_scheduler.add_schedule(
        daily_scheduler,
        run_stage_3_only,
        "Stage 3 (Daily)"
    )
    
    # Start all schedulers
    multi_scheduler.start(check_interval=60)
    multi_scheduler.wait()
