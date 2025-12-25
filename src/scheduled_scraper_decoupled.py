"""
Decoupled scheduled scraping orchestrator using task queue system.
Each site progresses through stages independently without waiting for others.
"""
import json
from config.settings import Config
from src.scrape_database import ScrapeSessionLocal, Job, JobCheck
from src.scrape_jobs_list import (
    get_crawl_delay_with_robotparser, find_max_pages_threaded, 
    scrape_jobs, store_jobs, ThreadProgressTracker, progress_tracker as global_progress_tracker,
    monitor_progress, check_page_exists
)
from src.scrape_job_details import fetch_job_description, update_job_check
from src.reporting import DailyReport, Stage1Stats, Stage2Stats, Stage3Stats
from src.error_logger import get_logger
from src.database_backup import backup_all_databases
from src.task_queue import TaskQueue, Priority
from src.rich_logger import get_rich_logger
from datetime import date, datetime, timezone
import threading
import time
from sqlalchemy import and_, func


def run_all_stages_decoupled():
    """
    Run all scraping stages (1, 2, 3) with decoupled per-site execution.
    Each site progresses through stages independently using a priority task queue.
    This is the main entry point for decoupled scheduled execution.
    """
    # Initialize components
    logger = get_logger()
    report = DailyReport()
    rich_logger = get_rich_logger()
    
    rich_logger.print_header(
        "DECOUPLED SCHEDULED SCRAPING",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        # Create database backups before starting
        rich_logger.print_section("Database Backup")
        rich_logger.print_info("Creating database backups...")
        backup_all_databases(keep_days=3)
        rich_logger.print_success("Database backups created")
        
        # Load scraper rules
        with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
            ruless = json.load(file)
        
        # Initialize task queue
        task_queue = TaskQueue(max_workers=len(ruless))
        
        # Register all sites and get crawl delays
        rich_logger.print_section("Registering Sites")
        site_crawl_delays = {}
        for rules in ruless:
            site_name = rules[Config.scraper_name]
            delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
            task_queue.register_site(site_name, delay)
            site_crawl_delays[site_name] = delay
            rich_logger.print_info(f"{delay}s crawl delay", site_name)
        
        # Statistics collection
        stats_collection = {
            'stage1': {},
            'stage2': {},
            'stage3': {},
        }
        stats_lock = threading.Lock()
        
        # Start task queue
        task_queue.start()
        
        # Start live display
        rich_logger.print_section("Starting Scraping Operations")
        rich_logger.start_live_display()
        
        # Define task functions that will be used by all sites
        def make_stage1_task(rules, site_name):
            """Create Stage 1 task for a site"""
            def task():
                try:
                    stats = execute_stage1_for_site(rules, logger, rich_logger)
                    with stats_lock:
                        stats_collection['stage1'][site_name] = stats
                    
                    # Queue Stage 2 for this site after Stage 1 completes
                    stage2_task = make_stage2_task(rules, site_name)
                    task_queue.add_task(
                        site_name=site_name,
                        priority=Priority.STAGE2,
                        stage_name=f"Stage 2: {site_name}",
                        task_func=stage2_task
                    )
                except Exception as e:
                    logger.exception(f"Stage 1 failed for {site_name}: {e}")
                    rich_logger.print_error(f"Stage 1 failed: {e}", site_name)
            return task
        
        def make_stage2_task(rules, site_name):
            """Create Stage 2 task for a site"""
            def task():
                try:
                    stats = execute_stage2_for_site(rules, logger, rich_logger)
                    with stats_lock:
                        stats_collection['stage2'][site_name] = stats
                    
                    # Queue Stage 3 for this site after Stage 2 completes
                    stage3_task = make_stage3_task(rules, site_name)
                    task_queue.add_task(
                        site_name=site_name,
                        priority=Priority.STAGE3,
                        stage_name=f"Stage 3: {site_name}",
                        task_func=stage3_task
                    )
                except Exception as e:
                    logger.exception(f"Stage 2 failed for {site_name}: {e}")
                    rich_logger.print_error(f"Stage 2 failed: {e}", site_name)
            return task
        
        def make_stage3_task(rules, site_name):
            """Create Stage 3 task for a site"""
            def task():
                try:
                    stats = execute_stage3_for_site(rules, logger, rich_logger)
                    with stats_lock:
                        stats_collection['stage3'][site_name] = stats
                except Exception as e:
                    logger.exception(f"Stage 3 failed for {site_name}: {e}")
                    rich_logger.print_error(f"Stage 3 failed: {e}", site_name)
            return task
        
        # Queue all Stage 1 tasks (highest priority)
        for rules in ruless:
            site_name = rules[Config.scraper_name]
            
            # Add Stage 1 task to queue
            stage1_task = make_stage1_task(rules, site_name)
            task_queue.add_task(
                site_name=site_name,
                priority=Priority.STAGE1,
                stage_name=f"Stage 1: {site_name}",
                task_func=stage1_task
            )
        
        # Wait for all tasks to complete
        task_queue.wait_completion()
        
        # Stop live display and task queue
        rich_logger.stop_live_display()
        task_queue.stop()
        
        rich_logger.print_section("All Stages Completed")
        
        # Generate report
        rich_logger.print_info("Generating report...")
        
        # Add statistics to report
        with stats_lock:
            for site_name, stats in stats_collection['stage1'].items():
                report.add_stage1_stats(stats)
            
            for site_name, stats in stats_collection['stage2'].items():
                report.add_stage2_stats(stats)
            
            for site_name, stats in stats_collection['stage3'].items():
                report.add_stage3_stats(stats)
        
        # Save and display report
        report.save()
        rich_logger.print_success(f"Report saved to: {report.report_file}")
        
        # Display report with rich formatting
        report.display_report_rich(report.report_file, rich_logger)
        
        # Display queue statistics
        queue_stats = task_queue.get_stats()
        rich_logger.print_summary("Task Queue Statistics", {
            'completed': queue_stats['completed_tasks'],
            'failed': queue_stats['failed_tasks'],
        })
        
    except Exception as e:
        logger.exception(f"Decoupled scheduled run failed: {e}")
        rich_logger.print_error(f"Decoupled scheduled run failed: {e}", "FATAL ERROR")
        raise


def find_max_pages_simple(site_name, rules, delay, rich_logger=None):
    """
    Find maximum pages using binary search with optional progress tracking.
    
    Args:
        site_name: Name of the site being scraped
        rules: Scraper rules dictionary
        delay: Crawl delay in seconds
        rich_logger: Optional RichLogger for progress tracking
    
    Returns:
        int: Maximum page number with jobs
    """
    pagination_url = rules[Config.scraper_pagination]
    max_page = Config.max_page
    
    high = max_page
    low = 1
    iteration = 0
    
    # Estimate max iterations for binary search (log2(max_page) + buffer)
    import math
    max_iterations = int(math.log2(max_page)) + 3
    
    # Start progress tracking for binary search if logger provided
    if rich_logger:
        rich_logger.start_stage("Finding pages", site_name, max_iterations)
    
    while low <= high:
        iteration += 1
        mid = low + (high - low) // 2
        
        # Update progress message
        if rich_logger:
            rich_logger.set_stage_status_message(
                site_name, 
                "Finding pages", 
                f"Checking page {mid} (range: {low}-{high})"
            )
        
        page_url = pagination_url.replace("{page}", str(mid))
        page_exists = check_page_exists(page_url, rules, mid, delay)
        
        if page_exists:
            next_page_url = pagination_url.replace("{page}", str(mid+1))
            next_page_exists = check_page_exists(next_page_url, rules, mid+1, delay=3)
            
            if next_page_exists:
                low = mid + 1
            else:
                # Found the last page
                if rich_logger:
                    rich_logger.update_progress(site_name, "Finding pages", max_iterations - iteration + 1)
                    rich_logger.complete_stage(site_name, "Finding pages", "success")
                return mid
        else:
            high = mid - 1
        
        # Update progress after each iteration
        if rich_logger:
            rich_logger.update_progress(site_name, "Finding pages", 1)
    
    # Complete the search
    if rich_logger:
        rich_logger.complete_stage(site_name, "Finding pages", "success")
    
    return low


def execute_stage1_for_site(rules, logger, rich_logger):
    """
    Execute Stage 1 (scrape job listings) for a single site.
    
    Returns:
        Stage1Stats object
    """
    site_name = rules[Config.scraper_name]
    db = ScrapeSessionLocal()
    
    links_found = 0
    pages_scraped = 0
    errors = 0
    
    try:
        # Get crawl delay
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
        
        # Find max pages with progress tracking
        pages = find_max_pages_simple(site_name, rules, delay, rich_logger)
        
        # Start progress tracking for scraping
        rich_logger.start_stage("Stage 1", site_name, pages)
        rich_logger.set_stage_status_message(site_name, "Stage 1", f"Scraping {pages} pages")
        
        # Scrape pages
        for i in range(1, pages + 1):
            try:
                # Update status to show current page being scraped
                rich_logger.set_stage_status_message(site_name, "Stage 1", f"Scraping page {i}/{pages}")
                
                pagination = rules[Config.scraper_pagination]
                url = pagination.replace("{page}", str(i))
                
                jobs = scrape_jobs(url, rules, delay)
                links_found += len(jobs)
                pages_scraped += 1
                
                # Store jobs
                store_jobs(db, jobs)
                
                # Update progress
                rich_logger.update_progress(site_name, "Stage 1", 1)
                
            except Exception as e:
                errors += 1
                logger.error(f"Stage 1 - {site_name} page {i}: {e}")
        
        rich_logger.complete_stage(site_name, "Stage 1", "success")
        
    except Exception as e:
        errors += 1
        logger.exception(f"Stage 1 - {site_name} failed: {e}")
        rich_logger.complete_stage(site_name, "Stage 1", "error")
    
    finally:
        db.close()
    
    return Stage1Stats(
        site=site_name,
        links_found=links_found,
        pages_scraped=pages_scraped,
        errors=errors
    )


def execute_stage2_for_site(rules, logger, rich_logger):
    """
    Execute Stage 2 (scrape job details) for a single site.
    
    Returns:
        Stage2Stats object
    """
    site_name = rules[Config.scraper_name]
    db = ScrapeSessionLocal()
    today = date.today()
    
    total_jobs = 0
    success = 0
    empty = 0
    failed = 0
    http_200 = 0
    http_404 = 0
    http_other = 0
    
    try:
        # Get crawl delay
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
        
        # Get jobs without descriptions
        jobs_without_description = db.query(Job).filter(
            Job.site == site_name,
            Job.job_description.is_(None)  # Use is_(None) for proper SQL NULL comparison
        ).all()
        
        total_jobs = len(jobs_without_description)
        
        if total_jobs == 0:
            # No jobs to process - mark as complete with no progress
            rich_logger.start_stage("Stage 2", site_name, 0)
            rich_logger.complete_stage(site_name, "Stage 2", "success")
            return Stage2Stats(
                site=site_name,
                total_jobs=0,
                success=0,
                empty=0,
                failed=0
            )
        
        # Start progress tracking
        rich_logger.start_stage("Stage 2", site_name, total_jobs)
        rich_logger.set_stage_status_message(site_name, "Stage 2", f"Processing {total_jobs} jobs")
        
        # Get details selectors
        details_selectors = rules.get(Config.scraper_details, [])
        
        # Process jobs
        work_times = []
        job_index = 0
        for job in jobs_without_description:
            job_index += 1
            try:
                # Update status to show current job being processed
                rich_logger.set_stage_status_message(
                    site_name, 
                    "Stage 2", 
                    f"Processing job {job_index}/{total_jobs}"
                )
                
                # Calculate adjusted delay
                adjusted_delay = delay
                if work_times:
                    last_work_time = work_times[-1]
                    adjusted_delay = max(0, delay - last_work_time)
                
                # Fetch description
                work_start = time.time()
                description, http_status = fetch_job_description(
                    job.job_url,
                    details_selectors,
                    adjusted_delay
                )
                work_end = time.time()
                work_times.append(work_end - work_start - adjusted_delay)
                
                # Update statistics
                if http_status == 200:
                    http_200 += 1
                elif http_status == 404:
                    http_404 += 1
                elif http_status:
                    http_other += 1
                
                if description is not None:
                    job.job_description = description
                    job.updated_at = datetime.now(timezone.utc)
                    
                    if description:
                        success += 1
                    else:
                        empty += 1
                else:
                    failed += 1
                
                # Update job check
                update_job_check(db, job.id, today, http_status)
                db.commit()
                
                # Update progress
                rich_logger.update_progress(site_name, "Stage 2", 1)
                
            except Exception as e:
                failed += 1
                logger.error(f"Stage 2 - {site_name} job {job.id}: {e}")
                db.rollback()
        
        rich_logger.complete_stage(site_name, "Stage 2", "success")
    
    except Exception as e:
        logger.exception(f"Stage 2 - {site_name} failed: {e}")
        rich_logger.complete_stage(site_name, "Stage 2", "error")
    
    finally:
        db.close()
    
    return Stage2Stats(
        site=site_name,
        total_jobs=total_jobs,
        success=success,
        empty=empty,
        failed=failed,
        http_200=http_200,
        http_404=http_404,
        http_other=http_other
    )


def execute_stage3_for_site(rules, logger, rich_logger):
    """
    Execute Stage 3 (recheck alive jobs) for a single site.
    
    Returns:
        Stage3Stats object
    """
    site_name = rules[Config.scraper_name]
    db = ScrapeSessionLocal()
    today = date.today()
    
    total_checked = 0
    alive = 0
    dead = 0
    
    try:
        # Get crawl delay
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
        
        # Build query for alive jobs
        query = db.query(Job).filter(Job.site == site_name)
        
        # Get jobs where last check with HTTP status was 200, OR jobs with no HTTP status yet
        subquery = db.query(
            JobCheck.job_id,
            func.max(JobCheck.check_date).label('last_status_check_date')
        ).filter(
            JobCheck.http_status.isnot(None)
        ).group_by(JobCheck.job_id).subquery()
        
        jobs_with_status = query.join(
            subquery,
            Job.id == subquery.c.job_id
        ).join(
            JobCheck,
            and_(
                JobCheck.job_id == subquery.c.job_id,
                JobCheck.check_date == subquery.c.last_status_check_date,
                JobCheck.http_status == 200
            )
        ).all()
        
        jobs_without_status = query.outerjoin(
            JobCheck,
            and_(
                Job.id == JobCheck.job_id,
                JobCheck.http_status.isnot(None)
            )
        ).filter(JobCheck.id.is_(None)).all()
        
        jobs_to_recheck = jobs_with_status + jobs_without_status
        total_checked = len(jobs_to_recheck)
        
        if total_checked == 0:
            # No jobs to recheck - mark as complete with no progress
            rich_logger.start_stage("Stage 3", site_name, 0)
            rich_logger.complete_stage(site_name, "Stage 3", "success")
            return Stage3Stats(
                site=site_name,
                total_checked=0,
                alive=0,
                dead=0
            )
        
        # Start progress tracking
        rich_logger.start_stage("Stage 3", site_name, total_checked)
        rich_logger.set_stage_status_message(site_name, "Stage 3", f"Rechecking {total_checked} jobs")
        
        # Get details selectors
        details_selectors = rules.get(Config.scraper_details, [])
        
        # Process jobs
        work_times = []
        job_index = 0
        for job in jobs_to_recheck:
            job_index += 1
            try:
                # Update status to show current job being rechecked
                rich_logger.set_stage_status_message(
                    site_name,
                    "Stage 3",
                    f"Rechecking job {job_index}/{total_checked}"
                )
                
                # Calculate adjusted delay
                adjusted_delay = delay
                if work_times:
                    last_work_time = work_times[-1]
                    adjusted_delay = max(0, delay - last_work_time)
                
                # Fetch description
                work_start = time.time()
                description, http_status = fetch_job_description(
                    job.job_url,
                    details_selectors,
                    adjusted_delay
                )
                work_end = time.time()
                work_times.append(work_end - work_start - adjusted_delay)
                
                # Count alive vs dead
                if http_status == 200:
                    alive += 1
                else:
                    dead += 1
                
                # Update job description if needed
                has_description = job.job_description is not None and job.job_description != ""
                if not has_description and description is not None:
                    job.job_description = description
                    job.updated_at = datetime.now(timezone.utc)
                
                # Update job check
                update_job_check(db, job.id, today, http_status)
                db.commit()
                
                # Update progress
                rich_logger.update_progress(site_name, "Stage 3", 1)
                
            except Exception as e:
                dead += 1
                logger.error(f"Stage 3 - {site_name} job {job.id}: {e}")
                db.rollback()
        
        rich_logger.complete_stage(site_name, "Stage 3", "success")
    
    except Exception as e:
        logger.exception(f"Stage 3 - {site_name} failed: {e}")
        rich_logger.complete_stage(site_name, "Stage 3", "error")
    
    finally:
        db.close()
    
    return Stage3Stats(
        site=site_name,
        total_checked=total_checked,
        alive=alive,
        dead=dead
    )
