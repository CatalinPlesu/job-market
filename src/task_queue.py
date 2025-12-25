"""
Task queue system for decoupled per-site scraping operations.
Allows each site to progress through stages independently with priority-based execution.
"""
import threading
import queue
import time
from enum import IntEnum
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import itertools


class Priority(IntEnum):
    """Task priority levels - lower number = higher priority"""
    STAGE1 = 1  # Scrape job links (highest priority)
    STAGE2 = 2  # Scrape job details
    STAGE3 = 3  # Check if job is alive (lowest priority)


@dataclass
class Task:
    """Represents a single task to be executed"""
    site_name: str
    priority: Priority
    stage_name: str
    task_func: Callable
    task_args: tuple = ()
    task_kwargs: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.task_kwargs is None:
            self.task_kwargs = {}
    
    def __lt__(self, other):
        """Compare tasks by priority for queue ordering"""
        # Lower priority number = higher priority in queue
        if self.priority != other.priority:
            return self.priority < other.priority
        # Same priority: maintain insertion order (FIFO per priority level)
        return False


class SiteWorker:
    """
    Worker that processes tasks for a single site.
    Maintains per-site crawl delay and ensures only one task per site runs at a time.
    """
    
    def __init__(self, site_name: str, crawl_delay: float = 1.0):
        self.site_name = site_name
        self.crawl_delay = crawl_delay
        self.last_request_time = 0
        self.lock = threading.Lock()
        self.is_active = False
        self.current_task: Optional[Task] = None
        self.available_event = threading.Event()
        self.available_event.set()  # Initially available
    
    def wait_for_crawl_delay(self):
        """Wait for crawl delay to elapse since last request"""
        with self.lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < self.crawl_delay:
                wait_time = self.crawl_delay - time_since_last_request
                time.sleep(wait_time)
            
            self.last_request_time = time.time()
    
    def execute_task(self, task: Task):
        """Execute a task with crawl delay enforcement"""
        # Mark as active and clear available event
        with self.lock:
            self.is_active = True
            self.current_task = task
            self.available_event.clear()
        
        try:
            # Wait for crawl delay (outside of lock)
            self.wait_for_crawl_delay()
            
            # Execute the task
            task.task_func(*task.task_args, **task.task_kwargs)
        finally:
            with self.lock:
                self.is_active = False
                self.current_task = None
                self.available_event.set()  # Signal that worker is available


class TaskQueue:
    """
    Priority-based task queue that manages per-site workers.
    Each site has its own FIFO queue within priority levels.
    """
    
    def __init__(self, max_workers: int = 10):
        # Priority queue for all tasks
        self.task_queue = queue.PriorityQueue()
        
        # Monotonic counter for insertion ordering
        self.insertion_counter = itertools.count()
        
        # Per-site workers
        self.site_workers: Dict[str, SiteWorker] = {}
        self.site_workers_lock = threading.Lock()
        
        # Worker threads
        self.max_workers = max_workers
        self.worker_threads = []
        self.running = False
        self.stop_event = threading.Event()
        
        # Statistics
        self.stats_lock = threading.Lock()
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.tasks_by_stage = {
            Priority.STAGE1: 0,
            Priority.STAGE2: 0,
            Priority.STAGE3: 0,
        }
    
    def register_site(self, site_name: str, crawl_delay: float = 1.0):
        """Register a site with its crawl delay"""
        with self.site_workers_lock:
            if site_name not in self.site_workers:
                self.site_workers[site_name] = SiteWorker(site_name, crawl_delay)
    
    def add_task(self, site_name: str, priority: Priority, stage_name: str,
                 task_func: Callable, *args, **kwargs):
        """Add a task to the queue"""
        task = Task(
            site_name=site_name,
            priority=priority,
            stage_name=stage_name,
            task_func=task_func,
            task_args=args,
            task_kwargs=kwargs
        )
        
        # Use tuple for priority queue: (priority, insertion_order, task)
        # insertion_order ensures FIFO within same priority level
        insertion_order = next(self.insertion_counter)
        self.task_queue.put((priority, insertion_order, task))
        
        with self.stats_lock:
            self.tasks_by_stage[priority] = self.tasks_by_stage.get(priority, 0) + 1
    
    def get_site_worker(self, site_name: str) -> Optional[SiteWorker]:
        """Get worker for a site"""
        with self.site_workers_lock:
            return self.site_workers.get(site_name)
    
    def worker_loop(self):
        """Main worker loop that processes tasks from the queue"""
        while self.running and not self.stop_event.is_set():
            try:
                # Get next task with timeout
                priority, insertion_order, task = self.task_queue.get(timeout=1)
                
                # Get worker for this site
                worker = self.get_site_worker(task.site_name)
                if not worker:
                    print(f"Warning: No worker registered for site {task.site_name}")
                    self.task_queue.task_done()
                    continue
                
                # Wait for worker to become available (using Event for efficiency)
                worker.available_event.wait()
                
                # Execute task (includes crawl delay enforcement)
                print(f"[TaskQueue] Executing {task.stage_name} for {task.site_name}")
                try:
                    worker.execute_task(task)
                    with self.stats_lock:
                        self.completed_tasks += 1
                except Exception as e:
                    print(f"[TaskQueue] Error executing {task.stage_name} for {task.site_name}: {e}")
                    with self.stats_lock:
                        self.failed_tasks += 1
                finally:
                    self.task_queue.task_done()
                    
            except queue.Empty:
                # No tasks available, continue
                continue
            except Exception as e:
                print(f"[TaskQueue] Worker error: {e}")
    
    def start(self):
        """Start worker threads"""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Start worker threads
        for i in range(self.max_workers):
            thread = threading.Thread(target=self.worker_loop, daemon=True, name=f"TaskWorker-{i}")
            thread.start()
            self.worker_threads.append(thread)
        
        print(f"[TaskQueue] Started with {self.max_workers} workers")
    
    def wait_completion(self, timeout: Optional[float] = None):
        """Wait for all tasks to complete"""
        self.task_queue.join()
    
    def stop(self, wait: bool = True):
        """Stop all worker threads"""
        self.running = False
        self.stop_event.set()
        
        if wait:
            for thread in self.worker_threads:
                thread.join(timeout=5)
        
        self.worker_threads.clear()
        print(f"[TaskQueue] Stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.stats_lock:
            return {
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'pending_tasks': self.task_queue.qsize(),
                'tasks_by_stage': dict(self.tasks_by_stage),
            }
