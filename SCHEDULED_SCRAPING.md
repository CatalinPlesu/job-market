# Scheduled Scraping Feature

## Overview

This feature provides automated, scheduled scraping of all job sites with comprehensive reporting, error logging, and database backups. It's designed to run on a self-managed schedule (default: midnight) without requiring external cron jobs.

## Features

### 1. Self-Managed Scheduler
- **No cron required**: The scheduler manages itself internally
- **Configurable schedule**: Default runs at 00:00 (midnight)
- **State persistence**: Tracks last run time to avoid duplicate executions
- **Manual override**: Can run immediately or wait for scheduled time

### 2. Three-Stage Scraping Pipeline

#### Stage 1: Job Listings Scraping
- Scrapes job listing pages from all configured sites
- Finds new job postings and URLs
- Uses binary search to detect maximum pages
- Respects robots.txt crawl delays

#### Stage 2: Job Details Scraping
- Gets detailed descriptions for jobs without descriptions
- Only processes jobs where `job_description` is NULL
- Handles HTTP status codes (200, 404, etc.)
- Updates job_description field

#### Stage 3: Job Status Recheck
- Re-checks jobs that were previously "alive" (HTTP 200)
- Verifies if job postings are still active
- Updates job descriptions if missing
- Tracks alive vs. dead status

### 3. Comprehensive Reporting

Reports are stored in the `reports/` directory with both JSON and text formats.

#### Daily Report Contents

**Stage 1 Statistics (per site + aggregated):**
- Total links found
- Total pages scraped
- Errors encountered

**Stage 2 Statistics (per site + aggregated):**
- Total jobs processed
- Successful scrapes (got description)
- Empty results (page loaded but no content)
- Failed scrapes (HTTP errors)
- HTTP status breakdown (200, 404, other)

**Stage 3 Statistics (per site + aggregated):**
- Total jobs checked
- Alive jobs (HTTP 200)
- Dead jobs (any error)

#### Report Files
- `report_YYYY-MM-DD.json` - Machine-readable JSON format
- `report_YYYY-MM-DD.txt` - Human-readable text format

### 4. Error-Only Logging

Logs are stored in the `logs/` directory organized by week.

**Features:**
- **Error-only**: Only logs errors, not normal operations
- **Weekly rotation**: One log file per week (e.g., `scraper_2025-W51.log`)
- **Automatic cleanup**: Keeps logs for 4 weeks by default
- **Detailed context**: Includes timestamps, error messages, and stack traces

### 5. Database Backups

Backups are stored in the `backups/` directory.

**Features:**
- **Pre-run backup**: Creates backup before each scheduled run
- **Timestamped files**: Format: `data_backup_YYYY-MM-DD_HH-MM-SS.db`
- **Automatic cleanup**: Keeps only last 3 days of backups
- **Safe restoration**: Creates pre-restore backup before restoring

## Usage

### From the Menu

1. Start the application:
   ```bash
   python main.py
   ```

2. Select the new menu option:
   ```
   1. Run All Stages on Schedule (with Logging & Reports)
   ```

3. Choose execution mode:
   - **Option 1: Run once NOW** - Executes all stages immediately
   - **Option 2: Start scheduler** - Waits for scheduled time (00:00)

### Running Scheduled Execution

**Option 1 - Immediate Execution:**
```
Options:
  1. Run once NOW
  2. Start scheduler (will wait for scheduled time)
  0. Cancel

Enter choice: 1
```

This will:
1. Create database backup
2. Run Stage 1 (scrape job listings)
3. Run Stage 2 (get job details)
4. Run Stage 3 (recheck alive jobs)
5. Generate daily report
6. Display summary

**Option 2 - Scheduled Monitoring:**
```
Options:
  1. Run once NOW
  2. Start scheduler (will wait for scheduled time)
  0. Cancel

Enter choice: 2
```

This will:
1. Show current schedule status
2. Display time until next run
3. Wait and monitor until scheduled time
4. Execute automatically at 00:00
5. Continue monitoring for next day

Press `Ctrl+C` to stop the scheduler.

### Programmatic Usage

You can also use the scheduler programmatically:

```python
from src.scheduler import Scheduler
from src.scheduled_scraper import run_all_stages_scheduled

# Create scheduler (runs at midnight)
scheduler = Scheduler(schedule_time_hour=0, schedule_time_minute=0)

# Run immediately
scheduler.run_once(
    task=run_all_stages_scheduled,
    task_name="Scheduled Scraping"
)

# Or start monitoring
scheduler.run_with_monitoring(
    task=run_all_stages_scheduled,
    task_name="Scheduled Scraping",
    check_interval=60  # Check every minute
)
```

## Directory Structure

After running scheduled scraping, the following directories will be created:

```
job-market/
├── backups/           # Database backups
│   └── data_backup_YYYY-MM-DD_HH-MM-SS.db
├── logs/              # Weekly error logs
│   └── scraper_YYYY-WXX.log
├── reports/           # Daily reports
│   ├── report_YYYY-MM-DD.json
│   └── report_YYYY-MM-DD.txt
└── scheduler_state.json  # Scheduler state (last run time)
```

