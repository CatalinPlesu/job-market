# JSON API Generation Specification

## Document Purpose
This specification defines how to generate paginated JSON files from SQLite databases to create a pseudo-API for the GitHub Pages site. The system must support efficient client-side filtering, pagination, and data access patterns.

## System Responsibilities

### Core Functions
1. Query data from SQLite databases (scrape.db, data.db)
2. Transform and sanitize data for public consumption
3. Generate paginated JSON files for job listings
4. Create intelligent index files for filtering
5. Export analysis results as JSON
6. Ensure data privacy compliance

### Out of Scope
- Database schema modifications
- Job scraping or LLM processing
- Frontend implementation
- Deployment automation (handled by separate component)

## Input Requirements

### Database Access
**Location:** Explore repository to find database paths in `config/settings.py`
- `Config.scrape_db_path` → Raw scraped jobs
- `Config.data_db_path` → LLM-processed structured data

**Schema Reference:** 
- `src/scrape_database.py` - Job, JobCheck models
- `src/data_database.py` - JobDetail and 50+ lookup tables

**Key Tables:**
- `jobs` (scrape.db): id, site, job_title, company_name, job_url, created_at, updated_at
- `job_checks` (scrape.db): job_id, check_date, http_status
- `job_details` (data.db): Fully normalized job information with FKs to lookup tables

**Time Fields for Temporal Analysis:**
- `jobs.created_at` - When job was first scraped (UTC datetime)
- `jobs.updated_at` - Last update timestamp (UTC datetime)
- `job_checks.check_date` - Date of status check
- `job_details.posting_date` - Original posting date from job ad
- `job_details.processed_at` - When LLM processed the job

### Configuration
- Pagination size (default: 50-100 jobs per page)
- Data sanitization rules
- Company blacklist for opt-outs
- Field inclusion/exclusion rules

## Output Definitions

### 1. Jobs API Structure

#### `/api/jobs/index.json`
```json
{
  "version": "1.0",
  "generated_at": "2026-01-01T00:00:00Z",
  "total_jobs": 5432,
  "total_pages": 55,
  "jobs_per_page": 100,
  "metadata": {
    "date_range": {
      "earliest": "2025-06-01",
      "latest": "2026-01-01"
    },
    "job_functions": [
      {"name": "Engineering", "count": 1234, "pages": [1, 2, 3, 15, 27]},
      {"name": "Sales", "count": 876, "pages": [1, 4, 8, 12, 28]},
      {"name": "Healthcare", "count": 654, "pages": [2, 5, 9, 13]}
    ],
    "seniority_levels": [
      {"name": "junior", "count": 2000, "pages": [1, 2, 3, 4, 5]},
      {"name": "mid", "count": 1800, "pages": [1, 3, 5, 7, 9]},
      {"name": "senior", "count": 1200, "pages": [2, 4, 6, 8]}
    ],
    "locations": [
      {"name": "Chișinău", "count": 3200, "pages": [1, 2, 3, 4]},
      {"name": "Bălți", "count": 800, "pages": [5, 6, 12]}
    ],
    "remote_work": [
      {"name": "on-site", "count": 3000, "pages": [1, 2, 3]},
      {"name": "hybrid", "count": 1500, "pages": [1, 4, 7]},
      {"name": "remote", "count": 932, "pages": [2, 5, 8]}
    ],
    "salary_ranges": [
      {"min": 0, "max": 10000, "currency": "MDL", "count": 1200, "pages": [1, 3, 5]},
      {"min": 10000, "max": 20000, "currency": "MDL", "count": 2100, "pages": [2, 4, 6]},
      {"min": 20000, "max": 50000, "currency": "MDL", "count": 1500, "pages": [7, 8, 9]}
    ],
    "companies": [
      {"name": "Company A", "count": 45, "pages": [1, 2]},
      {"name": "Company B", "count": 38, "pages": [1, 5]}
    ],
    "industries": [
      {"name": "Technology", "count": 1800, "pages": [1, 2, 3]},
      {"name": "Manufacturing", "count": 1200, "pages": [4, 5, 6]},
      {"name": "Healthcare", "count": 900, "pages": [7, 8]}
    ]
  },
  "filters": {
    "job_function": ["Engineering", "Sales", "Healthcare", "Manufacturing", "..."],
    "seniority_level": ["entry", "junior", "mid", "senior", "lead", "manager", "director"],
    "location": ["Chișinău", "Bălți", "Tiraspol", "..."],
    "remote_work": ["remote", "hybrid", "on-site"],
    "employment_type": ["full-time", "part-time", "contract", "..."],
    "industry": ["Technology", "Healthcare", "Manufacturing", "..."]
  }
}
```

