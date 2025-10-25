import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Scraper config
    scraper_rules = "config/scraper_rules.json"
    scraper_pagination = "pagination"
    scraper_job_card = "job-card"
    scraper_job_url = "job-url"
    scraper_job_title = "job-title"
    scraper_company_name = "company-name"

    # Scraper Timeouts and Limits
    request_timeout = 10  # seconds
    max_page = 50  # Maximum pages to search in binary search
    default_crawl_delay = 1.0  # seconds
    min_crawl_delay = 0.5  # seconds
    max_crawl_delay = 5.0  # seconds

    # LLM Configuration
    llm_api = "https://openrouter.ai/api/v1"
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_model = "deepseek/deepseek-chat-v3.1:free"

    # Scraper Configuration
    db_path = "data.db"
    scraper_state_path = "state.json"

    # Text Processing
    max_body_text_length = 10000  # characters