## Configuration

### Schedule Time

Default schedule is 00:00 (midnight). To change:

Edit `main.py` in the `ScheduledScrapingItem.execute()` method:

```python
scheduler = Scheduler(
    schedule_time_hour=0,   # 0-23
    schedule_time_minute=0  # 0-59
)
```

### Backup Retention

Default keeps last 3 days of backups. To change:

Edit `src/scheduled_scraper.py` in `run_all_stages_scheduled()`:

```python
backup = DatabaseBackup(Config.db_path, keep_days=3)  # Change to desired days
```

### Log Retention

Default keeps 4 weeks of logs. To change:

Call cleanup manually or modify `src/error_logger.py`:

```python
WeeklyErrorLogger.cleanup_old_logs(keep_weeks=4)  # Change to desired weeks
```

## Viewing Reports

### Latest Report

The latest report will be displayed automatically after each run.

### View Previous Reports

Reports are stored in `reports/` directory:

```bash
# View text version
cat reports/report_2025-12-21.txt

# View JSON version
cat reports/report_2025-12-21.json
```

### Example Report

```
================================================================================
DAILY SCRAPING REPORT - 2025-12-21
================================================================================

STAGE 1: Job Listings Scraping
--------------------------------------------------------------------------------
  jobber.md            | Links:   150 | Pages:    5 | Errors:   0
  rabota.md            | Links:   200 | Pages:    7 | Errors:   0
  delucru.md           | Links:   180 | Pages:    6 | Errors:   0

  TOTAL                | Links:   530 | Pages:   18 | Errors:   0

STAGE 2: Job Details Scraping
--------------------------------------------------------------------------------
  jobber.md            | Total:  150 | OK:  145 | Empty:    3 | Failed:    2
                       | HTTP 200:  145 | 404:    2 | Other:    0
  rabota.md            | Total:  200 | OK:  195 | Empty:    4 | Failed:    1
                       | HTTP 200:  195 | 404:    1 | Other:    0
  delucru.md           | Total:  180 | OK:  175 | Empty:    3 | Failed:    2
                       | HTTP 200:  175 | 404:    2 | Other:    0

  TOTAL                | Total:  530 | OK:  515 | Empty:   10 | Failed:    5
                       | HTTP 200:  515 | 404:    5 | Other:    0

STAGE 3: Job Status Recheck
--------------------------------------------------------------------------------
  jobber.md            | Checked:   500 | Alive:   485 | Dead:    15
  rabota.md            | Checked:   650 | Alive:   640 | Dead:    10
  delucru.md           | Checked:   420 | Alive:   410 | Dead:    10

  TOTAL                | Checked:  1570 | Alive:  1535 | Dead:    35

================================================================================
Report generated at: 2025-12-21T00:15:32.123456
================================================================================
```

## Viewing Logs

Logs only contain errors. If everything runs successfully, log files will be empty or contain minimal entries.

```bash
# View current week's log
cat logs/scraper_2025-W51.log
```

### Example Log

```
2025-12-21 00:05:23 - ERROR - Stage 2 - jobber.md job 1234: HTTP 404 Not Found
2025-12-21 00:07:45 - ERROR - Stage 3 - rabota.md job 5678: Connection timeout
```

## Troubleshooting

### Scheduler Not Running at Expected Time

Check `scheduler_state.json` for last run time:

```bash
cat scheduler_state.json
```

If needed, delete it to reset:

```bash
rm scheduler_state.json
```

### Database Backup Failed

Ensure sufficient disk space and write permissions:

```bash
ls -la backups/
df -h .
```

### Reports Not Generated

Check for errors in logs:

```bash
cat logs/scraper_*.log
```

Ensure `reports/` directory is writable:

```bash
ls -ld reports/
```

## Best Practices

1. **Run during off-peak hours**: Default 00:00 is recommended to avoid server load
2. **Monitor first few runs**: Check reports to ensure all sites are working
3. **Review error logs weekly**: Address persistent errors
4. **Keep backups archived**: Consider copying old backups elsewhere before cleanup
5. **Test schedule changes**: Use "Run once NOW" to test before scheduling

## Technical Details

### Scheduler State

The scheduler maintains state in `scheduler_state.json`:

```json
{
  "last_run": "2025-12-21T00:00:15.123456",
  "next_scheduled": "2025-12-22T00:00:00"
}
```

### Statistics Collection

All statistics are collected during execution:
- Stage 1: Counted during page scraping
- Stage 2: Tracked per HTTP status code
- Stage 3: Categorized as alive (200) or dead (other)

### Error Handling

- Errors in one site don't affect others (parallel execution)
- Failed stages are logged but don't stop execution
- Reports show partial results even if some stages fail

## Testing

Run verification tests:

```bash
python test_scheduled_scraper.py
```

This tests all components without running actual scraping.
