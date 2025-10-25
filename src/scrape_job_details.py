from config.settings import Config
from src.database import SessionLocal, Job, JobCheck
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, date
from sqlalchemy import and_
from src.scrape_jobs_list import get_crawl_delay_with_robotparser, format_time

def scrape_job_details():
    """
    Scrape job descriptions from job URLs and update the database.
    Creates/updates JobCheck records with HTTP status codes for today.
    """
    print("Scraping job details (Stage 2)...")
    
    # Load scraper rules
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)
    
    # Create database session
    db = SessionLocal()
    today = date.today()
    
    try:
        for rules in ruless:
            site = rules[Config.scraper_name]
            
            # Get crawl delay from robots.txt
            delay = get_crawl_delay_with_robotparser(site, user_agent="JobTaker")
            print(f"Crawl delay for {site}: {delay}s")
            
            # Get all jobs from this site that don't have descriptions yet
            jobs_without_description = db.query(Job).filter(
                Job.site == site,
                Job.job_description == None
            ).all()
            
            total_jobs = len(jobs_without_description)
            print(f"Found {total_jobs} jobs without descriptions from {site}")
            
            if total_jobs == 0:
                print(f"No jobs to scrape from {site}, skipping...")
                continue
            
            # Get details selectors from rules
            details_selectors = rules.get(Config.scraper_details, [])
            print(f"Details selectors for {site}: {details_selectors}")
            
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
                    print(f"✗ Error committing job {job.id}: {e}")
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
                estimated_total_time = elapsed_time + estimated_remaining_time
                
                print(f"{status_symbol} [{i}/{total_jobs}] Job ID: {job.id} | "
                      f"HTTP: {http_status} | "
                      f"Len: {desc_length} | "
                      f"Loop: {loop_duration:.2f}s | "
                      f"Avg: {avg_loop_time:.2f}s | "
                      f"ETA: {format_time(estimated_remaining_time)}")
            
            total_end_time = time.time()
            total_duration = total_end_time - total_start_time
            
            print(f"\n{'='*80}")
            print(f"Completed scraping {total_jobs} jobs from {site} in {format_time(total_duration)}")
            print(f"Success: {success_count} | Failed: {failed_count}")
            print(f"Average time per job: {sum(loop_times)/len(loop_times):.2f}s")
            print(f"{'='*80}\n")
    
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
        print(f"✗ Failed to fetch {url}: {e}")
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
        print(f"⚠ No content found with selectors on {url}")
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
        print(f"⚠ Error updating job check for job {job_id}: {e}")
        db.rollback()