**Purpose:** 
- Enable smart pagination (jump to relevant pages without loading all)
- Support client-side filtering
- Provide overview statistics
- Show which pages contain filtered results

**Page Mapping Logic:**
Each job appears on a page. Metadata includes which pages contain jobs matching specific filters. This allows the SPA to load only relevant pages when filtering.

#### `/api/jobs/page-{N}.json`
```json
{
  "version": "1.0",
  "page": 1,
  "total_pages": 55,
  "jobs_per_page": 100,
  "jobs": [
    {
      "id": 1234,
      "title": "Software Engineer",
      "job_function": "Engineering",
      "specialization": "Software Development",
      "seniority_level": "mid",
      "company": "TechCorp SRL",
      "company_size": "medium",
      "location": {
        "city": "Chișinău",
        "region": "Chișinău",
        "country": "Moldova",
        "remote_work": "hybrid"
      },
      "salary": {
        "min": 15000,
        "max": 25000,
        "currency": "MDL",
        "period": "month"
      },
      "employment": {
        "type": "full-time",
        "contract": "permanent",
        "schedule": "flexible"
      },
      "requirements": {
        "education": "bachelor",
        "experience_years": 3,
        "languages": ["Romanian", "English"],
        "hard_skills": ["Python", "JavaScript", "SQL", "Docker"],
        "soft_skills": ["Communication", "Teamwork"],
        "certifications": []
      },
      "benefits": [
        "Health insurance",
        "Professional development budget",
        "Flexible working hours"
      ],
      "posting_date": "2025-12-15",
      "source": {
        "site": "jobsite.md",
        "url": "https://jobsite.md/job/12345"
      },
      "parsed_view": {
        "responsibilities": [
          "Develop and maintain web applications",
          "Collaborate with cross-functional teams",
          "Write clean, maintainable code"
        ],
        "work_environment": ["Modern office", "Collaborative team"],
        "professional_development": ["Training budget", "Conference attendance"]
      }
    }
  ]
}
```

**Data Sanitization:**
- **EXCLUDE** from JSON: contact_emails, contact_phones, contact_person
- **AGGREGATE** if <10 jobs: Company names, small locations
- **ANONYMIZE** if requested: Company names on blacklist → "Confidential"

#### `/api/jobs/{job_id}/detail.json`
```json
{
  "version": "1.0",
  "job": {
    "id": 1234,
    "title": "Software Engineer",
    "parsed": {
      "job_function": "Engineering",
      "specialization": "Software Development",
      "seniority_level": "mid",
      "industry": "Technology",
      "company": "TechCorp SRL",
      "location": { "city": "Chișinău", "country": "Moldova", "remote_work": "hybrid" },
      "salary": { "min": 15000, "max": 25000, "currency": "MDL", "period": "month" },
      "requirements": {
        "education": "bachelor",
        "experience_years": 3,
        "languages": {"Romanian": "native", "English": "fluent"},
        "hard_skills": ["Python", "JavaScript", "SQL", "Docker"],
        "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
        "certifications": ["AWS Solutions Architect"]
      },
      "responsibilities": [
        "Develop and maintain web applications",
        "Collaborate with cross-functional teams",
        "Write clean, maintainable code",
        "Participate in code reviews"
      ],
      "benefits": ["Health insurance", "Training budget"],
      "employment": { "type": "full-time", "contract": "permanent" },
      "posting_date": "2025-12-15"
    },
    "raw": {
      "original_title": "Software Engineer - Full Stack",
      "original_company": "TechCorp SRL",
      "original_description": "We are looking for a talented Software Engineer...",
      "original_language": "en",
      "source_site": "jobsite.md",
      "source_url": "https://jobsite.md/job/12345",
      "scraped_at": "2025-12-16T08:30:00Z"
    },
    "metadata": {
      "processed_at": "2025-12-16T09:00:00Z",
      "llm_model": "openai/gpt-oss-safeguard-20b"
    }
  }
}
```

