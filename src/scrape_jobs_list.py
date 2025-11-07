from config.settings import Config
from src.database import SessionLocal, Job, JobCheck
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from datetime import datetime, date
from sqlalchemy import and_
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# Global lock for synchronized printing
print_lock = threading.Lock()

class ThreadProgressTracker:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.progress_data = {}
        self.log_messages = {}
        self.lock = threading.Lock()
        
        # Initialize data for each thread
        for i in range(num_threads):
            self.progress_data[i] = {
                'site_name': 'Initializing...',
                'current_page': 0,
                'total_pages': 0,
                'status': 'Starting...',
                'stage': 'INIT',
                'timestamp': time.time(),
                'start_time': time.time(),  # Track when this thread started
                'page_times': [],  # Track time per page for ETA calculation
                'avg_time_per_page': 0  # Average time per page
            }
            self.log_messages[i] = []
    
    def update_progress(self, thread_id, site_name, current_page, total_pages, status, stage):
        with self.lock:
            current_time = time.time()
            
            # Calculate time statistics
            start_time = self.progress_data[thread_id]['start_time']
            elapsed_time = current_time - start_time
            
            # Track page processing time
            if current_page > 0:
                if len(self.progress_data[thread_id]['page_times']) < current_page:
                    self.progress_data[thread_id]['page_times'].append(current_time)
                
                # Calculate average time per page
                if len(self.progress_data[thread_id]['page_times']) > 1:
                    page_times = self.progress_data[thread_id]['page_times']
                    total_page_time = page_times[-1] - page_times[0]
                    pages_processed = len(page_times) - 1  # Exclude initial timestamp
                    if pages_processed > 0:
                        avg_time = total_page_time / pages_processed
                        self.progress_data[thread_id]['avg_time_per_page'] = avg_time
            
            self.progress_data[thread_id] = {
                'site_name': site_name,
                'current_page': current_page,
                'total_pages': total_pages,
                'status': status,
                'stage': stage,
                'timestamp': current_time,
                'start_time': start_time,
                'elapsed_time': elapsed_time,
                'page_times': self.progress_data[thread_id]['page_times'],
                'avg_time_per_page': self.progress_data[thread_id]['avg_time_per_page']
            }
    
    def get_estimated_completion(self, thread_id):
        """Calculate estimated completion time for a thread"""
        with self.lock:
            data = self.progress_data[thread_id]
            if data['total_pages'] == 0 or data['avg_time_per_page'] == 0:
                return None, None, None
            
            remaining_pages = data['total_pages'] - data['current_page']
            estimated_remaining_time = data['avg_time_per_page'] * remaining_pages
            estimated_completion_time = time.time() + estimated_remaining_time
            
            return estimated_remaining_time, estimated_completion_time, data['avg_time_per_page']
    
    def add_log_message(self, thread_id, message):
        with self.lock:
            self.log_messages[thread_id].append(message)
            # Keep only last 3 messages per thread to avoid overflow
            if len(self.log_messages[thread_id]) > 3:
                self.log_messages[thread_id] = self.log_messages[thread_id][-3:]
    
    def get_all_data(self):
        with self.lock:
            return self.progress_data.copy(), {k: v[:] for k, v in self.log_messages.items()}

progress_tracker = None

def format_time(seconds):
    """Format seconds into human-readable time string"""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int((seconds % 3600) % 60)
        return f"{hours}h {minutes}m {secs}s"

def format_timestamp(timestamp):
    """Format timestamp to readable time"""
    if timestamp is None:
        return "N/A"
    return time.strftime('%H:%M:%S', time.localtime(timestamp))

