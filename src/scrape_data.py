from config.settings import Config
import requests
from bs4 import BeautifulSoup
import json
import json
import time
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import requests  # used only to check HTTP status if you want


def scrape_data():
    print("Scraping data...")
    with open(Config.scraper_rules, 'r', encoding='utf-8') as file:
        ruless = json.load(file)

    for rules in ruless:
        # Stage 0 binary search for page numbers
        pages = find_max_pages(rules)

        # Stage 0.5 read delay from robots.txt
        delay = get_crawl_delay_with_robotparser(rules[Config.scraper_name], user_agent="JobTaker") 
        print(delay)

        # Stage 1 get job cards from paginated pages
        # start_time = time.time()
        # print(rules[Config.scraper_pagination])
        # paginatin = rules[Config.scraper_pagination]
        # url = paginatin.replace("{page}", str(1))
        # print(scrape_jobs(url, rules))
        # end_time = time.time()
        # execution_time = end_time - start_time
        # print(f"Execution time: {execution_time:.4f} seconds")

    # Stage 2 get job details and status

def get_robots_url(site_url):
    parts = urlparse(site_url)
    scheme = parts.scheme or "http"
    netloc = parts.netloc or parts.path  # handle if user passed "example.com"
    return f"{scheme}://{netloc}/robots.txt"

def get_crawl_delay_with_robotparser(site_url, user_agent="*"):
    robots_url = get_robots_url(site_url)
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()       # fetches and parses robots.txt
    except Exception:
        # could not read robots.txt (network error) -> treat as no rules
        return Config.default_crawl_delay

    # RobotFileParser provides crawl_delay(useragent) which may return None
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
    print(pagination_url)

    high = Config.max_page
    low = 1
    while True:
        url = pagination_url.replace("{page}", str(high))
        print(url)
        # use jobs on page as indicator this page is existing, not to be deceived by sites who dont know to send back 404 - delucru.md
        jobs = scrape_jobs(url, rules)
        if len(jobs) > 0:
            # we are not sure yet what is the max mage
            low = high
            high *= 2
            print(f"Double l:{low} h:{high}")
        else:
            print("Leave")
            break
    while low <= high:
        mid = low + (high - low) // 2
        print(f"mid: {mid}")
        jobs = len(scrape_jobs(
            pagination_url.replace("{page}", str(mid)), rules))

        if jobs > 0:
            jobs2 = len(scrape_jobs(
                pagination_url.replace("{page}", str(mid+1)), rules))
            if jobs2 > 0:
                low = mid + 1
            else:
                print(pagination_url.replace("{page}", str(mid)))
                return mid
        else:
            high = mid - 1


def scrape_jobs(url, rules, delay = Config.default_crawl_delay):
    """
    Scrapes job listings from a given URL using configurable CSS selectors.

    Args:
        url (str): The URL of the page containing job listings.
        rules (dict): A dictionary containing CSS selectors for scraping.

    Returns:
        list: A list of dictionaries containing job data (index, url, title, company).
    """
    # Send a GET request to the URL
    time.sleep(delay)
    response = requests.get(url)
    try:
        response.raise_for_status()  # Raise an exception for bad status codes
    except:
        return []
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract selectors from rules
    job_card_selector = rules[Config.scraper_job_card]
    job_url_selector = rules[Config.scraper_job_url]
    job_title_selector = rules[Config.scraper_job_title]
    company_name_selector = rules[Config.scraper_company_name]

    # Find all job card elements
    job_cards = soup.select(job_card_selector)

    # List to hold the extracted job data
    jobs_data = []

    for index, card in enumerate(job_cards):
        # Initialize a dictionary for the current job
        job_data = {
            'url': None,
            'title': None,
            'company': None
        }

        # Extract data using the selectors within the current card's scope
        url_element = card.select_one(job_url_selector)
        title_element = card.select_one(job_title_selector)
        company_element = card.select_one(company_name_selector)

        if url_element:
            job_data['url'] = url_element.get(
                'href')  # Get the 'href' attribute

        if title_element:
            job_data['title'] = title_element.get_text(
                strip=True)  # Get the text content (job title)

        if company_element:
            job_data['company'] = company_element.get_text(
                strip=True)  # Get the text content (company name)

        # Add the structured data dictionary for this job to the list
        if job_data['title'] != '' and job_data['url'] != '' and job_data['company'] != '':
            jobs_data.append(job_data)

    return jobs_data
