import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Job sites configuration
    job_sites = [
        "https://jobber.md/jobs/",
        "https://www.rabota.md/ro/jobs-moldova/",
        "https://www.delucru.md/jobs",
    ]

    # LLM Configuration
    llm_api = "https://openrouter.ai/api/v1"
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_model = "deepseek/deepseek-chat-v3.1:free"

    # Scraper Configuration
    scraper_rules = "config/scraper_rules.json"
    raw_db_path = "raw.db"
    scraper_state_path = "scraper_state.json"

    # Scraper Timeouts and Limits
    request_timeout = 10  # seconds
    max_page_search = 500  # Maximum pages to search in binary search
    default_crawl_delay = 1.0  # seconds
    min_crawl_delay = 0.5  # seconds
    max_crawl_delay = 5.0  # seconds

    # Async Configuration
    max_concurrent_requests = 10
    request_batch_delay = 0.1  # seconds between batches

    # Text Processing
    max_body_text_length = 5000  # characters

    prompt_pagination_and_job_url = """
    You are an expert web scraping specialist. Analyze the provided HTML from a job listing page and return a JSON object with the following structure:

    {
      "pagination_pattern": "URL pattern where {page} can be replaced with page numbers (e.g., 'https://example.com/jobs?page={page}', 'https://example.com/jobs/page/{page}', etc.)",
      "job_url_selector": "CSS selector within each job card that selects the link to the individual job detail page"
    }

    Analyze the HTML carefully and identify:
    1. How pagination works on this site (URL structure for different pages)
    2. The main container element that holds each job listing
    3. The specific link element within each job card that leads to the job details page

    The pagination pattern should be a template where {page} can be substituted with actual page numbers (1, 2, 3, etc.).

    Example patterns:
    - 'https://site.com/jobs?page={page}'
    - 'https://site.com/jobs/page/{page}'
    - 'https://site.com/jobs?p={page}'
    - 'https://site.com/jobs/{page}'

    Return ONLY valid JSON with no additional text or explanation.
    """

    prompt_job_fields_selector = """
    You are an expert web scraping specialist. Analyze the provided HTML from a job detail page and return a JSON array of CSS selectors that target meaningful text content related to the job posting.

    Return a JSON array containing CSS selectors for all relevant text elements on the page that could contain job-related information. The selectors should target elements that contain text content useful for job data extraction.

    Rules:
    - Each array item should be a valid CSS selector that returns text content
    - Include selectors for all meaningful text elements that could be relevant to job information
    - Use the most specific and reliable CSS selectors possible
    - Focus on text-containing elements that appear to be job-related
    - Consider various HTML elements: headings, paragraphs, spans, divs, lists, etc.
    - Include selectors for contact information, requirements, benefits, and other job details
    - Don't limit to specific categories - include any text element that appears relevant

    Return ONLY valid JSON array with no additional text or explanation.
    """