**Purpose:** Two-tab view support
- **Parsed tab:** Clean, structured, translated data (primary view)
- **Raw tab:** Original data for verification and transparency

### 2. Analysis API Structure

#### `/api/analysis/index.json`
```json
{
  "version": "1.0",
  "generated_at": "2026-01-01T00:00:00Z",
  "available_analyses": [
    {
      "id": "salary-overview",
      "title": "Salary Analysis Overview",
      "endpoint": "/api/analysis/salary-overview.json",
      "last_updated": "2026-01-01T00:00:00Z"
    },
    {
      "id": "salary-by-function",
      "title": "Salary by Job Function",
      "endpoint": "/api/analysis/salary-by-function.json"
    },
    {
      "id": "skills-demand",
      "title": "Most In-Demand Skills",
      "endpoint": "/api/analysis/skills-demand.json"
    },
    {
      "id": "market-trends",
      "title": "Job Market Trends Over Time",
      "endpoint": "/api/analysis/market-trends.json",
      "temporal": true
    }
  ],
  "data_summary": {
    "total_jobs": 5432,
    "date_range": { "start": "2025-06-01", "end": "2026-01-01" },
    "jobs_with_salary": 3200,
    "unique_companies": 234,
    "unique_skills": 456
  }
}
```

#### `/api/analysis/salary-overview.json` (Static Analysis)
```json
{
  "version": "1.0",
  "analysis_id": "salary-overview",
  "generated_at": "2026-01-01T00:00:00Z",
  "type": "static",
  "data": {
    "overall": {
      "count": 3200,
      "average": 18500,
      "median": 16000,
      "min": 5000,
      "max": 85000,
      "currency": "MDL",
      "period": "month"
    },
    "by_currency": [
      {
        "currency": "MDL",
        "count": 2800,
        "average": 17000,
        "median": 15000,
        "percentile_25": 12000,
        "percentile_75": 22000
      },
      {
        "currency": "EUR",
        "count": 300,
        "average": 2200,
        "median": 2000
      },
      {
        "currency": "USD",
        "count": 100,
        "average": 3500,
        "median": 3200
      }
    ],
    "distribution": [
      {"range": "0-10000", "count": 800, "percentage": 25},
      {"range": "10000-20000", "count": 1400, "percentage": 43.75},
      {"range": "20000-30000", "count": 600, "percentage": 18.75},
      {"range": "30000-50000", "count": 300, "percentage": 9.375},
      {"range": "50000+", "count": 100, "percentage": 3.125}
    ]
  },
  "visualization_hints": {
    "chart_types": ["histogram", "box_plot"],
    "recommended_chart": "histogram"
  }
}
```

#### `/api/analysis/market-trends.json` (Temporal Analysis)
```json
{
  "version": "1.0",
  "analysis_id": "market-trends",
  "generated_at": "2026-01-01T00:00:00Z",
  "type": "temporal",
  "granularity": "monthly",
  "data": {
    "job_posting_volume": [
      {"date": "2025-06", "count": 450, "new": 380, "closed": 320},
      {"date": "2025-07", "count": 480, "new": 410, "closed": 380},
      {"date": "2025-08", "count": 520, "new": 450, "closed": 410},
      {"date": "2025-09", "count": 550, "new": 470, "closed": 440},
      {"date": "2025-10", "count": 580, "new": 490, "closed": 460},
      {"date": "2025-11", "count": 620, "new": 520, "closed": 480},
      {"date": "2025-12", "count": 650, "new": 540, "closed": 510}
    ],
    "average_salary_trend": [
      {"date": "2025-06", "average": 17200, "median": 15500, "sample_size": 280},
      {"date": "2025-07", "average": 17500, "median": 15800, "sample_size": 310},
      {"date": "2025-08", "average": 17800, "median": 16000, "sample_size": 340},
      {"date": "2025-09", "average": 18000, "median": 16200, "sample_size": 360},
      {"date": "2025-10", "average": 18300, "median": 16400, "sample_size": 380},
      {"date": "2025-11", "average": 18500, "median": 16600, "sample_size": 400},
      {"date": "2025-12", "average": 18700, "median": 16800, "sample_size": 420}
    ],
    "remote_work_adoption": [
      {"date": "2025-06", "remote": 15, "hybrid": 25, "on_site": 60},
      {"date": "2025-07", "remote": 16, "hybrid": 26, "on_site": 58},
      {"date": "2025-08", "remote": 17, "hybrid": 27, "on_site": 56},
      {"date": "2025-09", "remote": 18, "hybrid": 28, "on_site": 54},
      {"date": "2025-10", "remote": 19, "hybrid": 29, "on_site": 52},
      {"date": "2025-11", "remote": 20, "hybrid": 30, "on_site": 50},
      {"date": "2025-12", "remote": 21, "hybrid": 31, "on_site": 48}
    ]
  },
  "visualization_hints": {
    "chart_types": ["line_chart", "area_chart"],
    "recommended_chart": "line_chart"
  }
}
```

