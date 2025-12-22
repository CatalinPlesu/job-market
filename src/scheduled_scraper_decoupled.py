"""
Decoupled scheduled scraping orchestrator using task queue system.
Each site progresses through stages independently without waiting for others.
"""
import json
from config.settings import Config
from src.database import SessionLocal, Job, JobCheck
from src.scrape_jobs_list import (
    get_crawl_delay_with_robotparser, find_max_pages_threaded, 
    scrape_jobs, store_jobs, ThreadProgressTracker, progress_tracker as global_progress_tracker,
    monitor_progress
)
from src.scrape_job_details import fetch_job_description, update_job_check
from src.reporting import DailyReport, Stage1Stats, Stage2Stats, Stage3Stats
from src.error_logger import get_logger
from src.database_backup import DatabaseBackup
from src.task_queue import TaskQueue, Priority
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
    backup = DatabaseBackup(Config.db_path, keep_days=3)
    
    print(f"\n{'='*80}")
    print(f"DECOUPLED SCHEDULED SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    try:
        # Create database backup before starting
        print("Creating database backup...")
        backup.backup_and_cleanup()
        print()
        
        # Load scraper rules
        with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
            ruless = json.load(file)
        
        # Initialize task queue
        task_queue = TaskQueue(max_workers=len(ruless))
        
        # Register all sites and get crawl delays
        print("Registering sites...")
        site_crawl_delays = {}
        for rules in ruless:
            site_name = rules[Config.scraper_name]
            delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
            task_queue.register_site(site_name, delay)
            site_crawl_delays[site_name] = delay
            print(f"  {site_name}: {delay}s crawl delay")
        print()
        
        # Statistics collection
        stats_collection = {
            'stage1': {},
            'stage2': {},
            'stage3': {},
        }
        stats_lock = threading.Lock()
        
        # Start task queue
        task_queue.start()
        
        # Queue all Stage 1 tasks (highest priority)
        print(f"\n{'='*80}")
        print(f"Queuing Stage 1 tasks (scrape job listings)...")
        print(f"{'='*80}\n")
        
        for rules in ruless:
            site_name = rules[Config.scraper_name]
            
            # Create wrapper function for Stage 1
            def stage1_task(rules=rules, site_name=site_name):
                try:
                    stats = execute_stage1_for_site(rules, logger)
                    with stats_lock:
                        stats_collection['stage1'][site_name] = stats
                    
                    # Queue Stage 2 for this site after Stage 1 completes
                    task_queue.add_task(
                        site_name=site_name,
                        priority=Priority.STAGE2,
                        stage_name=f"Stage 2: {site_name}",
                        task_func=stage2_task,
                        rules=rules,
                        site_name=site_name
                    )
                except Exception as e:
                    logger.exception(f"Stage 1 failed for {site_name}: {e}")
                    print(f"ERROR in Stage 1 for {site_name}: {e}")
            
            # Create wrapper function for Stage 2
            def stage2_task(rules, site_name):
                try:
                    stats = execute_stage2_for_site(rules, logger)
                    with stats_lock:
                        stats_collection['stage2'][site_name] = stats
                    
                    # Queue Stage 3 for this site after Stage 2 completes
                    task_queue.add_task(
                        site_name=site_name,
                        priority=Priority.STAGE3,
                        stage_name=f"Stage 3: {site_name}",
                        task_func=stage3_task,
                        rules=rules,
                        site_name=site_name
                    )
                except Exception as e:
                    logger.exception(f"Stage 2 failed for {site_name}: {e}")
                    print(f"ERROR in Stage 2 for {site_name}: {e}")
            
            # Create wrapper function for Stage 3
            def stage3_task(rules, site_name):
                try:
                    stats = execute_stage3_for_site(rules, logger)
                    with stats_lock:
                        stats_collection['stage3'][site_name] = stats
                except Exception as e:
                    logger.exception(f"Stage 3 failed for {site_name}: {e}")
                    print(f"ERROR in Stage 3 for {site_name}: {e}")
            
            # Add Stage 1 task to queue
            task_queue.add_task(
                site_name=site_name,
                priority=Priority.STAGE1,
                stage_name=f"Stage 1: {site_name}",
                task_func=stage1_task
            )
        
        # Wait for all tasks to complete
        print("\nWaiting for all tasks to complete...")
        task_queue.wait_completion()
        
        # Stop task queue
        task_queue.stop()
        
        print(f"\n{'='*80}")
        print(f"All stages completed!")
        print(f"{'='*80}\n")
        
        # Generate report
        print("Generating report...")
        
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
        print(f"\n{'='*80}")
        print(f"Report saved to: {report.report_file}")
        print(f"{'='*80}\n")
        
        report.display_report(report.report_file)
        
        # Display queue statistics
        queue_stats = task_queue.get_stats()
        print(f"\n{'='*80}")
        print(f"Task Queue Statistics:")
        print(f"  Completed: {queue_stats['completed_tasks']}")
        print(f"  Failed: {queue_stats['failed_tasks']}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        logger.exception(f"Decoupled scheduled run failed: {e}")
        print(f"\n{'='*80}")
        print(f"FATAL ERROR: Decoupled scheduled run failed: {e}")
        print(f"{'='*80}\n")
        raise


def execute_stage1_for_site(rules, logger):
    """
    Execute Stage 1 (scrape job listings) for a single site.
    
    Returns:
        Stage1Stats object
    """
    site_name = rules[Config.scraper_name]
    db = SessionLocal()
    
    links_found = 0
    pages_scraped = 0
    errors = 0
    
    print(f"\n[Stage 1] Starting {site_name}")
    
    try:
        # Get crawl delay
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
        
        # Find max pages
        pages = find_max_pages_threaded(0, site_name, rules, delay)
        print(f"[Stage 1] {site_name}: Found {pages} pages")
        
        # Scrape pages
        for i in range(1, pages + 1):
            try:
                pagination = rules[Config.scraper_pagination]
                url = pagination.replace("{page}", str(i))
                
                jobs = scrape_jobs(url, rules, delay)
                links_found += len(jobs)
                pages_scraped += 1
                
                # Store jobs
                store_jobs(db, jobs)
                
            except Exception as e:
                errors += 1
                logger.error(f"Stage 1 - {site_name} page {i}: {e}")
        
        print(f"[Stage 1] {site_name}: Completed - {links_found} links from {pages_scraped} pages")
        
    except Exception as e:
        errors += 1
        logger.exception(f"Stage 1 - {site_name} failed: {e}")
        print(f"[Stage 1] {site_name}: ERROR - {e}")
    
    finally:
        db.close()
    
    return Stage1Stats(
        site=site_name,
        links_found=links_found,
        pages_scraped=pages_scraped,
        errors=errors
    )


def execute_stage2_for_site(rules, logger):
    """
    Execute Stage 2 (scrape job details) for a single site.
    
    Returns:
        Stage2Stats object
    """
    site_name = rules[Config.scraper_name]
    db = SessionLocal()
    today = date.today()
    
    total_jobs = 0
    success = 0
    empty = 0
    failed = 0
    http_200 = 0
    http_404 = 0
    http_other = 0
    
    print(f"\n[Stage 2] Starting {site_name}")
    
    try:
        # Get crawl delay
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
        
        # Get jobs without descriptions
        jobs_without_description = db.query(Job).filter(
            Job.site == site_name,
            Job.job_description == None
        ).all()
        
        total_jobs = len(jobs_without_description)
        
        if total_jobs == 0:
            print(f"[Stage 2] {site_name}: No jobs to process")
            return Stage2Stats(
                site=site_name,
                total_jobs=0,
                success=0,
                empty=0,
                failed=0
            )
        
        print(f"[Stage 2] {site_name}: Processing {total_jobs} jobs")
        
        # Get details selectors
        details_selectors = rules.get(Config.scraper_details, [])
        
        # Process jobs
        work_times = []
        for job in jobs_without_description:
            try:
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
                
            except Exception as e:
                failed += 1
                logger.error(f"Stage 2 - {site_name} job {job.id}: {e}")
                db.rollback()
        
        print(f"[Stage 2] {site_name}: Completed - {success} success, {empty} empty, {failed} failed")
    
    except Exception as e:
        logger.exception(f"Stage 2 - {site_name} failed: {e}")
        print(f"[Stage 2] {site_name}: ERROR - {e}")
    
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


def execute_stage3_for_site(rules, logger):
    """
    Execute Stage 3 (recheck alive jobs) for a single site.
    
    Returns:
        Stage3Stats object
    """
    site_name = rules[Config.scraper_name]
    db = SessionLocal()
    today = date.today()
    
    total_checked = 0
    alive = 0
    dead = 0
    
    print(f"\n[Stage 3] Starting {site_name}")
    
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
            print(f"[Stage 3] {site_name}: No jobs to recheck")
            return Stage3Stats(
                site=site_name,
                total_checked=0,
                alive=0,
                dead=0
            )
        
        print(f"[Stage 3] {site_name}: Rechecking {total_checked} jobs")
        
        # Get details selectors
        details_selectors = rules.get(Config.scraper_details, [])
        
        # Process jobs
        work_times = []
        for job in jobs_to_recheck:
            try:
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
                
            except Exception as e:
                dead += 1
                logger.error(f"Stage 3 - {site_name} job {job.id}: {e}")
                db.rollback()
        
        print(f"[Stage 3] {site_name}: Completed - {alive} alive, {dead} dead")
    
    except Exception as e:
        logger.exception(f"Stage 3 - {site_name} failed: {e}")
        print(f"[Stage 3] {site_name}: ERROR - {e}")
    
    finally:
        db.close()
    
    return Stage3Stats(
        site=site_name,
        total_checked=total_checked,
        alive=alive,
        dead=dead
    )
