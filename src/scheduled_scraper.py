"""
Scheduled scraping orchestrator.
Runs all scraping stages with reporting and logging.
"""
import json
from config.settings import Config
from src.database import SessionLocal, Job, JobCheck
from src.scrape_jobs_list import (
    scrape_single_site, get_crawl_delay_with_robotparser, 
    find_max_pages_threaded, scrape_jobs, store_jobs,
    ThreadProgressTracker, progress_tracker as global_progress_tracker,
    monitor_progress
)
from src.scrape_job_details import scrape_site_details, fetch_job_description, update_job_check
from src.scrape_job_recheck import recheck_site_jobs
from src.reporting import DailyReport, Stage1Stats, Stage2Stats, Stage3Stats
from src.error_logger import get_logger
from src.database_backup import DatabaseBackup
from datetime import date, datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time


def run_all_stages_scheduled():
    """
    Run all scraping stages (1, 2, 3) in sequence with reporting and error logging.
    This is the main entry point for scheduled execution.
    """
    # Initialize components
    logger = get_logger()
    report = DailyReport()
    backup = DatabaseBackup(Config.db_path, keep_days=3)
    
    print(f"\n{'='*80}")
    print(f"SCHEDULED SCRAPING RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    try:
        # Create database backup before starting
        print("Creating database backup...")
        backup.backup_and_cleanup()
        print()
        
        # Stage 1: Scrape job listings
        print("\n" + "="*80)
        print("STAGE 1: Scraping Job Listings")
        print("="*80 + "\n")
        
        try:
            stage1_stats = run_stage1_with_stats()
            for stats in stage1_stats:
                report.add_stage1_stats(stats)
        except Exception as e:
            logger.exception(f"Stage 1 failed: {e}")
            print(f"ERROR in Stage 1: {e}")
        
        # Stage 2: Get job details
        print("\n" + "="*80)
        print("STAGE 2: Scraping Job Details")
        print("="*80 + "\n")
        
        try:
            stage2_stats = run_stage2_with_stats()
            for stats in stage2_stats:
                report.add_stage2_stats(stats)
        except Exception as e:
            logger.exception(f"Stage 2 failed: {e}")
            print(f"ERROR in Stage 2: {e}")
        
        # Stage 3: Recheck alive jobs
        print("\n" + "="*80)
        print("STAGE 3: Rechecking Job Status")
        print("="*80 + "\n")
        
        try:
            stage3_stats = run_stage3_with_stats()
            for stats in stage3_stats:
                report.add_stage3_stats(stats)
        except Exception as e:
            logger.exception(f"Stage 3 failed: {e}")
            print(f"ERROR in Stage 3: {e}")
        
        # Save report
        report.save()
        print(f"\n{'='*80}")
        print(f"Report saved to: {report.report_file}")
        print(f"{'='*80}\n")
        
        # Display summary
        report.display_report(report.report_file)
        
    except Exception as e:
        logger.exception(f"Scheduled run failed: {e}")
        print(f"\n{'='*80}")
        print(f"FATAL ERROR: Scheduled run failed: {e}")
        print(f"{'='*80}\n")
        raise


def run_stage1_with_stats():
    """
    Run Stage 1 (scrape job listings) and collect statistics.
    
    Returns:
        List of Stage1Stats objects
    """
    logger = get_logger()
    stats_list = []
    
    # Load scraper rules
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)
    
    # Initialize global progress tracker
    global global_progress_tracker
    from src import scrape_jobs_list
    scrape_jobs_list.progress_tracker = ThreadProgressTracker(len(ruless))
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Start progress monitor thread
        progress_monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        progress_monitor_thread.start()
        
        # Process each site
        with ThreadPoolExecutor(max_workers=len(ruless)) as executor:
            futures = {}
            for i, rules in enumerate(ruless):
                future = executor.submit(scrape_site_stage1_with_stats, i, rules, db, logger)
                futures[future] = rules[Config.scraper_name]
            
            # Collect results
            for future in as_completed(futures):
                site_name = futures[future]
                try:
                    site_stats = future.result()
                    stats_list.append(site_stats)
                except Exception as e:
                    logger.exception(f"Stage 1 failed for {site_name}: {e}")
                    # Add empty stats for failed site
                    stats_list.append(Stage1Stats(
                        site=site_name,
                        links_found=0,
                        pages_scraped=0,
                        errors=1
                    ))
        
        # Wait for monitor to finish
        time.sleep(2)
    
    finally:
        db.close()
    
    return stats_list


