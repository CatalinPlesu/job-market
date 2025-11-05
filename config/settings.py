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

    # Scraper Timeouts and Limits
    request_timeout = 10  # seconds
    max_page = 2000  # Maximum pages to search in binary search
    default_crawl_delay = 1.0  # seconds
    min_crawl_delay = 0.5  # seconds
    max_crawl_delay = 5.0  # seconds

    # LLM Configuration
    llm_api = "https://openrouter.ai/api/v1"
    llm_api_key = os.getenv("LLM_API_KEY")
    # llm_model = "deepseek/deepseek-chat-v3.1:free"
    # llm_model = "nvidia/nemotron-nano-12b-v2-vl:free"
    llm_model = "minimax/minimax-m2:free"

    # Scraper Configuration
    db_path = "data.db"

    # Text Processing
    max_body_text_length = 30000  # characters

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
  "title": "string (TRANSLATE; MINIMZE)",
  "job_function": "string|null",
  "seniority_level": "entry|junior|mid|senior|lead|manager|director|executive|null",
  "industry": "string|null",
  "department": "string|null",
  "job_family": "string|null",
  "specialization": "string|null",
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

**Rules (apply only if the field exists):**
1. Missing → `null`.
2. `remote_work` → `"on-site"` if not mentioned.
3. “today” / “azi” → `2025-11-05`.
4. Moldova jobs → add `["Romanian","Russian"]` to `languages` if empty.
5. One short action per item in `responsibilities`.

**No explanations, no markdown, no extra text.**
    """
