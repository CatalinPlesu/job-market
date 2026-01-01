"""Configuration for JSON generator."""

class GeneratorConfig:
    """Configuration options for JSON generation."""
    
    # Pagination
    JOBS_PER_PAGE = 100
    
    # Privacy
    MIN_CATEGORY_SIZE = 10  # Aggregate if <10 jobs
    EXCLUDE_CONTACT_INFO = True
    COMPANY_BLACKLIST_FILE = 'config/company_blacklist.txt'
    
    # Output
    OUTPUT_DIR = 'pages/api'
    INDENT_JSON = False  # Set True for debugging
    
    # Version
    API_VERSION = "1.0"
    
    # Field mappings for metadata
    ONE_TO_ONE_FIELDS = [
        'title', 'job_function', 'seniority_level', 'industry', 'department',
        'job_family', 'specialization', 'education_level',
        'employment_type', 'contract_type', 'work_schedule', 'shift_details',
        'remote_work', 'travel_requirements',
        'city', 'region', 'country',
        'company_name', 'company_size',
        'currency', 'salary_period'
    ]
    
    MANY_TO_MANY_FIELDS = [
        'hard_skills', 'soft_skills', 'languages',
        'certifications', 'licenses', 'benefits',
        'work_environment', 'professional_development',
        'work_life_balance', 'physical_requirements',
        'work_conditions', 'special_requirements'
    ]
