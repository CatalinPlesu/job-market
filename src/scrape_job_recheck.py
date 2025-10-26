from config.settings import Config
from src.database import SessionLocal, Job, JobCheck
import json
import time
from datetime import datetime, date
from sqlalchemy import and_, func, or_
from src.scrape_jobs_list import get_crawl_delay_with_robotparser, format_time
from src.scrape_job_details import fetch_job_description, update_job_check, buffered_print, print_lock, print_buffer
import threading

def recheck_alive_jobs():
    """
    Re-check jobs that were "alive" (HTTP 200) in their last check.
    Updates job descriptions if empty/null and creates/updates today's JobCheck.
    Processes each site in parallel using threading.
    """
    print("Re-checking alive jobs - Parallel mode...")
    _recheck_jobs_internal(alive_only=True)


def recheck_all_jobs():
    """
    Re-check ALL jobs regardless of previous status.
    Updates job descriptions if empty/null and creates/updates today's JobCheck.
    Processes each site in parallel using threading.
    """
    print("Re-checking all jobs - Parallel mode...")
    _recheck_jobs_internal(alive_only=False)


def _recheck_jobs_internal(alive_only=True):
    """
    Internal function to re-check jobs with parallel processing.
    
    Args:
        alive_only (bool): If True, only check jobs that were alive (HTTP 200) last time.
                          If False, check all jobs.
    """
    # Load scraper rules
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)
    
    # Initialize print buffer for each site
    global print_buffer
    for rules in ruless:
        site = rules[Config.scraper_name]
        if site not in print_buffer:
            print_buffer[site] = []
    
    # Create a thread for each site
    threads = []
    for rules in ruless:
        thread = threading.Thread(target=recheck_site_jobs, args=(rules, alive_only))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Flush any remaining buffered messages
    with print_lock:
        for site, messages in print_buffer.items():
            for msg in messages:
                print(msg)
            print_buffer[site] = []
    
    print("\n" + "="*80)
    print("All sites completed!")
    print("="*80)