def scrape_site_stage1_with_stats(thread_id, rules, db, logger):
    """
    Scrape a single site and return statistics.
    
    Returns:
        Stage1Stats object
    """
    local_db = SessionLocal()
    site_name = rules[Config.scraper_name]
    links_found = 0
    pages_scraped = 0
    errors = 0
    
    try:
        # Get crawl delay
        from src import scrape_jobs_list
        progress_tracker = scrape_jobs_list.progress_tracker
        
        progress_tracker.update_progress(thread_id, site_name, 0, 0, "Reading robots.txt", "CRAWL_DELAY")
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker")
        
        # Find max pages
        progress_tracker.update_progress(thread_id, site_name, 0, 0, "Finding max pages", "PAGE_DETECTION")
        pages = find_max_pages_threaded(thread_id, site_name, rules, delay)
        
        # Scrape pages
        progress_tracker.update_progress(thread_id, site_name, 0, pages, "Starting page scraping", "SCRAPING")
        
        for i in range(1, pages + 1):
            try:
                progress_tracker.update_progress(thread_id, site_name, i, pages, f"Scraping page {i}/{pages}", "SCRAPING")
                
                pagination = rules[Config.scraper_pagination]
                url = pagination.replace("{page}", str(i))
                
                jobs = scrape_jobs(url, rules, delay)
                links_found += len(jobs)
                pages_scraped += 1
                
                # Store jobs
                store_jobs(local_db, jobs)
                
            except Exception as e:
                errors += 1
                logger.error(f"Stage 1 - {site_name} page {i}: {e}")
        
        progress_tracker.update_progress(thread_id, site_name, pages, pages, "COMPLETED", "FINISHED")
        
    except Exception as e:
        errors += 1
        logger.exception(f"Stage 1 - {site_name} failed: {e}")
    
    finally:
        local_db.close()
    
    return Stage1Stats(
        site=site_name,
        links_found=links_found,
        pages_scraped=pages_scraped,
        errors=errors
    )


def run_stage2_with_stats():
    """
    Run Stage 2 (get job details) and collect statistics.
    
    Returns:
        List of Stage2Stats objects
    """
    logger = get_logger()
    stats_list = []
    
    # Load scraper rules
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)
    
    # Helper function to avoid closure issues
    def run_stage2_for_site(site_name, rules):
        result = scrape_site_stage2_with_stats(rules, logger)
        results[site_name] = result
    
    # Process each site
    threads = []
    results = {}
    
    for rules in ruless:
        site_name = rules[Config.scraper_name]
        results[site_name] = None
        thread = threading.Thread(
            target=run_stage2_for_site,
            args=(site_name, rules)
        )
        thread.start()
        threads.append(thread)
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    # Collect results
    for site_name, site_stats in results.items():
        if site_stats:
            stats_list.append(site_stats)
    
    return stats_list


def scrape_site_stage2_with_stats(rules, logger):
    """
    Scrape job details for a site and return statistics.
    
    Returns:
        Stage2Stats object
    """
    site = rules[Config.scraper_name]
    db = SessionLocal()
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
        delay = get_crawl_delay_with_robotparser(site, user_agent="JobTaker")
        
        # Get jobs without descriptions
        jobs_without_description = db.query(Job).filter(
            Job.site == site,
            Job.job_description == None
        ).all()
        
        total_jobs = len(jobs_without_description)
        
        if total_jobs == 0:
            return Stage2Stats(
                site=site,
                total_jobs=0,
                success=0,
                empty=0,
                failed=0
            )
        
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
                logger.error(f"Stage 2 - {site} job {job.id}: {e}")
                db.rollback()
    
    except Exception as e:
        logger.exception(f"Stage 2 - {site} failed: {e}")
    
    finally:
        db.close()
    
    return Stage2Stats(
        site=site,
        total_jobs=total_jobs,
        success=success,
        empty=empty,
        failed=failed,
        http_200=http_200,
        http_404=http_404,
        http_other=http_other
    )


def run_stage3_with_stats():
    """
    Run Stage 3 (recheck alive jobs) and collect statistics.
    
    Returns:
        List of Stage3Stats objects
    """
    logger = get_logger()
    stats_list = []
    
    # Load scraper rules
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)
    
    # Helper function to avoid closure issues
    def run_stage3_for_site(site_name, rules):
        result = recheck_site_stage3_with_stats(rules, logger)
        results[site_name] = result
    
    # Process each site
    threads = []
    results = {}
    
    for rules in ruless:
        site_name = rules[Config.scraper_name]
        results[site_name] = None
        thread = threading.Thread(
            target=run_stage3_for_site,
            args=(site_name, rules)
        )
        thread.start()
        threads.append(thread)
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    # Collect results
    for site_name, site_stats in results.items():
        if site_stats:
            stats_list.append(site_stats)
    
    return stats_list


def recheck_site_stage3_with_stats(rules, logger):
    """
    Recheck jobs for a site and return statistics.
    
    Returns:
        Stage3Stats object
    """
    site = rules[Config.scraper_name]
    db = SessionLocal()
    today = date.today()
    
    total_checked = 0
    alive = 0
    dead = 0
    
    try:
        from sqlalchemy import and_, func
        
        # Get crawl delay
        delay = get_crawl_delay_with_robotparser(site, user_agent="JobTaker")
        
        # Build query for alive jobs (same logic as recheck_alive_jobs)
        query = db.query(Job).filter(Job.site == site)
        
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
            return Stage3Stats(
                site=site,
                total_checked=0,
                alive=0,
                dead=0
            )
        
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
                logger.error(f"Stage 3 - {site} job {job.id}: {e}")
                db.rollback()
    
    except Exception as e:
        logger.exception(f"Stage 3 - {site} failed: {e}")
    
    finally:
        db.close()
    
    return Stage3Stats(
        site=site,
        total_checked=total_checked,
        alive=alive,
        dead=dead
    )
