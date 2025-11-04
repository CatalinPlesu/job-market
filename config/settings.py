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
    Extract job posting information into this JSON structure. Use null for unspecified/omitted values. Use 0 or empty arrays where appropriate as defaults.
    {
      // ============ BASIC INFO ============
      "title": "string", // job title as posted
      "job_function": "string", // normalized role: "software developer", "sales manager", "nurse", "accountant"
      "seniority_level": "entry" | "junior" | "mid" | "senior" | "lead" | "manager" | "director" | "executive" | null, // career level
      
      // ============ HIERARCHICAL CATEGORIZATION (for building taxonomies later) ============
      "industry": "string", // broad sector: "technology", "healthcare", "finance", "retail", "manufacturing"
      "department": "string", // functional area: "engineering", "sales", "operations", "hr", "marketing"
      "job_family": "string", // specific role cluster: "software development", "customer service", "accounting", "nursing"
      "specialization": "string", // niche area: "backend", "pediatrics", "tax accounting", "react developer"
      
      // ============ COMPENSATION ============
      "min_salary": number | null, // minimum salary offered
      "max_salary": number | null, // maximum salary offered
      "salary_currency": "mdl" | "eur" | "usd" | "gbp" | null, // currency code
      "salary_period": "hour" | "month" | "year" | null, // how often salary is paid
      "commission_available": boolean, // whether commission/sales incentives are offered
      "bonus_structure": ["string"], // types of bonuses: ["annual bonus", "performance bonus", "signing bonus", "quarterly bonus"]
      
      // ============ REQUIREMENTS ============
      "minimum_education": "none" | "unspecified" | "highschool" | "vocational" | "associate" | "bachelor" | "master" | "phd", // minimum education required
      "preferred_education": "string", // specific degree/field if mentioned: "computer science", "nursing", "accounting"
      "experience_years": number | null, // years of experience required
      "experience_level_required": "none" | "some" | "moderate" | "extensive", // qualitative experience level
      "languages": ["string"], // language codes required: ["en", "ro", "ru", "fr", "es"]
      "language_proficiency": {"en": "basic" | "intermediate" | "fluent" | "native"}, // specific proficiency levels if mentioned
      
      // ============ SKILLS ============
      "hard_skills": ["string"], // ALL technical/job-specific skills: ["python", "excel", "forklift operation", "salesforce", "autocad", "sql", "nursing care"]
      "soft_skills": ["string"], // behavioral/interpersonal skills: ["communication", "leadership", "time management", "teamwork", "problem solving"]
      "certifications": ["string"], // professional certifications: ["aws certified", "cpa", "pmp", "cissp", "google analytics"]
      "licenses_required": ["string"], // legal licenses needed: ["drivers license", "medical license", "security clearance", "forklift license"]
      
      // ============ JOB DETAILS ============
      "responsibilities": ["string"], // what they'll do - short action tokens: ["develop", "maintain", "sell", "manage", "analyze", "care for patients"]
      
      // ============ WORK ARRANGEMENTS ============
      "employment_type": "full-time" | "part-time" | "contract" | "temporary" | "seasonal", // type of employment
      "contract_type": "permanent" | "fixed-term" | "internship" | "apprenticeship" | "freelance" | "zero-hours", // contract nature
      "work_schedule": "standard" | "flexible" | "shift" | "rotating" | "on-call" | "compressed", // schedule type
      "shift_details": "day" | "night" | "weekend" | "split" | null, // specific shift pattern if mentioned
      "hours_per_week": number | null, // expected weekly hours
      "remote_work": "remote" | "hybrid" | "on-site", // work location arrangement
      "travel_required": "none" | "occasional" | "frequent" | "constant" | null, // travel expectations
      "travel_percentage": number | null, // percentage of time traveling (0-100)
      
      // ============ LOCATION (for mapping with Google Maps) ============
      "street_address": "string" | null, // street number and name: "123 main street", "45 victory avenue"
      "city": "string", // city name: "chisinau", "bucharest", "london"
      "region": "string", // state/province/county: "california", "ile-de-france", "chisinau municipality"
      "postal_code": "string" | null, // zip/postal code: "md-2001", "75001", "sw1a 1aa"
      "country": "string", // country name: "moldova", "romania", "france"
      "full_address": "string" | null, // complete address string for geocoding: "123 main street, chisinau, md-2001, moldova"
      "multiple_locations": boolean, // whether job spans multiple locations
      "relocation_offered": boolean, // whether company offers relocation assistance
      
      // ============ COMPANY ============
      "company_name": "string", // company/employer name
      "company_size": "startup" | "small" | "medium" | "large" | "enterprise" | null, // company size category
      "company_type": "private" | "public" | "nonprofit" | "government" | "startup" | null, // organization type
      
      // ============ CONTACT INFO (for direct outreach) ============
      "contact_email": "string" | null, // email for applications/inquiries
      "contact_phone": "string" | null, // phone number for contact
      "contact_person": "string" | null, // specific person to contact if named: "john smith", "hr department"
      "application_url": "string" | null, // direct apply link if different from source_url
      
      // ============ BENEFITS & PERKS ============
      "benefits": ["string"], // employee benefits: ["health insurance", "pension", "gym membership", "meal vouchers", "stock options"]
      "work_environment": ["string"], // workplace characteristics: ["modern office", "warehouse", "outdoor", "clinical", "coworking space"]
      "professional_development": ["string"], // growth opportunities: ["training", "conferences", "tuition reimbursement", "mentorship", "career progression"]
      "work_life_balance": ["string"], // quality of life perks: ["flexible hours", "unlimited pto", "parental leave", "remote work", "4-day week"]
      
      // ============ PHYSICAL/SPECIAL REQUIREMENTS (important for non-office jobs) ============
      "physical_requirements": ["string"], // physical demands: ["lifting 50lbs", "standing 8hrs", "driving", "climbing ladders", "repetitive motion"]
      "work_conditions": ["string"], // environmental conditions: ["outdoor", "noisy", "cleanroom", "hazardous materials", "extreme temperatures"]
      "special_requirements": ["string"], // additional requirements: ["background check", "drug test", "security clearance", "credit check", "vaccination"]
      
      // ============ METADATA (tracking info) ============
      "posting_date": "string", // when job was posted: "2025-11-03"
      "source_url": "string", // URL of original posting
      "job_board": "string", // where it was found: "linkedin", "robota.md", "indeed"
      "posting_id": "string" // unique identifier from job board
    }
    """

    job_to_db_prompt_2 = """
    Extract job posting information into this JSON structure. Use null for unspecified/omitted values. Use 0 or empty arrays where appropriate as defaults.
    {
      // ============ BASIC INFO ============
      "title": "string", // job title as posted
      "job_function": "string | null", // normalized role: "software developer", "sales manager", "nurse", "accountant"
      "seniority_level": "entry" | "junior" | "mid" | "senior" | "lead" | "manager" | "director" | "executive" | null,
      
      // ============ HIERARCHICAL CATEGORIZATION ============
      "industry": "string | null", // broad sector: "technology", "healthcare", "finance", "retail", "manufacturing"
      "department": "string | null", // functional area: "engineering", "sales", "operations", "hr", "marketing"
      "job_family": "string | null", // specific role cluster: "software development", "customer service", "accounting", "nursing"
      "specialization": "string | null", // niche area: "backend", "pediatrics", "tax accounting", "react developer"
      
      // ============ COMPENSATION ============
      "min_salary": number | null, // minimum salary offered (null if not specified)
      "max_salary": number | null, // maximum salary offered (null if not specified)
      "salary_currency": "mdl" | "eur" | "usd" | "gbp" | null, // currency code (null if not specified)
      "salary_period": "hour" | "month" | "year" | null, // payment frequency (null if not specified)
      "commission_available": boolean, // false if not mentioned
      "bonus_structure": ["string"], // empty array [] if none mentioned: ["annual bonus", "performance bonus", "signing bonus", "quarterly bonus"]
      
      // ============ REQUIREMENTS ============
      "minimum_education": "none" | "unspecified" | "highschool" | "vocational" | "associate" | "bachelor" | "master" | "phd", // "unspecified" if not mentioned
      "preferred_education": "string | null", // specific degree/field: "computer science", "nursing", "accounting" (null if not specified)
      "experience_years": number | null, // years required (null if not specified, 0 if explicitly "no experience required")
      "experience_level_required": "none" | "some" | "moderate" | "extensive", // "none" if not mentioned
      "languages": ["string"], // empty array [] if none specified: ["en", "ro", "ru", "fr", "es"]
      "language_proficiency": {"string": "basic" | "intermediate" | "fluent" | "native"} | null, // null if not specified, e.g. {"en": "fluent", "ro": "native"}
      
      // ============ SKILLS ============
      "hard_skills": ["string"], // empty array [] if none: ["python", "excel", "forklift operation", "salesforce", "autocad", "sql", "nursing care"]
      "soft_skills": ["string"], // empty array [] if none: ["communication", "leadership", "time management", "teamwork", "problem solving"]
      "certifications": ["string"], // empty array [] if none: ["aws certified", "cpa", "pmp", "cissp", "google analytics"]
      "licenses_required": ["string"], // empty array [] if none: ["drivers license", "medical license", "security clearance", "forklift license"]
      
      // ============ JOB DETAILS ============
      "responsibilities": ["string"], // empty array [] if none listed: ["develop", "maintain", "sell", "manage", "analyze", "care for patients"]
      
      // ============ WORK ARRANGEMENTS ============
      "employment_type": "full-time" | "part-time" | "contract" | "temporary" | "seasonal" | null, // null if not specified
      "contract_type": "permanent" | "fixed-term" | "internship" | "apprenticeship" | "freelance" | "zero-hours" | null, // null if not specified
      "work_schedule": "standard" | "flexible" | "shift" | "rotating" | "on-call" | "compressed" | null, // null if not specified
      "shift_details": "day" | "night" | "weekend" | "split" | null, // null if not specified
      "hours_per_week": number | null, // null if not specified, 0 if explicitly mentioned as "varies"
      "remote_work": "remote" | "hybrid" | "on-site" | null, // null if not specified
      "travel_required": "none" | "occasional" | "frequent" | "constant" | null, // null if not mentioned
      "travel_percentage": number | null, // 0-100, null if not specified
      
      // ============ LOCATION ============
      "street_address": "string | null", // null if not provided
      "city": "string | null", // null if not specified
      "region": "string | null", // state/province/county, null if not specified
      "postal_code": "string | null", // null if not provided
      "country": "string | null", // null if not specified
      "full_address": "string | null", // complete address for geocoding, null if insufficient info
      "multiple_locations": boolean, // false if single/unspecified location
      "relocation_offered": boolean, // false if not mentioned
      
      // ============ COMPANY ============
      "company_name": "string | null", // null if not provided
      "company_size": "startup" | "small" | "medium" | "large" | "enterprise" | null, // null if not specified
      "company_type": "private" | "public" | "nonprofit" | "government" | "startup" | null, // null if not specified
      
      // ============ CONTACT INFO ============
      "contact_email": "string | null", // null if not provided
      "contact_phone": "string | null", // null if not provided
      "contact_person": "string | null", // null if not specified
      "application_url": "string | null", // null if not provided or same as source_url
      
      // ============ BENEFITS & PERKS ============
      "benefits": ["string"], // empty array [] if none: ["health insurance", "pension", "gym membership", "meal vouchers", "stock options"]
      "work_environment": ["string"], // empty array [] if none: ["modern office", "warehouse", "outdoor", "clinical", "coworking space"]
      "professional_development": ["string"], // empty array [] if none: ["training", "conferences", "tuition reimbursement", "mentorship", "career progression"]
      "work_life_balance": ["string"], // empty array [] if none: ["flexible hours", "unlimited pto", "parental leave", "remote work", "4-day week"]
      
      // ============ PHYSICAL/SPECIAL REQUIREMENTS ============
      "physical_requirements": ["string"], // empty array [] if none: ["lifting 50lbs", "standing 8hrs", "driving", "climbing ladders", "repetitive motion"]
      "work_conditions": ["string"], // empty array [] if none: ["outdoor", "noisy", "cleanroom", "hazardous materials", "extreme temperatures"]
      "special_requirements": ["string"], // empty array [] if none: ["background check", "drug test", "security clearance", "credit check", "vaccination"]
      
      // ============ METADATA ============
      "posting_date": "string | null", // ISO format "2025-11-03", null if not available
      "source_url": "string | null", // null if not available
      "job_board": "string | null", // null if not specified: "linkedin", "robota.md", "indeed"
      "posting_id": "string | null", // null if not available
      "original_language": "string | null" // ISO 639-1 language code of original posting: "en", "ro", "ru", "fr", "es", "de", etc. (null if cannot be determined)
    }

    RULES:
    - **ALWAYS translate all extracted content to English** regardless of the original posting language
    - **Keep wording concise, dense, and information-rich** - use proper capitalization, clear syntax, and professional formatting
      - Capitalize proper nouns, job titles, technologies, company names, certifications
      - Use lowercase for general terms unless they're acronyms (e.g., "Python", "AWS", "SQL" but "backend development")
      - Remove filler words and redundancy - prioritize clarity and accuracy
      - Example: Instead of "the person will be responsible for developing software" use "develop software"
    - Use null for any field where information is not provided, omitted, or cannot be determined
    - Use empty arrays [] for list fields when no items are mentioned
    - Use false for boolean fields when the feature/requirement is not mentioned
    - Use 0 for numeric fields only when explicitly appropriate (e.g., "no experience required" = 0)
    - For "unspecified" states, use null rather than string values like "unspecified"
    - Only the "title" field is truly required; all others can be null/empty as appropriate
    - Detect and record the original language in "original_language" field using ISO 639-1 codes
    """