**Temporal Analysis Strategy:**
1. Use `jobs.created_at` for job posting dates
2. Use `job_checks.check_date` + `http_status` to determine when jobs closed
3. Aggregate by month (or week if sufficient data)
4. Compute rolling averages for smoother trends
5. Track how metrics evolve: salaries, skill demand, remote work, etc.

#### `/api/analysis/salary-by-hierarchy.json` (Dynamic Hierarchy)
```json
{
  "version": "1.0",
  "analysis_id": "salary-by-hierarchy",
  "generated_at": "2026-01-01T00:00:00Z",
  "hierarchy_levels": ["job_function", "specialization", "seniority_level"],
  "data": {
    "job_function": [
      {
        "name": "Engineering",
        "count": 1234,
        "average_salary": 22000,
        "median_salary": 20000,
        "salary_range": {"min": 8000, "max": 85000},
        "specializations": [
          {
            "name": "Software Development",
            "count": 800,
            "average_salary": 24000,
            "median_salary": 22000,
            "seniority_levels": [
              {"name": "junior", "count": 200, "average_salary": 15000},
              {"name": "mid", "count": 350, "average_salary": 23000},
              {"name": "senior", "count": 200, "average_salary": 35000},
              {"name": "lead", "count": 50, "average_salary": 45000}
            ]
          },
          {
            "name": "Quality Assurance",
            "count": 150,
            "average_salary": 18000,
            "seniority_levels": [
              {"name": "junior", "count": 50, "average_salary": 12000},
              {"name": "mid", "count": 70, "average_salary": 18000},
              {"name": "senior", "count": 30, "average_salary": 27000}
            ]
          }
        ]
      },
      {
        "name": "Sales",
        "count": 876,
        "average_salary": 15000,
        "specializations": [
          {
            "name": "B2B Sales",
            "count": 400,
            "average_salary": 17000
          }
        ]
      }
    ]
  }
}
```

**Purpose:** Support drill-down analysis
- Top level: Job functions
- Second level: Specializations within each function
- Third level: Seniority levels within each specialization

## Implementation Approach

### Module Structure
```
json-generator/
├── __init__.py
├── config.py                  # Configuration and constants
├── db_connector.py            # Database access layer
├── data_sanitizer.py          # Privacy and security filters
├── jobs_generator.py          # Generate jobs API files
├── analysis_generator.py      # Generate analysis API files
├── index_builder.py           # Build intelligent index files
├── pagination.py              # Pagination logic
├── hierarchy_analyzer.py      # Dynamic hierarchy computation
├── temporal_analyzer.py       # Time-series analysis
├── json_schemas.py            # JSON schema definitions
└── main.py                    # Entry point
```

### Key Algorithms

