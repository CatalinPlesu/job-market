# Decoupled Scheduled Scraping System

## Overview

This document describes the new decoupled scheduled scraping system that allows each site to progress through scraping stages independently, without being blocked by slower sites.

## Problem Statement

The original implementation had the following issues:

1. **Sequential Stage Execution**: All 3 stages (scrape job links, scrape job details, check if job is alive) ran sequentially
2. **Blocking on Slowest Site**: Within each stage, all sites were processed in parallel, but the stage would wait for ALL sites to complete before moving to the next stage
3. **Inefficiency**: If one site took significantly longer than others, all other sites would wait idle before proceeding to the next stage

## Solution

The new system implements a **priority-based task queue** with **per-site workers** that allows:

- Each site to progress through stages independently
- Priority ordering: Stage 1 > Stage 2 > Stage 3
- Per-site crawl delay enforcement to avoid bans
- FIFO ordering within each priority level

## Architecture

### Key Components

#### 1. Task Queue (`src/task_queue.py`)

The central orchestrator that manages task execution with the following features:

- **Priority Queue**: Tasks are ordered by priority (Stage 1 = highest, Stage 3 = lowest)
- **Per-Site Workers**: Each site has its own worker that enforces crawl delays
- **Thread Pool**: Multiple worker threads process tasks concurrently
- **Statistics Tracking**: Tracks completed, failed, and pending tasks

```python
from src.task_queue import TaskQueue, Priority

# Create queue
queue = TaskQueue(max_workers=3)

# Register sites with crawl delays
queue.register_site("site1", crawl_delay=1.0)
queue.register_site("site2", crawl_delay=2.0)

# Start processing
queue.start()

# Add tasks
queue.add_task(
    site_name="site1",
    priority=Priority.STAGE1,
    stage_name="Stage 1: site1",
    task_func=my_function,
    arg1, arg2  # Task function arguments
)

# Wait for completion
queue.wait_completion()
queue.stop()
```

#### 2. Site Worker

Each site has a dedicated worker that:

- Enforces crawl delays between requests to the same site
- Ensures only one task per site runs at a time
- Tracks the last request time for delay calculation

#### 3. Decoupled Scheduler (`src/scheduled_scraper_decoupled.py`)

Reimplements the scheduled scraping logic using the task queue:

- Queues Stage 1 tasks for all sites
- Each Stage 1 task, upon completion, queues Stage 2 for that site
- Each Stage 2 task, upon completion, queues Stage 3 for that site
- Sites progress independently through the stages

### Execution Flow

```
Initial State:
  Queue: [Stage1:site1, Stage1:site2, Stage1:site3]

After site2 completes Stage 1 first:
  Queue: [Stage1:site1, Stage1:site3, Stage2:site2]

After site1 completes Stage 1:
  Queue: [Stage1:site3, Stage2:site2, Stage2:site1]

After site2 completes Stage 2:
  Queue: [Stage1:site3, Stage2:site1, Stage3:site2]

And so on... Each site progresses independently!
```

## Key Benefits

### 1. No More Blocking

Previously, if Site A took 10 minutes for Stage 1 and Site B took 2 minutes, Site B would wait 8 minutes before starting Stage 2.

Now, Site B starts Stage 2 immediately after completing Stage 1.

### 2. Priority Ordering

Stage 1 tasks (detecting new links) always have priority over Stage 2 (getting details) and Stage 3 (checking if jobs are alive). This ensures fresh jobs are discovered quickly.

### 3. Crawl Delay Enforcement

Each site maintains its own crawl delay timer. Multiple requests to different sites can happen simultaneously, but requests to the same site respect the configured delay.

### 4. Minimal Code Changes

The change is transparent to the rest of the system:
- `run_all_stages_scheduled()` still works the same way
- Same reporting and statistics
- Same error handling and logging
- Existing tests and infrastructure unchanged

## Usage

### From the Menu

No changes to the user interface. Use the same menu option:

```
1. Run All Stages on Schedule (with Logging & Reports)
```

### Programmatic Usage

The existing API remains unchanged:

```python
from src.scheduled_scraper import run_all_stages_scheduled

# This now uses the decoupled implementation automatically
run_all_stages_scheduled()
```