def update_display():
    """Update the display with current progress and logs"""
    progress_data, log_messages = progress_tracker.get_all_data()
    
    # Clear screen and print current progress
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*150)
    print("SCRAPING PROGRESS MONITOR")
    print("="*150)
    
    for thread_id in sorted(progress_data.keys()):
        data = progress_data[thread_id]
        
        # Calculate progress percentage
        if data['total_pages'] > 0:
            progress_percentage = (data['current_page'] / data['total_pages']) * 100 if data['total_pages'] > 0 else 0
            bar_length = 40
            filled_length = int(bar_length * progress_percentage / 100)
            bar = '#' * filled_length + '-' * (bar_length - filled_length)
            progress_bar = f"[{bar}] {progress_percentage:.1f}% | {data['current_page']}/{data['total_pages']}"
        else:
            progress_bar = "[--------------------] 0.0% | 0/0"
        
        # Get time estimates
        estimated_remaining_time, estimated_completion_time, avg_time_per_page = progress_tracker.get_estimated_completion(thread_id)
        
        print(f"Thread {thread_id} [{data['site_name']}] {progress_bar}")
        print(f"  Status: {data['status']}")
        print(f"  Stage: {data['stage']}")
        print(f"  Elapsed: {format_time(data.get('elapsed_time'))} | Avg per page: {format_time(avg_time_per_page)} | ETA: {format_time(estimated_remaining_time)}")
        print(f"  Estimated completion: {format_timestamp(estimated_completion_time)}")
        
        # Print log messages for this thread
        if log_messages[thread_id]:
            print(f"  Recent Logs:")
            for msg in log_messages[thread_id]:
                print(f"    {msg}")
        else:
            print(f"  Recent Logs: (no recent messages)")
        
        print("-" * 150)
    
    # Calculate and display overall progress
    total_current = sum(data['current_page'] for data in progress_data.values())
    total_total = sum(data['total_pages'] for data in progress_data.values())
    
    if total_total > 0:
        overall_percentage = (total_current / total_total) * 100
        overall_bar_length = 40
        overall_filled_length = int(overall_bar_length * overall_percentage / 100)
        overall_bar = '#' * overall_filled_length + '-' * (overall_bar_length - overall_filled_length)
        print(f"OVERALL PROGRESS: [{overall_bar}] {overall_percentage:.1f}% | {total_current}/{total_total} pages")
    
    print("="*150)

def print_threaded(thread_id, message):
    """Add log message for a specific thread"""
    progress_tracker.add_log_message(thread_id, message)

def scrape_jobs_list():
    global progress_tracker
    
    print("Scraping data...")
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)

    # Initialize progress tracker
    progress_tracker = ThreadProgressTracker(len(ruless))

    # Create database session
    db = SessionLocal()
    
    try:
        # Start a thread to monitor progress
        import threading
        progress_monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        progress_monitor_thread.start()
        
        # Process each site in parallel
        with ThreadPoolExecutor(max_workers=len(ruless)) as executor:
            # Submit all site scraping tasks
            futures = []
            for i, rules in enumerate(ruless):
                future = executor.submit(scrape_single_site, i, rules, db)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print_threaded(0, f"Error in scraping task: {e}")  # Use thread 0 for errors
        
        # Stop the monitor and show final summary
        time.sleep(2)  # Give monitor time to show final status
    
    finally:
        db.close()
    
    # Final clear and summary
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*150)
    print("ALL SCRAPING TASKS COMPLETED!")
    print("="*150)

def monitor_progress():
    """Monitor and display progress for all threads"""
    while True:
        progress_data, _ = progress_tracker.get_all_data()
        
        # Check if all threads have finished (all have stage 'FINISHED')
        all_finished = all(data['stage'] == 'FINISHED' for data in progress_data.values())
        
        update_display()
        
        if all_finished:
            time.sleep(2)  # Show final status for 2 seconds before stopping
            break
        
        time.sleep(1)  # Update every second