#### 1. Intelligent Index Building
```python
def build_index(jobs, jobs_per_page):
    """
    Create index.json with metadata for efficient filtering.
    
    Algorithm:
    1. Assign each job to a page number
    2. Group jobs by filter categories (function, location, etc.)
    3. For each filter value, record which pages contain matching jobs
    4. Return index with page mappings
    """
    total_pages = ceil(len(jobs) / jobs_per_page)
    index = {
        'total_jobs': len(jobs),
        'total_pages': total_pages,
        'metadata': {}
    }
    
    # Build category mappings
    categories = ['job_function', 'seniority_level', 'city', 'remote_work']
    for category in categories:
        category_map = {}
        for i, job in enumerate(jobs):
            page = (i // jobs_per_page) + 1
            value = job.get(category)
            if value:
                if value not in category_map:
                    category_map[value] = {'count': 0, 'pages': set()}
                category_map[value]['count'] += 1
                category_map[value]['pages'].add(page)
        
        # Convert sets to sorted lists
        index['metadata'][category] = [
            {'name': k, 'count': v['count'], 'pages': sorted(v['pages'])}
            for k, v in category_map.items()
        ]
    
    return index
```

#### 2. Temporal Data Aggregation
```python
def aggregate_temporal_data(jobs, granularity='monthly'):
    """
    Aggregate job data over time for trend analysis.
    
    Uses jobs.created_at to bucket jobs into time periods.
    Computes statistics for each period.
    """
    from collections import defaultdict
    from datetime import datetime
    
    periods = defaultdict(list)
    
    for job in jobs:
        created_at = job.created_at
        if granularity == 'monthly':
            period_key = created_at.strftime('%Y-%m')
        elif granularity == 'weekly':
            period_key = created_at.strftime('%Y-W%U')
        else:  # daily
            period_key = created_at.strftime('%Y-%m-%d')
        
        periods[period_key].append(job)
    
    # Compute statistics for each period
    trend_data = []
    for period, period_jobs in sorted(periods.items()):
        trend_data.append({
            'date': period,
            'count': len(period_jobs),
            'average_salary': compute_average_salary(period_jobs),
            'new_companies': count_new_companies(period_jobs),
            # ... other metrics
        })
    
    return trend_data
```

#### 3. Dynamic Hierarchy Analysis
```python
def analyze_hierarchy(jobs, levels=['job_function', 'specialization', 'seniority_level']):
    """
    Compute statistics dynamically across job hierarchy levels.
    
    Supports drill-down from domain → specialization → seniority.
    """
    def build_tree(jobs, levels, current_level=0):
        if current_level >= len(levels):
            return None
        
        level_key = levels[current_level]
        grouped = group_by(jobs, level_key)
        
        result = []
        for value, value_jobs in grouped.items():
            node = {
                'name': value,
                'count': len(value_jobs),
                'average_salary': compute_average_salary(value_jobs),
                'median_salary': compute_median_salary(value_jobs)
            }
            
            # Recurse to next level
            if current_level < len(levels) - 1:
                next_level_key = levels[current_level + 1] + 's'  # pluralize
                node[next_level_key] = build_tree(value_jobs, levels, current_level + 1)
            
            result.append(node)
        
        return result
    
    return build_tree(jobs, levels)
```

### Data Sanitization

```python
class DataSanitizer:
    """Remove sensitive information before generating public JSON."""
    
    EXCLUDED_FIELDS = [
        'contact_emails',
        'contact_phones',
        'contact_person',
        'contact_person_id'
    ]
    
    COMPANY_BLACKLIST_FILE = 'config/company_blacklist.txt'
    
    def __init__(self):
        self.blacklist = self.load_blacklist()
    
    def sanitize_job(self, job_dict):
        """Remove sensitive fields from job dictionary."""
        sanitized = {k: v for k, v in job_dict.items() 
                     if k not in self.EXCLUDED_FIELDS}
        
        # Anonymize blacklisted companies
        if sanitized.get('company') in self.blacklist:
            sanitized['company'] = 'Confidential'
        
        return sanitized
    
    def should_aggregate(self, category_count):
        """Determine if category should be aggregated to 'Other'."""
        return category_count < 10
```

## Testing Strategy

### Unit Tests
- Database query functions
- Pagination logic
- Index building algorithm
- Data sanitization
- Hierarchy analysis
- Temporal aggregation

### Integration Tests
- Generate JSON from test database
- Validate JSON schemas
- Check file sizes
- Verify data consistency across files
- Test with various data sizes (100, 1000, 10000 jobs)

### Validation Tests
- Ensure no sensitive data in output
- Verify all jobs appear exactly once across pages
- Check page references in index are accurate
- Validate temporal data is chronological
- Confirm hierarchy totals match

## Performance Considerations