### Direct Use of Decoupled Version

You can also use the decoupled version directly:

```python
from src.scheduled_scraper_decoupled import run_all_stages_decoupled

run_all_stages_decoupled()
```

## Configuration

### Crawl Delays

Crawl delays are still read from robots.txt for each site. The system respects these delays automatically.

### Worker Count

By default, the system creates one worker per site. You can modify this in `scheduled_scraper_decoupled.py`:

```python
# Create task queue with custom worker count
task_queue = TaskQueue(max_workers=10)  # Default: len(ruless)
```

## Testing

A comprehensive test suite is provided in `test_task_queue.py`:

```bash
python test_task_queue.py
```

Tests verify:
1. Priority ordering (Stage 1 before Stage 2 before Stage 3)
2. Crawl delay enforcement (per-site delays respected)
3. Independent progression (fast sites don't wait for slow sites)

## Performance Comparison

### Original System (Sequential Stages)

```
Timeline:
[0s-600s] Stage 1: All sites (site1=100s, site2=500s, site3=200s)
  → Wait for site2 to complete (500s total)

[600s-900s] Stage 2: All sites (site1=50s, site2=200s, site3=100s)
  → Wait for site2 to complete (200s additional)

[900s-1100s] Stage 3: All sites (site1=50s, site2=150s, site3=100s)
  → Wait for site2 to complete (150s additional)

Total time: 850s (site1+site2+site3 all finish at same time)
```

### New System (Decoupled)

```
Timeline:
[0s-100s]   site1: Stage 1 completes
[100s-150s] site1: Stage 2 completes
[150s-200s] site1: Stage 3 completes → site1 DONE in 200s

[0s-200s]   site3: Stage 1 completes
[200s-300s] site3: Stage 2 completes
[300s-400s] site3: Stage 3 completes → site3 DONE in 400s

[0s-500s]   site2: Stage 1 completes
[500s-700s] site2: Stage 2 completes
[700s-850s] site2: Stage 3 completes → site2 DONE in 850s

Total time: 850s (same) BUT:
- site1 finished at 200s (650s earlier!)
- site3 finished at 400s (450s earlier!)
- Results available much sooner
```

## Implementation Details

### Thread Safety

- All shared state protected by locks
- Per-site workers use locks for atomic operations
- Statistics collection uses dedicated lock
- Queue operations are thread-safe by design

### Error Handling

- Errors in one site don't affect other sites
- Failed tasks are tracked in statistics
- Error logging continues to work as before
- Partial results are still reported

### Reporting

- Same report format as before
- Statistics collected per site and aggregated
- Reports saved in same location and format
- No changes to report viewing

## Future Enhancements

Possible improvements for future versions:

1. **Dynamic Worker Allocation**: Adjust worker count based on workload
2. **Task Retry Logic**: Automatically retry failed tasks
3. **Rate Limiting**: Global rate limits across all sites
4. **Progress Dashboard**: Real-time visualization of site progress
5. **Adaptive Priorities**: Adjust priorities based on site performance

## Migration Notes

### Backward Compatibility

The change is fully backward compatible:
- Existing code continues to work
- Same API and interfaces
- Same configuration files
- Same database schema

### Rollback

If needed, you can temporarily revert to the old behavior by modifying `src/scheduled_scraper.py`:

```python
# Comment out the new implementation
# from src.scheduled_scraper_decoupled import run_all_stages_decoupled
# run_all_stages_decoupled()

# Uncomment the old implementation (lines 100-540 in original file)
```

## Troubleshooting

### Issue: Tasks not respecting crawl delays

**Solution**: Verify that each site is registered with the correct crawl delay:
```python
queue.register_site(site_name, crawl_delay=delay)
```

### Issue: Some sites not progressing

**Solution**: Check the logs for errors. Failed tasks don't automatically queue subsequent stages.

### Issue: Higher memory usage

**Solution**: The task queue holds all pending tasks in memory. This is expected and scales with the number of sites.

## Conclusion

The decoupled scheduled scraping system provides significant efficiency improvements by allowing sites to progress independently through scraping stages. The implementation maintains backward compatibility while offering better resource utilization and faster results availability.
