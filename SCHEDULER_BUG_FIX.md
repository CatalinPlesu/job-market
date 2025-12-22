# Scheduler Bug Fix Summary

## Issue Reported

User reported that the scheduler didn't run at the scheduled time (00:00). They launched it expecting it to run the next day at midnight, but it never executed. The manual trigger worked fine, but the automatic scheduling failed.

User also expressed concern about potential sleep magnitude issues (waiting 18 days instead of 18 hours) and suggested not waiting more than 30 minutes in the loop for safety.

## Root Cause Analysis

The bug was in `src/scheduler.py`, specifically in the `should_run_now()` method (lines 75-98):

```python
# BEFORE (BUGGY CODE)
def should_run_now(self) -> bool:
    last_run = self.load_last_run()
    now = datetime.now()
    
    # If never run before, don't run immediately (wait for scheduled time)
    if last_run is None:
        return False  # <-- BUG: This prevents first-time execution!
    
    # ... rest of the logic
```

**The Problem:**
- When the scheduler started for the first time (no `scheduler_state.json` file), `last_run` would be `None`
- The code returned `False` immediately, meaning "don't run now"
- This caused the scheduler to wait indefinitely without ever executing
- The scheduler only checked if it should run, but the check always returned `False` for first-time runs

## Fix Applied

### 1. Fixed First-Run Detection

```python
# AFTER (FIXED CODE)
def should_run_now(self) -> bool:
    last_run = self.load_last_run()
    now = datetime.now()
    
    # Calculate today's scheduled time
    today_scheduled = datetime.combine(now.date(), self.schedule_time)
    
    # If never run before, check if we're past today's scheduled time
    if last_run is None:
        return now >= today_scheduled  # <-- FIX: Check against scheduled time!
    
    # Run if past scheduled time and haven't run today
    if now >= today_scheduled and last_run < today_scheduled:
        return True
    
    return False
```

**What Changed:**
- First-time runs now check if current time is past the scheduled time
- If yes, execute immediately
- If no, wait until scheduled time is reached

### 2. Added Maximum Check Interval Cap

Per user's request to not wait more than 30 minutes:

```python
def run_with_monitoring(self, task: Callable, task_name: str = "Scheduled Task", 
                      check_interval: int = 60):
    # Ensure check_interval is reasonable (max 30 minutes as suggested)
    max_interval = 30 * 60  # 30 minutes in seconds
    check_interval = min(check_interval, max_interval)
```

**What This Does:**
- Even if a longer interval is requested, it's capped at 30 minutes
- This ensures the scheduler checks at least every 30 minutes
- Prevents the "waiting 18 days instead of 18 hours" scenario

### 3. Implemented Adaptive Intervals

To be more responsive as the scheduled time approaches:

```python
# Use adaptive check interval: check more frequently as we get closer
adaptive_interval = check_interval
if total_seconds < 300:  # Less than 5 minutes
    adaptive_interval = 60  # Check every minute
elif total_seconds < 3600:  # Less than 1 hour
    adaptive_interval = min(check_interval, 300)  # Check every 5 minutes max
```

**What This Does:**
- When >1 hour away: use configured interval (max 30 minutes)
- When <1 hour away: check every 5 minutes
- When <5 minutes away: check every minute
- Ensures timely execution without excessive checking

## Testing

Created comprehensive test suite (`test_scheduler_fix.py`) that verifies:

1. ✅ **First run detection** - Executes at scheduled time without previous state
2. ✅ **Future time handling** - Doesn't execute if scheduled time is in future
3. ✅ **Adaptive interval** - Check interval capped at 30 minutes
4. ✅ **Next day execution** - Runs again the next day after previous run

All tests pass, confirming the bug is fixed.

## Impact

**Before Fix:**
- Scheduler would never run automatically on first launch
- User had to manually trigger execution every time
- Scheduled monitoring mode was unusable

**After Fix:**
- Scheduler runs at scheduled time (00:00) as expected
- Works on first launch without any previous state
- Safe interval checking (max 30 minutes)
- Adaptive intervals for better responsiveness

## Files Changed

- `src/scheduler.py` - Fixed logic and added interval safeguards
- `test_scheduler_fix.py` - New comprehensive test suite

## Verification

All existing tests continue to pass:
- `test_scheduled_scraper.py` - All 4 tests pass ✓
- `test_scheduler_fix.py` - All 4 new tests pass ✓

The scheduler now works correctly in both modes:
- **Option 1 (Run now):** Still works as before ✓
- **Option 2 (Scheduled):** Now works on first launch ✓

## User Feedback Addressed

✅ Fixed scheduler not running at scheduled time  
✅ Implemented 30-minute maximum check interval as suggested  
✅ Added adaptive intervals for better responsiveness  
✅ Manual trigger continues to work  
✅ No magnitude errors in sleep calculations