def scrape_single_site(thread_id, rules, db):
    """
    Scrape a single site with its own rules and database session
    """
    # Create a new database session for this thread
    local_db = SessionLocal()
    
    try:
        site_name = rules[Config.scraper_name]
        
        # Stage 0 read delay from robots.txt
        progress_tracker.update_progress(thread_id, site_name, 0, 0, "Reading robots.txt", "CRAWL_DELAY")
        delay = get_crawl_delay_with_robotparser(site_name, user_agent="JobTaker") 
        print_threaded(thread_id, f"Crawl delay from robots.txt: {delay}s")

        # Stage 0 binary search for page numbers
        progress_tracker.update_progress(thread_id, site_name, 0, 0, "Finding max pages", "PAGE_DETECTION")
        pages = find_max_pages_threaded(thread_id, site_name, rules, delay)
        print_threaded(thread_id, f"Total pages to scrape: {pages}")

        # Stage 1 get job cards from paginated pages
        progress_tracker.update_progress(thread_id, site_name, 0, pages, "Starting page scraping", "SCRAPING")
        total_start_time = time.time()
        
        for i in range(1, pages+1):
            progress_tracker.update_progress(thread_id, site_name, i, pages, f"Scraping page {i}/{pages}", "SCRAPING")
            
            pagination = rules[Config.scraper_pagination]
            url = pagination.replace("{page}", str(i))
            
            jobs = scrape_jobs(url, rules, delay)
            print_threaded(thread_id, f"Found {len(jobs)} jobs on page {i}/{pages}")
            
            # Store jobs in database using local session
            store_jobs(local_db, jobs)
            
            # The progress tracker now handles time estimation automatically
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        progress_tracker.update_progress(thread_id, site_name, pages, pages, "COMPLETED", "FINISHED")
        print_threaded(thread_id, f"Completed scraping {pages} pages in {format_time(total_duration)}")
    
    finally:
        local_db.close()

def find_max_pages_threaded(thread_id, site_name, rules, delay):
    """
    On a given domain with pagination url, and start page,
    will find the number of pages that can be accessed from 1 to x
    """
    pagination_url = rules[Config.scraper_pagination]
    max_page = Config.max_page
    print_threaded(thread_id, f"Finding max pages for: {pagination_url}")

    high = Config.max_page
    low = 1
    iteration = 0
    
    while low <= high:
        iteration += 1
        mid = low + (high - low) // 2
        progress_tracker.update_progress(thread_id, site_name, 0, 0, f"Binary search iteration {iteration}, testing page {mid}", "PAGE_DETECTION")
        
        print_threaded(thread_id, f"Iteration {iteration}: Testing page {mid} (current range: {low} to {high})")
        
        page_url = pagination_url.replace("{page}", str(mid))
        print_threaded(thread_id, f"Testing URL: {page_url}")
        
        jobs = len(scrape_jobs(page_url, rules, delay))
        print_threaded(thread_id, f"Found {jobs} jobs on page {mid}")

        if jobs > 0:
            next_page_url = pagination_url.replace("{page}", str(mid+1))
            print_threaded(thread_id, f"Testing next page {mid+1} at URL: {next_page_url}")
            
            jobs2 = len(scrape_jobs(next_page_url, rules, delay = 3))
            print_threaded(thread_id, f"Found {jobs2} jobs on page {mid+1}")
            
            if jobs2 > 0:
                print_threaded(thread_id, f"Page {mid+1} exists with jobs, moving low to {mid + 1}")
                low = mid + 1
            else:
                print_threaded(thread_id, f"Page {mid+1} has no jobs, max page found: {mid}")
                return mid
        else:
            print_threaded(thread_id, f"Page {mid} has no jobs, moving high to {mid - 1}")
            high = mid - 1
    
    print_threaded(thread_id, f"Binary search completed. Returning low value: {low}")
    return low

