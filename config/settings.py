import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Scraper config
    scraper_rules = "config/scraper_rules.json"
    scraper_name = "name"
    scraper_pagination = "pagination"
    scraper_job_card = "job-card"
    scraper_job_url = "job-url"
    scraper_job_title = "job-title"
    scraper_company_name = "company-name"
    scraper_details = "details"
    scraper_page_number = "page-number"

    # Scraper Timeouts and Limits
    request_timeout = 10  # seconds
    max_page = 500  # Maximum pages to search in binary search
    default_crawl_delay = 1.0  # seconds
    min_crawl_delay = 0.5  # seconds
    max_crawl_delay = 5.0  # seconds

    # LLM Configuration
    llm_api = os.getenv("ENDPOINT")
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_model = os.getenv("MODEL")
    llm_request_timeout = 30

    # Database Configuration
    # Scrape database stores raw scraped data (Job records)
    scrape_db_path = "databases/scrape.db"
    # Data database stores LLM-processed data (JobDetail records and all lookups)
    data_db_path = "databases/data.db"
    # Legacy db_path for backward compatibility (points to data.db)
    db_path = "databases/data.db"

    # Text Processing
    max_body_text_length = 30000  # characters

    # Job Identification Settings
    # After a job is marked dead/removed for this many days, treat it as a new position if it reappears
    job_resurrection_threshold_days = 7  # days
    
    # Stage 1 Efficiency Settings
    # Stop scraping when this many consecutive jobs already exist in database
    stage1_consecutive_known_threshold = 150
    
    # Frontend Git Operations Settings
    # Remote URL for the frontend git repository (e.g., GitHub Pages repo)
    frontend_git_remote_url = os.getenv("FRONTEND_GIT_REMOTE_URL", "")
    # Branch to push to (default: main)
    frontend_git_branch = os.getenv("FRONTEND_GIT_BRANCH", "main")
    # Use fresh repo approach (remove .git, init, push --force) to keep repo size small
    # Set to False for incremental commits
    frontend_git_use_fresh_approach = os.getenv("FRONTEND_GIT_FRESH_APPROACH", "true").lower() == "true"
    
    # Debug Settings
    # Run Stage 3 (daily workflow) immediately instead of waiting for 00:00
    # Useful for testing the complete workflow without waiting
    debug_run_stage3_now = os.getenv("DEBUG_RUN_STAGE3_NOW", "false").lower() == "true"
    
    # Skip scraping stages (1 & 2) and jump directly to LLM processing and deployment
    # Useful when you already have scraped data and want to test LLM + deployment only
    debug_skip_scraping = os.getenv("DEBUG_SKIP_SCRAPING", "false").lower() == "true"

    job_to_db_prompt = """
    Extract job posting data as JSON. Translate descriptive text to English; keep proper nouns original.
    Follow this schema and rules strictly:

    ### JSON SCHEMA
    ```json
    {
      "title": "string (TRANSLATE)",
      "job_function": "string | null",
      "seniority_level": "entry | junior | mid | senior | lead | manager | director | executive | null",
      "industry": "string | null",
      "department": "string | null",
      "job_family": "string | null",
      "specialization": "string | null",
      "min_salary": "number | null",
      "max_salary": "number | null",
      "salary_currency": "mdl | eur | usd | gbp | null",
      "salary_period": "hour | month | year | null",
      "required_education": "none | highschool | vocational | associate | bachelor | master | phd | null",
      "experience_years": "number | null",
      "languages": ["string (e.g., Romanian, Russian)"] | null,
      "language_proficiency": {"LanguageName": "basic | intermediate | fluent | native"} | null,
      "hard_skills": ["string (TRANSLATE, keep tool names)"] | null,
      "soft_skills": ["string (TRANSLATE)"] | null,
      "certifications": ["string (KEEP ORIGINAL)"] | null,
      "licenses_required": ["string"] | null,
      "responsibilities": ["string (TRANSLATE, one action per item)"] | null,
      "employment_type": "full-time | part-time | contract | temporary | seasonal | null",
      "contract_type": "permanent | fixed-term | internship | apprenticeship | freelance | zero-hours | null",
      "work_schedule": "standard | flexible | shift | rotating | on-call | compressed | null",
      "shift_details": "day | night | weekend | split | null",
      "remote_work": "remote | hybrid | on-site | null",
      "travel_required": "occasional | frequent | constant | null",
      "city": "string | null",
      "region": "string | null",
      "country": "string | null",
      "full_address": "string | null",
      "company_name": "string (KEEP ORIGINAL) | null",
      "company_size": "startup | small | medium | large | enterprise | null",
      "contact_emails": ["string"] | null,
      "contact_phones": ["string"] | null,
      "contact_person": "string (KEEP ORIGINAL) | null",
      "benefits": ["string (TRANSLATE)"] | null,
      "work_environment": ["string (TRANSLATE)"] | null,
      "professional_development": ["string (TRANSLATE)"] | null,
      "work_life_balance": ["string (TRANSLATE)"] | null,
      "physical_requirements": ["string (TRANSLATE)"] | null,
      "work_conditions": ["string (TRANSLATE)"] | null,
      "special_requirements": ["string (TRANSLATE)"] | null,
      "posting_date": "YYYY-MM-DD | null",
      "original_language": "string (ISO 639-1 code, e.g., 'ro', 'ru', 'en')"
    }
    ```

    ### RULES
    1. Use `null` for missing information.
    2. Default `remote_work` to "on-site" if not specified.
    3. Convert "today" or "azi" to the current date in YYYY-MM-DD format.
    4. For Moldova, default languages to Romanian and Russian if not specified.
    5. Keep proper nouns in their original language.
    6. Translate all descriptive text to English.
    7. Return ONLY valid JSON. No markdown, explanations, or extra text.
    """


    job_to_db_prompt2 = """
Extract the job posting into JSON. Translate all descriptive text to English; keep proper nouns (company names, tools, certifications) in the original language.

Return **only** valid JSON that follows this schema:

```json
{
  "title": "string (REQUIRED - TRANSLATE; MINIMIZE)",
  "job_function": "string (REQUIRED)",
  "seniority_level": "entry|junior|mid|senior|lead|manager|director|executive (REQUIRED)",
  "industry": "string (REQUIRED)",
  "department": "string (REQUIRED)",
  "job_family": "string (REQUIRED)",
  "specialization": "string (REQUIRED)",
  "min_salary": "number|null",
  "max_salary": "number|null",
  "salary_currency": "mdl|eur|usd|gbp|null",
  "salary_period": "hour|month|year|null",
  "required_education": "none|highschool|vocational|associate|bachelor|master|phd|null",
  "experience_years": "number|null",
  "languages": ["string"]|null,
  "language_proficiency": {"Language": "basic|intermediate|fluent|native"}|null,
  "hard_skills": ["string"]|null,
  "soft_skills": ["string"]|null,
  "certifications": ["string"]|null,
  "licenses_required": ["string"]|null,
  "responsibilities": ["string"]|null,
  "employment_type": "full-time|part-time|contract|temporary|seasonal|null",
  "contract_type": "permanent|fixed-term|internship|apprenticeship|freelance|zero-hours|null",
  "work_schedule": "standard|flexible|shift|rotating|on-call|compressed|null",
  "shift_details": "day|night|weekend|split|null",
  "remote_work": "remote|hybrid|on-site|null",
  "travel_required": "occasional|frequent|constant|null",
  "city": "string|null",
  "region": "string|null",
  "country": "string|null",
  "full_address": "string|null",
  "company_name": "string|null",
  "company_size": "startup|small|medium|large|enterprise|null",
  "contact_emails": ["string"]|null,
  "contact_phones": ["string"]|null,
  "contact_person": "string|null",
  "benefits": ["string"]|null,
  "work_environment": ["string"]|null,
  "professional_development": ["string"]|null,
  "work_life_balance": ["string"]|null,
  "physical_requirements": ["string"]|null,
  "work_conditions": ["string"]|null,
  "special_requirements": ["string"]|null,
  "posting_date": "YYYY-MM-DD|null",
  "original_language": "string (ISO 639-1 code)"
}
```

**Rules:**
1. **REQUIRED fields must always have a valid value** (never `null`). If not explicitly stated, infer from context.
2. Missing optional fields → `null`.
3. `remote_work` → `"on-site"` if not mentioned.
4. "today" / "azi" → `2025-11-05`.
5. Moldova jobs → add `["Romanian","Russian"]` to `languages` if empty.
6. One short action per item in `responsibilities`.

**No explanations, no markdown, no extra text.**
"""
