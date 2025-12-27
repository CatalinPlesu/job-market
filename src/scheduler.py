"""
Scheduler module for running scraping tasks on schedule.
Self-manages scheduling without requiring cron jobs.
"""
import time
import json
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Callable, Optional
import threading


class Scheduler:
    """
    Self-managing scheduler that runs tasks at specified times.
    Handles schedule tracking and execution without external cron.
    Supports both daily schedules and interval-based schedules (e.g., hourly).
    """
    
    def __init__(self, schedule_time_hour: int = 0, schedule_time_minute: int = 0, 
                 interval_minutes: Optional[int] = None, state_file_name: str = "scheduler_state.json"):
        """
        Initialize scheduler with target time or interval.
        
        Args:
            schedule_time_hour: Hour to run (0-23), default 0 (midnight). Ignored if interval_minutes is set.
            schedule_time_minute: Minute to run (0-59), default 0. Ignored if interval_minutes is set.
            interval_minutes: If set, run every N minutes instead of at a specific time
            state_file_name: Name of the state file to track last run
        """
        self.schedule_time = dt_time(schedule_time_hour, schedule_time_minute)
        self.interval_minutes = interval_minutes
        self.state_file = Path(state_file_name)
        self.running = False
        self.stop_event = threading.Event()
        
    def load_last_run(self) -> Optional[datetime]:
        """Load the last run timestamp from state file."""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                if 'last_run' in data:
                    return datetime.fromisoformat(data['last_run'])
        except Exception:
            pass
        
        return None
    
    def save_last_run(self, run_time: datetime):
        """Save the last run timestamp to state file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_run': run_time.isoformat(),
                    'next_scheduled': self.get_next_run_time().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save scheduler state: {e}")
    
    def get_next_run_time(self) -> datetime:
        """
        Calculate the next scheduled run time.
        
        Returns:
            datetime: Next scheduled run time
        """
        now = datetime.now()
        
        if self.interval_minutes:
            # Interval-based scheduling: next run is interval_minutes from last run
            last_run = self.load_last_run()
            if last_run:
                next_run = last_run + timedelta(minutes=self.interval_minutes)
                # If next run is in the past, calculate the next future run
                if next_run <= now:
                    # Calculate how many intervals have passed since last run
                    time_since_last = (now - last_run).total_seconds() / 60
                    intervals_passed = int(time_since_last / self.interval_minutes) + 1
                    next_run = last_run + timedelta(minutes=self.interval_minutes * intervals_passed)
                return next_run
            else:
                # First run: schedule for interval_minutes from now
                return now + timedelta(minutes=self.interval_minutes)
        else:
            # Time-based scheduling: next run is at the scheduled time
            scheduled = datetime.combine(now.date(), self.schedule_time)
            
            # If scheduled time has passed today, schedule for tomorrow
            if scheduled <= now:
                scheduled = scheduled + timedelta(days=1)
            
            return scheduled
    
    def should_run_now(self) -> bool:
        """
        Check if the task should run now based on schedule.
        
        Returns:
            bool: True if task should run now
        """
        last_run = self.load_last_run()
        now = datetime.now()
        
        if self.interval_minutes:
            # Interval-based scheduling
            if last_run is None:
                # Never run before, don't run immediately
                return False
            
            # Run if interval has passed since last run
            time_since_last = (now - last_run).total_seconds() / 60
            return time_since_last >= self.interval_minutes
        else:
            # Time-based scheduling
            # Calculate today's scheduled time
            today_scheduled = datetime.combine(now.date(), self.schedule_time)
            
            # If never run before, don't run immediately
            # Wait for the next scheduled time instead
            if last_run is None:
                return False
            
            # Run if:
            # 1. Current time is past scheduled time today
            # 2. Last run was before today's scheduled time
            if now >= today_scheduled and last_run < today_scheduled:
                return True
            
            return False
    
    def run_once(self, task: Callable, task_name: str = "Scheduled Task") -> bool:
        """
        Run the task once immediately and update last run time.
        
        Args:
            task: Callable to execute
            task_name: Name of the task for logging
            
        Returns:
            bool: True if task executed successfully
        """
        print(f"\n{'='*80}")
        print(f"Executing {task_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        try:
            task()
            run_time = datetime.now()
            self.save_last_run(run_time)
            
            next_run = self.get_next_run_time()
            print(f"\n{'='*80}")
            print(f"{task_name} completed successfully!")
            print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}\n")
            return True
            
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"ERROR: {task_name} failed with exception: {e}")
            print(f"{'='*80}\n")
            import traceback
            traceback.print_exc()
            return False
    
    def run_with_monitoring(self, task: Callable, task_name: str = "Scheduled Task", 
                          check_interval: int = 60):
        """
        Run task in a monitoring loop that checks the schedule.
        This is for manual execution where the user wants to keep the process running
        and have it automatically execute at the scheduled time.
        
        Args:
            task: Callable to execute
            task_name: Name of the task for logging
            check_interval: Seconds between schedule checks (default: 60)
        """
        self.running = True
        
        # Ensure check_interval is reasonable (max 30 minutes as suggested)
        max_interval = 30 * 60  # 30 minutes in seconds
        check_interval = min(check_interval, max_interval)
        
        # Show initial status
        last_run = self.load_last_run()
        next_run = self.get_next_run_time()
        
        print(f"\n{'='*80}")
        print(f"Scheduler started for: {task_name}")
        if self.interval_minutes:
            print(f"Schedule: Every {self.interval_minutes} minutes")
        else:
            print(f"Schedule time: {self.schedule_time.strftime('%H:%M')}")
        if last_run:
            print(f"Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"Last run: Never")
        print(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Check interval: {check_interval} seconds")
        print(f"Press Ctrl+C to stop monitoring")
        print(f"{'='*80}\n")
        
        try:
            while self.running and not self.stop_event.is_set():
                # Initialize adaptive_interval with default value
                # This ensures it's always defined even if exceptions occur
                adaptive_interval = check_interval
                
                if self.should_run_now():
                    self.run_once(task, task_name)
                    # After running, recalculate next run
                    next_run = self.get_next_run_time()
                else:
                    # Show countdown to next run
                    now = datetime.now()
                    time_until_next = next_run - now
                    total_seconds = time_until_next.total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    
                    print(f"Waiting for next run... "
                          f"(Next: {next_run.strftime('%Y-%m-%d %H:%M')} - "
                          f"{hours}h {minutes}m remaining)", end='\r')
                    
                    # Use adaptive check interval: check more frequently as we get closer
                    # If less than 5 minutes away, check every minute
                    if total_seconds < 300:  # Less than 5 minutes
                        adaptive_interval = 60  # Check every minute
                    elif total_seconds < 3600:  # Less than 1 hour
                        adaptive_interval = min(check_interval, 300)  # Check every 5 minutes max
                
                # Check every interval
                self.stop_event.wait(adaptive_interval)
        
        except KeyboardInterrupt:
            print("\n\nScheduler stopped by user.")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the scheduler monitoring loop."""
        self.running = False
        self.stop_event.set()
