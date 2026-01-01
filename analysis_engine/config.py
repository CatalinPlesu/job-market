"""Configuration for analysis engine."""


class AnalysisConfig:
    """Configuration settings for analysis computations."""
    
    # Temporal settings
    GRANULARITY = 'monthly'  # daily, weekly, monthly
    MIN_DATA_POINTS = 3  # Minimum periods for trend analysis
    
    # Aggregation thresholds
    MIN_SAMPLE_SIZE = 10  # Minimum jobs for category analysis
    TOP_N_SKILLS = 20
    TOP_N_COMPANIES = 50
    
    # Hierarchy levels
    HIERARCHY = ['job_function', 'specialization', 'seniority_level']
    
    # Outlier detection
    SALARY_OUTLIER_THRESHOLD = 3.0  # Standard deviations
    
    # Cache settings
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # seconds
