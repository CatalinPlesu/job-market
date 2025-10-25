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

def scrape_data():
    print("Scraping data...")
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)

    # Create database session
    db = SessionLocal()
    
    try:
        for rules in ruless:
            if rules[Config.scraper_name] != "rabota.md":
                continue
            # Stage 0 binary search for page numbers
            pages = find_max_pages(rules)
            print(f"Total pages to scrape: {pages}")

            # Stage 0.5 read delay from robots.txt
            delay = get_crawl_delay_with_robotparser(rules[Config.scraper_name], user_agent="JobTaker") 
            print(f"Crawl delay from robots.txt: {delay}s")

            # Stage 1 get job cards from paginated pages
            total_start_time = time.time()
            loop_times = []
            
            for i in range(1, pages+1):
                loop_start_time = time.time()
                
                pagination = rules[Config.scraper_pagination]
                url = pagination.replace("{page}", str(i))
                
                # Calculate adjusted delay based on last loop time
                adjusted_delay = delay
                if loop_times:
                    last_loop_time = loop_times[-1]
                    adjusted_delay = max(0, delay - last_loop_time)
                
                jobs = scrape_jobs(url, rules, adjusted_delay)
                print(f"Found {len(jobs)} jobs on page {i}/{pages}")
                
                # Store jobs in database
                store_jobs(db, jobs)
                
                loop_end_time = time.time()
                loop_duration = loop_end_time - loop_start_time
                loop_times.append(loop_duration)
                
                # Calculate statistics
                elapsed_time = loop_end_time - total_start_time
                avg_loop_time = sum(loop_times) / len(loop_times)
                remaining_pages = pages - i
                estimated_remaining_time = avg_loop_time * remaining_pages
                estimated_total_time = elapsed_time + estimated_remaining_time
                
                print(f"Loop time: {loop_duration:.2f}s | "
                      f"Avg: {avg_loop_time:.2f}s | "
                      f"Elapsed: {format_time(elapsed_time)} | "
                      f"ETA: {format_time(estimated_remaining_time)} | "
                      f"Total est: {format_time(estimated_total_time)}")
                print(f"Adjusted delay for next loop: {adjusted_delay:.2f}s")
                print("-" * 80)
            
            total_end_time = time.time()
            total_duration = total_end_time - total_start_time
            print(f"\n{'='*80}")
            print(f"Completed scraping {pages} pages in {format_time(total_duration)}")
            print(f"Average time per page: {sum(loop_times)/len(loop_times):.2f}s")
            print(f"{'='*80}\n")
    
    finally:
        db.close()

def format_time(seconds):
    """Format seconds into human-readable time string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

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
            print(f"Error processing job {job_data.get('title', 'Unknown')}: {e}")
            db.rollback()
            continue
    
    # Commit all changes at once
    try:
        db.commit()
        print(f"✓ {added_count} new | {existing_count} existing | {checked_count} checks added")
    except Exception as e:
        print(f"✗ Error committing to database: {e}")
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

def find_max_pages(rules):
    """
    On a given domain with pagination url, and start page,
    will find the number of pages that can be accessed from 1 to x
    """
    pagination_url = rules[Config.scraper_pagination]
    max_page = Config.max_page
    print(f"Finding max pages for: {pagination_url}")
    print(f"Initial range: low={1}, high={Config.max_page}")

    high = Config.max_page
    low = 1
    iteration = 0
    
    while low <= high:
        iteration += 1
        mid = low + (high - low) // 2
        print(f"Iteration {iteration}: Testing page {mid} (current range: {low} to {high})")
        
        page_url = pagination_url.replace("{page}", str(mid))
        print(f"Testing URL: {page_url}")
        
        jobs = len(scrape_jobs(page_url, rules))
        print(f"Found {jobs} jobs on page {mid}")

        if jobs > 0:
            next_page_url = pagination_url.replace("{page}", str(mid+1))
            print(f"Testing next page {mid+1} at URL: {next_page_url}")
            
            jobs2 = len(scrape_jobs(next_page_url, rules, delay = 3))
            print(f"Found {jobs2} jobs on page {mid+1}")
            
            if jobs2 > 0:
                print(f"Page {mid+1} exists with jobs, moving low to {mid + 1}")
                low = mid + 1
            else:
                print(f"Page {mid+1} has no jobs, max page found: {mid}")
                return mid
        else:
            print(f"Page {mid} has no jobs, moving high to {mid - 1}")
            high = mid - 1
    
    print(f"Binary search completed. Returning low value: {low}")
    return low

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
            'site': site_domain
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
