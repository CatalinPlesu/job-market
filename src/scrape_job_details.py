from config.settings import Config
from src.database import SessionLocal, Job, JobCheck
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, date
from sqlalchemy import and_
from src.scrape_jobs_list import get_crawl_delay_with_robotparser, format_time
import threading
from queue import Queue

# Global print lock and buffer for organized output
print_lock = threading.Lock()
print_buffer = {}
buffer_size = 15

def scrape_job_details():
    """
    Scrape job descriptions from job URLs and update the database.
    Creates/updates JobCheck records with HTTP status codes for today.
    Processes each site in parallel using threading.
    """
    print("Scraping job details (Stage 2) - Parallel mode...")
    
    # Load scraper rules
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)
    
    # Initialize print buffer for each site
    global print_buffer
    for rules in ruless:
        site = rules[Config.scraper_name]
        print_buffer[site] = []
    
    # Create a thread for each site
    threads = []
    for rules in ruless:
        thread = threading.Thread(target=scrape_site_details, args=(rules,))
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
    
    print("\n" + "="*80)
    print("All sites completed!")
    print("="*80)


def buffered_print(site, message):
    """
    Add message to buffer and print when buffer reaches size threshold.
    Thread-safe printing with organized output per site.
    """
    global print_buffer
    
    with print_lock:
        print_buffer[site].append(message)
        
        # When buffer reaches threshold, print all messages for this site
        if len(print_buffer[site]) >= buffer_size:
            for msg in print_buffer[site]:
                print(msg)
            print_buffer[site] = []  # Clear buffer


def scrape_site_details(rules):
    """
    Scrape job details for a single site.
    Each site runs in its own thread with its own database connection.
    
    Args:
        rules (dict): Scraper rules for the site
    """
    site = rules[Config.scraper_name]
    
    # Each thread gets its own database session
    db = SessionLocal()
    today = date.today()
    
    try:
        # Get crawl delay from robots.txt
        delay = get_crawl_delay_with_robotparser(site, user_agent="JobTaker")
        print(f"[{site:15}] Crawl delay: {delay}s")
        
        # Get all jobs from this site that don't have descriptions yet
        jobs_without_description = db.query(Job).filter(
            Job.site == site,
            Job.job_description == None
        ).all()
        
        total_jobs = len(jobs_without_description)
        print(f"[{site:15}] Found {total_jobs} jobs without descriptions")
        
        if total_jobs == 0:
            print(f"[{site:15}] No jobs to scrape, skipping...")
            return
        
        # Get details selectors from rules
        details_selectors = rules.get(Config.scraper_details, [])
        print(f"[{site:15}] Details selectors: {details_selectors}")
        
        # Track statistics
        total_start_time = time.time()
        loop_times = []
        work_times = []  # Track time spent on work (excluding delay)
        success_count = 0
        failed_count = 0
        
        for i, job in enumerate(jobs_without_description, 1):
            loop_start_time = time.time()
            
            # Calculate adjusted delay based on last work time (not loop time)
            adjusted_delay = delay
            if work_times:
                last_work_time = work_times[-1]
                adjusted_delay = max(0, delay - last_work_time)
            
            # Fetch and parse job details (delay is applied inside fetch function)
            work_start_time = time.time()
            description, http_status = fetch_job_description(
                job.job_url, 
                details_selectors,
                adjusted_delay
            )
            work_end_time = time.time()
            work_duration = work_end_time - work_start_time - adjusted_delay  # Subtract delay from work time
            
            if description:
                # Update job with description
                job.job_description = description
                job.updated_at = datetime.utcnow()
                success_count += 1
                status_symbol = "✓"
                desc_length = len(description)
            else:
                failed_count += 1
                status_symbol = "✗"
                desc_length = 0
            
            # Create or update JobCheck for today
            update_job_check(db, job.id, today, http_status)
            
            # Commit after each job
            try:
                db.commit()
            except Exception as e:
                print(f"[{site:15}] ✗ Error committing job {job.id}: {e}")
                db.rollback()
            
            # Calculate loop statistics AFTER all work is done
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
        print(f"[{site:15}] Completed scraping {total_jobs} jobs in {format_time(total_duration)}")
        print(f"[{site:15}] Success: {success_count} | Failed: {failed_count}")
        print(f"[{site:15}] Average time per job: {sum(loop_times)/len(loop_times):.2f}s")
        print(f"[{site:15}] {'='*80}\n")
    
    finally:
        db.close()


def fetch_job_description(url, selectors, delay=Config.default_crawl_delay):
    """
    Fetch job description from URL using CSS selectors.
    
    Args:
        url (str): The URL to fetch
        selectors (list): List of CSS selectors to extract text from
        delay (float): Time to wait before making the request (in seconds)
    
    Returns:
        tuple: (description_text, http_status_code)
            - description_text: Combined text from selectors, or None if failed
            - http_status_code: HTTP status code from the request
    """
    # Apply delay before request
    if delay > 0:
        time.sleep(delay)
    
    try:
        response = requests.get(url, timeout=10)
        http_status = response.status_code
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Return None for description but capture status if available
        http_status = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        return None, http_status
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract text from all matching selectors
    all_text = []
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator='\n', strip=True)
            if text:
                all_text.append(text)
    
    if all_text:
        description = '\n\n'.join(all_text)
        return description, http_status
    else:
        return None, http_status


def update_job_check(db, job_id, check_date, http_status):
    """
    Create or update a JobCheck record for the given job and date.
    
    Args:
        db: SQLAlchemy database session
        job_id (int): The job ID
        check_date (date): The date of the check
        http_status (int): HTTP status code from the request
    """
    try:
        # Check if record exists for this job and date
        existing_check = db.query(JobCheck).filter(
            and_(
                JobCheck.job_id == job_id,
                JobCheck.check_date == check_date
            )
        ).first()
        
        if existing_check:
            # Update existing check with HTTP status
            existing_check.http_status = http_status
        else:
            # Create new check record
            new_check = JobCheck(
                job_id=job_id,
                check_date=check_date,
                http_status=http_status
            )
            db.add(new_check)
    
    except Exception as e:
        db.rollback()
