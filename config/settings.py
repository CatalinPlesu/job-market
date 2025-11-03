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
    llm_model = "deepseek/deepseek-chat-v3.1:free"

    # Scraper Configuration
    db_path = "data.db"

    # Text Processing
    max_body_text_length = 10000  # characters

    job_to_db_prompt = """
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
      "latitude": number | null, // latitude coordinate (if pre-geocoded)
      "longitude": number | null, // longitude coordinate (if pre-geocoded)
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
      
      // ============ HIRING PROCESS ============
      "application_deadline": "string" | null, // last date to apply: "2025-12-31"
      "start_date": "immediate" | "flexible" | "specific_date" | null, // when position starts
      "hiring_urgency": "urgent" | "normal" | "planning" | null, // how quickly they're hiring
      "visa_sponsorship": boolean | null, // whether company sponsors work visas
      
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