def recheck_site_jobs(rules, alive_only):
    """
    Re-check jobs for a single site.
    Each site runs in its own thread with its own database connection.
    
    Args:
        rules (dict): Scraper rules for the site
        alive_only (bool): If True, only check jobs that were alive last time
    """
    site = rules[Config.scraper_name]
    
    # Each thread gets its own database session
    db = SessionLocal()
    today = date.today()
    
    try:
        # Get crawl delay from robots.txt
        delay = get_crawl_delay_with_robotparser(site, user_agent="JobTaker")
        print(f"[{site:15}] Crawl delay: {delay}s")
        
        # Build query for jobs to recheck
        query = db.query(Job).filter(Job.site == site)
        
        if alive_only:
            # Get jobs where last check with HTTP status was 200, OR jobs with no HTTP status yet
            # Subquery to get the most recent check WITH http_status for each job
            subquery = db.query(
                JobCheck.job_id,
                func.max(JobCheck.check_date).label('last_status_check_date')
            ).filter(
                JobCheck.http_status.isnot(None)  # Only checks that have HTTP status
            ).group_by(JobCheck.job_id).subquery()
            
            # Get jobs that either:
            # 1. Have most recent HTTP status = 200
            # 2. Have NO checks with HTTP status (never actually fetched)
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
            
            # Get jobs with no HTTP status checks at all
            jobs_without_status = query.outerjoin(
                JobCheck,
                and_(
                    Job.id == JobCheck.job_id,
                    JobCheck.http_status.isnot(None)
                )
            ).filter(JobCheck.id.is_(None)).all()
            
            # Combine both lists
            jobs_to_recheck = jobs_with_status + jobs_without_status
            mode_label = "alive"
        else:
            jobs_to_recheck = query.all()
            mode_label = "all"
        
        total_jobs = len(jobs_to_recheck)
        
        print(f"[{site:15}] Found {total_jobs} {mode_label} jobs to recheck")
        
        if total_jobs == 0:
            print(f"[{site:15}] No jobs to recheck, skipping...")
            return
        
        # Get details selectors from rules
        details_selectors = rules.get(Config.scraper_details, [])
        print(f"[{site:15}] Details selectors: {details_selectors}")
        
        # Track statistics
        total_start_time = time.time()
        loop_times = []
        work_times = []
        success_count = 0  # Successfully got description
        empty_count = 0  # Page loaded but no content
        failed_count = 0  # HTTP errors
        updated_count = 0  # Jobs where description was updated
        skipped_count = 0  # Jobs that already had description
        
        for i, job in enumerate(jobs_to_recheck, 1):
            loop_start_time = time.time()
            
            # Check if job already has description
            has_description = job.job_description is not None and job.job_description != ""
            
            # Calculate adjusted delay
            adjusted_delay = delay
            if work_times:
                last_work_time = work_times[-1]
                adjusted_delay = max(0, delay - last_work_time)
            
            # Fetch job details
            work_start_time = time.time()
            description, http_status = fetch_job_description(
                job.job_url, 
                details_selectors,
                adjusted_delay
            )
            work_end_time = time.time()
            work_duration = work_end_time - work_start_time - adjusted_delay
            
            # Update job description only if it's empty/null AND we got new content
            description_updated = False
            if not has_description and description is not None:
                job.job_description = description
                job.updated_at = datetime.utcnow()
                description_updated = True
                updated_count += 1
            elif has_description:
                skipped_count += 1
            
            # Determine status
            if description is not None:
                if description:
                    success_count += 1
                    status_symbol = "✓"
                    desc_length = len(description)
                else:
                    empty_count += 1
                    status_symbol = "○"
                    desc_length = 0
            else:
                failed_count += 1
                status_symbol = "✗"
                desc_length = 0
            
            # Add indicator if description was updated
            if description_updated:
                status_symbol += "+"
            elif has_description:
                status_symbol += "~"  # Already had description
            
            # Create or update JobCheck for today
            update_job_check(db, job.id, today, http_status)
            
            # Commit after each job
            try:
                db.commit()
            except Exception as e:
                print(f"[{site:15}] ✗ Error committing job {job.id}: {e}")
                db.rollback()
            
            # Calculate loop statistics
            loop_end_time = time.time()
            loop_duration = loop_end_time - loop_start_time
            loop_times.append(loop_duration)
            work_times.append(work_duration)
            
            elapsed_time = loop_end_time - total_start_time
            avg_loop_time = sum(loop_times) / len(loop_times)
            remaining_jobs = total_jobs - i
            estimated_remaining_time = avg_loop_time * remaining_jobs
            
            # Use buffered print for organized output
            msg = (f"[{site:15}] {status_symbol} [{i:4}/{total_jobs:4}] "
                   f"ID: {job.id:5} | HTTP: {http_status or 'N/A':3} | "
                   f"Len: {desc_length:5} | Loop: {loop_duration:5.2f}s | "
                   f"Avg: {avg_loop_time:5.2f}s | ETA: {format_time(estimated_remaining_time):>8}")
            buffered_print(site, msg)
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # Flush remaining buffered messages for this site
        with print_lock:
            for msg in print_buffer[site]:
                print(msg)
            print_buffer[site] = []
        
        print(f"\n[{site:15}] {'='*80}")
        print(f"[{site:15}] Completed rechecking {total_jobs} jobs in {format_time(total_duration)}")
        print(f"[{site:15}] Success: {success_count} | Empty: {empty_count} | Failed: {failed_count}")
        print(f"[{site:15}] Updated: {updated_count} | Skipped (had desc): {skipped_count}")
        print(f"[{site:15}] Average time per job: {sum(loop_times)/len(loop_times):.2f}s")
        print(f"[{site:15}] {'='*80}\n")
    
    finally:
        db.close()
