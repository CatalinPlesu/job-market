"""
Test the decoupled task queue system for scheduled scraping.
"""
import time
from src.task_queue import TaskQueue, Priority


def test_task_queue_basic():
    """Test basic task queue functionality"""
    print("Testing basic task queue functionality...")
    
    # Track execution order
    execution_order = []
    
    def task_func(site_name, stage):
        execution_order.append((site_name, stage))
        print(f"  Executed: {site_name} - {stage}")
        time.sleep(0.1)  # Simulate work
    
    # Create queue with 2 workers
    queue = TaskQueue(max_workers=2)
    
    # Register sites
    queue.register_site("site1", crawl_delay=0.1)
    queue.register_site("site2", crawl_delay=0.1)
    queue.register_site("site3", crawl_delay=0.1)
    
    # Start queue
    queue.start()
    
    # Add tasks with different priorities
    # Stage 1 has higher priority than Stage 2
    queue.add_task("site1", Priority.STAGE2, "Stage 2", task_func, "site1", "Stage 2")
    queue.add_task("site1", Priority.STAGE1, "Stage 1", task_func, "site1", "Stage 1")
    queue.add_task("site2", Priority.STAGE2, "Stage 2", task_func, "site2", "Stage 2")
    queue.add_task("site2", Priority.STAGE1, "Stage 1", task_func, "site2", "Stage 1")
    
    # Wait for completion
    queue.wait_completion()
    queue.stop()
    
    # Verify priority order
    print("\nExecution order:", execution_order)
    
    # All Stage 1 tasks should execute before Stage 2 tasks
    stage1_indices = [i for i, (_, stage) in enumerate(execution_order) if stage == "Stage 1"]
    stage2_indices = [i for i, (_, stage) in enumerate(execution_order) if stage == "Stage 2"]
    
    if stage1_indices and stage2_indices:
        max_stage1_index = max(stage1_indices)
        min_stage2_index = min(stage2_indices)
        
        if max_stage1_index < min_stage2_index:
            print("✓ Priority ordering works correctly (Stage 1 before Stage 2)")
        else:
            print("✗ Priority ordering failed")
            print(f"  Max Stage 1 index: {max_stage1_index}")
            print(f"  Min Stage 2 index: {min_stage2_index}")
    else:
        print("✓ Test completed")
    
    # Display stats
    stats = queue.get_stats()
    print("\nQueue Statistics:")
    print(f"  Completed: {stats['completed_tasks']}")
    print(f"  Failed: {stats['failed_tasks']}")
    print(f"  Pending: {stats['pending_tasks']}")


def test_crawl_delay():
    """Test that crawl delays are respected per site"""
    print("\n" + "="*80)
    print("Testing crawl delay enforcement...")
    print("="*80)
    
    request_times = {}
    
    def request_func(site_name):
        current_time = time.time()
        if site_name not in request_times:
            request_times[site_name] = []
        request_times[site_name].append(current_time)
        print(f"  {site_name} request at {current_time:.2f}")
    
    # Create queue
    queue = TaskQueue(max_workers=3)
    
    # Register site with 0.5s crawl delay
    crawl_delay = 0.5
    queue.register_site("test_site", crawl_delay=crawl_delay)
    
    # Start queue
    queue.start()
    
    # Add multiple tasks for the same site
    for i in range(3):
        queue.add_task("test_site", Priority.STAGE1, f"Request {i}", request_func, "test_site")
    
    # Wait for completion
    queue.wait_completion()
    queue.stop()
    
    # Verify delays
    if "test_site" in request_times and len(request_times["test_site"]) >= 2:
        times = request_times["test_site"]
        delays = [times[i+1] - times[i] for i in range(len(times)-1)]
        
        print(f"\nMeasured delays: {[f'{d:.2f}s' for d in delays]}")
        
        # Check if delays are approximately correct (within 0.1s tolerance)
        all_valid = all(d >= crawl_delay - 0.1 for d in delays)
        
        if all_valid:
            print(f"✓ Crawl delay ({crawl_delay}s) is respected")
        else:
            print(f"✗ Some delays are too short")
    else:
        print("✓ Test completed (not enough requests to verify)")


def test_independent_site_progression():
    """Test that sites progress independently"""
    print("\n" + "="*80)
    print("Testing independent site progression...")
    print("="*80)
    
    execution_log = []
    
    def fast_task(site_name, stage):
        execution_log.append((time.time(), site_name, stage, "start"))
        time.sleep(0.1)  # Fast task
        execution_log.append((time.time(), site_name, stage, "end"))
        print(f"  {site_name} - {stage} (fast)")
    
    def slow_task(site_name, stage):
        execution_log.append((time.time(), site_name, stage, "start"))
        time.sleep(0.5)  # Slow task
        execution_log.append((time.time(), site_name, stage, "end"))
        print(f"  {site_name} - {stage} (slow)")
    
    # Create queue
    queue = TaskQueue(max_workers=3)
    
    # Register sites
    queue.register_site("fast_site", crawl_delay=0.05)
    queue.register_site("slow_site", crawl_delay=0.05)
    
    # Start queue
    queue.start()
    
    # Add tasks
    # slow_site Stage 1 takes long, but fast_site should not wait
    queue.add_task("slow_site", Priority.STAGE1, "Stage 1", slow_task, "slow_site", "Stage 1")
    queue.add_task("fast_site", Priority.STAGE1, "Stage 1", fast_task, "fast_site", "Stage 1")
    
    # Wait for completion
    queue.wait_completion()
    queue.stop()
    
    # Check if fast_site completed before slow_site
    fast_end = None
    slow_end = None
    
    for timestamp, site, stage, event in execution_log:
        if site == "fast_site" and event == "end":
            fast_end = timestamp
        if site == "slow_site" and event == "end":
            slow_end = timestamp
    
    if fast_end and slow_end:
        if fast_end < slow_end:
            print(f"✓ Fast site completed before slow site (independent progression)")
            print(f"  Fast site ended at: {fast_end:.2f}")
            print(f"  Slow site ended at: {slow_end:.2f}")
        else:
            print(f"✗ Sites did not progress independently")
    else:
        print("✓ Test completed")


if __name__ == "__main__":
    print("="*80)
    print("TASK QUEUE TESTS")
    print("="*80 + "\n")
    
    try:
        test_task_queue_basic()
        test_crawl_delay()
        test_independent_site_progression()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
    
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