### Generation Speed
- **Target:** Generate all JSON files in <30 seconds for 10,000 jobs
- **Optimization:**
  - Batch database queries
  - Use efficient JSON serialization (orjson)
  - Parallel file writing for independent analyses
  - Cache lookup table data

### Output Size
- **Target:** Total API size <20MB
- **Monitoring:**
  - Log file sizes after generation
  - Alert if any file exceeds thresholds
  - Track growth over time

### Incremental Updates (Future)
- Detect which jobs are new/changed
- Regenerate only affected pages
- Update index intelligently
- Reduces generation time for daily updates

## Configuration Options

```python
# json-generator/config.py

class GeneratorConfig:
    # Pagination
    JOBS_PER_PAGE = 100
    
    # Privacy
    MIN_CATEGORY_SIZE = 10  # Aggregate if <10 jobs
    EXCLUDE_CONTACT_INFO = True
    COMPANY_BLACKLIST_FILE = 'config/company_blacklist.txt'
    
    # Temporal analysis
    TEMPORAL_GRANULARITY = 'monthly'  # daily, weekly, monthly
    MIN_TEMPORAL_DATA_POINTS = 3  # Need at least 3 months for trends
    
    # Output
    OUTPUT_DIR = 'pages/api'
    INDENT_JSON = False  # Set True for debugging
    USE_COMPRESSION = True  # .json.gz files
    
    # Analysis
    TOP_N_SKILLS = 20
    TOP_N_COMPANIES = 50
    HIERARCHY_LEVELS = ['job_function', 'specialization', 'seniority_level']
```

## Error Handling

### Missing Data
- Use `null` for missing fields in JSON
- Log warnings for jobs with incomplete data
- Don't skip jobs due to missing optional fields

### Database Errors
- Fail fast with clear error messages
- Log full traceback
- Don't create partial JSON files

### Large Dataset Handling
- Implement streaming for very large result sets
- Monitor memory usage
- Pagination should handle arbitrary dataset sizes

## Success Criteria

- [ ] Generates valid JSON according to schemas
- [ ] All jobs appear exactly once across pages
- [ ] Index metadata accurately reflects page contents
- [ ] No sensitive data (emails, phones) in output
- [ ] Generation completes in <30 seconds for 10,000 jobs
- [ ] Total API size <20MB
- [ ] Temporal analysis includes all available historical data
- [ ] Hierarchy analysis works for all defined levels
- [ ] All tests pass with 90%+ coverage

## Dependencies

### Python Packages
- sqlalchemy - Database ORM
- orjson - Fast JSON serialization
- python-dateutil - Date parsing
- pandas (optional) - Data aggregation helpers

### External Systems
- SQLite databases (scrape.db, data.db)
- File system access for output directory

## Integration Points

### Upstream: Database Schema
- **Contract:** SQLAlchemy models in `src/scrape_database.py`, `src/data_database.py`
- **Stability:** Schema changes require code updates
- **Testing:** Use sample databases for testing

### Downstream: SPA Frontend
- **Contract:** JSON schemas defined in this spec
- **Versioning:** Include version field in all JSON
- **Testing:** Provide sample JSON files for frontend development

### Deployment Pipeline
- **Interface:** Called as Python module or CLI command
- **Input:** Database paths
- **Output:** Directory of JSON files
- **Exit codes:** 0 for success, non-zero for errors

## Implementation Timeline

**Week 1:**
- Set up module structure
- Implement database connector
- Implement data sanitizer
- Write basic jobs pagination

**Week 2:**
- Implement index builder
- Implement basic analysis generators
- Add temporal analysis
- Add hierarchy analysis

**Week 3:**
- Testing and optimization
- Documentation
- Integration testing
- Performance tuning

## Open Questions for Implementer

1. Should we use .json or .json.gz for smaller files?
2. Fixed jobs per page (100) or dynamic based on total size?
3. Include full job description in list view or only in detail view?
4. Should temporal analysis fill gaps (months with no data)?
5. How to handle jobs with missing created_at timestamps?

## References

- Database schemas: `src/scrape_database.py`, `src/data_database.py`
- Settings: `config/settings.py`
- Analytics requirements: `ANALYTICS_SPEC.md`
- Architecture: `01-architecture-strategy.md`