def store_jobs(db, jobs_data):
    """
    Store scraped jobs in the database, identifying by company + title + site.
    Add job check record for today if not already checked.
    
    Args:
        db: SQLAlchemy database session
        jobs_data: List of job dictionaries from scrape_jobs()
    """
    added_count = 0
    existing_count = 0
    checked_count = 0
    today = date.today()
    
    for job_data in jobs_data:
        try:
            # Find existing job by company + title + site
            existing_job = db.query(Job).filter(
                and_(
                    Job.job_title == job_data['title'],
                    Job.company_name == job_data['company'],
                    Job.site == job_data['site']
                )
            ).first()
            
            if existing_job:
                existing_count += 1
                
                # Check if we've already checked this job today
                today_check = db.query(JobCheck).filter(
                    and_(
                        JobCheck.job_id == existing_job.id,
                        JobCheck.check_date == today
                    )
                ).first()
                
                if not today_check:
                    # Add check record for today linked to the job ID
                    new_check = JobCheck(
                        job_id=existing_job.id,
                        check_date=today,
                        http_status=None
                    )
                    db.add(new_check)
                    checked_count += 1
                
                # Update the job URL if it changed
                if existing_job.job_url != job_data['url']:
                    existing_job.job_url = job_data['url']
                    existing_job.updated_at = datetime.utcnow()
                
            else:
                # Create new job entry
                new_job = Job(
                    job_title=job_data['title'],
                    company_name=job_data['company'],
                    job_url=job_data['url'],
                    site=job_data['site'],
                    job_description=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_job)
                db.flush()
                
                # Add initial check record linked to the new job
                initial_check = JobCheck(
                    job_id=new_job.id,
                    check_date=today,
                    http_status=None
                )
                db.add(initial_check)
                
                added_count += 1
            
        except Exception as e:
            print_threaded(0, f"Error processing job {job_data.get('title', 'Unknown')}: {e}")  # Use thread 0 for errors
            db.rollback()
            continue
    
    # Commit all changes at once
    try:
        db.commit()
        print_threaded(0, f"✓ {added_count} new | {existing_count} existing | {checked_count} checks added")  # Use thread 0 for general messages
    except Exception as e:
        print_threaded(0, f"✗ Error committing to database: {e}")  # Use thread 0 for errors
        db.rollback()

def get_robots_url(site_url):
    parts = urlparse(site_url)
    scheme = parts.scheme or "http"
    netloc = parts.netloc or parts.path
    return f"{scheme}://{netloc}/robots.txt"

def get_crawl_delay_with_robotparser(site_url, user_agent="*"):
    robots_url = get_robots_url(site_url)
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return Config.default_crawl_delay

    delay = rp.crawl_delay(user_agent)
    if delay != None:
        return delay
    else:
        return Config.default_crawl_delay

def scrape_jobs(url, rules, delay=Config.default_crawl_delay):
    """
    Scrapes job listings from a given URL using configurable CSS selectors.

    Args:
        url (str): The URL of the page containing job listings.
        rules (dict): A dictionary containing CSS selectors for scraping.
        delay (float): Time to wait before making the request (in seconds).

    Returns:
        list: A list of dictionaries containing job data (url, title, company, site).
    """
    # Apply delay before request
    if delay > 0:
        time.sleep(delay)
    
    response = requests.get(url)
    try:
        response.raise_for_status()
    except:
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract selectors from rules
    job_card_selector = rules[Config.scraper_job_card]
    job_url_selector = rules[Config.scraper_job_url]
    job_title_selector = rules[Config.scraper_job_title]
    company_name_selector = rules[Config.scraper_company_name]
 
    # Extract site domain for storing and building absolute URLs
    parsed_url = urlparse(url)
    site_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    job_cards = soup.select(job_card_selector)
    jobs_data = []

    for index, card in enumerate(job_cards):
        job_data = {
            'url': None,
            'title': None,
            'company': None,
            'site': rules[Config.scraper_name]
        }

        url_element = card.select_one(job_url_selector)
        title_element = card.select_one(job_title_selector)
        company_element = card.select_one(company_name_selector)

        if url_element:
            relative_url = url_element.get('href')
            job_data['url'] = urljoin(site_domain, relative_url)

        if title_element:
            job_data['title'] = title_element.get_text(strip=True)

        if company_element:
            # Check if this is an img tag with alt attribute
            if company_element.name == 'img' and company_element.get('alt'):
                job_data['company'] = company_element.get('alt').strip()
            else:
                job_data['company'] = company_element.get_text(strip=True)

        if job_data['title'] and job_data['url'] and job_data['company']:
            jobs_data.append(job_data)

    return jobs_data
