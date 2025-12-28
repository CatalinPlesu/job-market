# Job Board HTML Exporter - Technical Specification

## 1. Overview

This document specifies the requirements for generating a static Vue.js SPA that displays job listings from the scraped database. The app will be hosted on GitHub Pages and use a JSON-based API structure.

## 2. Core Requirements

### 2.1 Job Data Export
- **Page Size**: 100 jobs per page
- **Currency Normalization**: All salaries converted to MDL for consistency
- **Status Filter**: Export only "alive" jobs (seen within last 7 days based on `JobCheck.check_date`)
- **Days Open Calculation**: Show how many days position has been open since `posting_date`

### 2.2 Job Deduplication Strategy

**Matching Rules**:
- Match on exact `job_title` and `company_name` from **raw `scrape.db` Job table** (not processed data)
- Do NOT compare `job_description`
- When same job found on multiple sites (rabota.md, jobs.md, 999.md):
  - Create single job listing
  - Show all source sites with separate URLs
  - Use tabs to compare raw data per site

**Display Logic**:
- Use processed/translated data from `data.db` for display (English)
- Keep track of all source sites and URLs for each unique job

**Important Notes**:
- Scraper already deduplicates based on URL
- Jobs can "die" and be "resurrected" (7-day threshold from `Config.job_resurrection_threshold_days`)
- Only ONE alive instance of same job at a company should exist
- Multiple historical instances possible, but export only current alive one

### 2.3 URL State Management

**Requirement**: ALL UI operations must be reflected as URL parameters for reproducibility.

**Examples**:
```
/?page=1
/?page=2&industry=5&department=12
/?page=1&city=1&remote=hybrid&salary_min=30000
/?page=5&industry=5&specialization=34&seniority=senior&has_salary=true
```

**All filterable fields must be URL parameters**:
- `page` - current page number
- `industry`, `department`, `job_family`, `specialization` - hierarchical filters (IDs)
- `city`, `region`, `country` - location filters (IDs)
- `seniority_level`, `employment_type`, `contract_type`, `work_schedule`, `remote_work` - job type filters (IDs)
- `salary_min`, `salary_max` - salary range (in MDL)
- `has_salary` - boolean filter
- `experience_min`, `experience_max` - years of experience
- `education` - required education level (ID)
- `company` - company filter (ID)
- `company_size` - company size filter (ID)
- `skills` - comma-separated skill IDs
- `languages` - comma-separated language names
- `posted_after`, `posted_before` - date filters
- `search` - free text search

### 2.4 Smart Filtering with Metadata

**Goal**: Enable jumping directly to page N with filters applied, without loading all previous pages.

**Solution**: Pre-compute job counts for all filter combinations and store in metadata.

**Requirements**:
- Metadata should be in `/api/jobs/index.json` (not separate file)
- For each filter value, store:
  - Total job count
  - Which pages contain jobs with this value
  - Valid combinations with other filters (prevent 0 results)

**Hierarchical Filters**:
```
industry → department → job_family → specialization
```
These are hierarchical, so:
- When industry selected, show only valid departments under that industry
- When department selected, show only valid job_families under that department
- When job_family selected, show only valid specializations under that job_family
- Never show options that would result in 0 jobs

**Semantic Filtering**:
- All filter dropdowns should be disabled/enabled based on current selections
- Filter values should show job counts: "Software Development (234)"
- When filters would result in 0 jobs, prevent selection or show warning

### 2.5 Salary Handling

**Currency Conversion**:
- All salaries displayed in MDL for consistency
- Store original currency and values for reference
- Exchange rates defined in config or fetched from API

**Display Format**:
- Show range: "50,000 - 80,000 MDL/month"
- Show original if different: "50,000 - 80,000 MDL/month (originally 2,500-4,000 EUR)"
- Handle missing salary gracefully

### 2.6 All Fields Filterable

**Requirement**: Every field stored in database should be filterable in UI.

**Fields from JobDetail**:
- Job classification: title, job_function, seniority_level, industry, department, job_family, specialization
- Compensation: salary range, currency, period
- Requirements: education, experience_years, languages, hard_skills, soft_skills, certifications, licenses
- Work arrangement: employment_type, contract_type, work_schedule, shift_details, remote_work, travel_required
- Location: city, region, country
- Company: company_name, company_size

**Implementation Notes**:
- Some filters are single-select (seniority_level)
- Some are multi-select (skills, languages)
- Some are ranges (salary, experience)
- Some are hierarchical (industry→department→job_family→specialization)
- Some are boolean (has_salary)

## 3. Data Structure

### 3.1 Directory Structure

```
pages/
├── index.html                    # Main SPA
├── js/
│   ├── app.js                   # Vue app initialization
│   ├── components/
│   │   ├── JobList.js          # Job cards grid
│   │   ├── JobDetail.js        # Job detail modal
│   │   ├── FilterPanel.js      # Smart filter sidebar
│   │   ├── SearchBar.js        # Search
│   │   ├── Pagination.js       # Pagination
│   │   └── DebugPanel.js       # Raw data tabs
│   ├── utils/
│   │   ├── api.js              # JSON loading
│   │   ├── url-state.js        # URL param management
│   │   ├── filters.js          # Filter logic
│   │   └── formatters.js       # Formatting helpers
│   └── store/
│       └── state.js            # App state
├── css/
│   └── styles.css
└── api/
    ├── metadata.json           # Global metadata
    ├── jobs/
    │   ├── index.json          # **Main metadata + pages info**
    │   ├── page-1.json
    │   ├── page-2.json
    │   └── ...
    ├── lookups/
    │   ├── industries.json
    │   ├── departments.json
    │   ├── job_families.json
    │   ├── specializations.json
    │   ├── cities.json
    │   ├── companies.json
    │   ├── skills.json
    │   └── ... (all lookup tables)
    └── analytics/
        ├── summary.json
        ├── salary-by-city.json
        └── ...
```

### 3.2 Key JSON Files

#### `/api/jobs/index.json` - **Critical File**

This file contains all metadata needed for smart filtering without loading all pages.

```json
{
  "generated_at": "2025-12-28T20:00:00Z",
  "total_jobs": 1523,
  "total_pages": 16,
  "jobs_per_page": 100,
  
  "filter_metadata": {
    "industries": {
      "5": {
        "name": "Information Technology",
        "jobs_count": 450,
        "pages": [1, 2, 3, 4, 5],
        "departments": [12, 15, 18],
        "avg_salary_mdl": 65000
      },
      "8": {
        "name": "Finance",
        "jobs_count": 120,
        "pages": [1, 3, 6],
        "departments": [20, 21],
        "avg_salary_mdl": 55000
      }
    },
    
    "departments": {
      "12": {
        "name": "Software Engineering",
        "parent_industry": 5,
        "jobs_count": 320,
        "pages": [1, 2, 3, 4],
        "job_families": [25, 26, 27]
      }
    },
    
    "job_families": {
      "25": {
        "name": "Backend Development",
        "parent_department": 12,
        "jobs_count": 150,
        "pages": [1, 2, 3],
        "specializations": [45, 46]
      }
    },
    
    "specializations": {
      "45": {
        "name": "Python Development",
        "parent_job_family": 25,
        "jobs_count": 80,
        "pages": [1, 2]
      }
    },
    
    "cities": {
      "1": {
        "name": "Chisinau",
        "jobs_count": 1200,
        "pages": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "avg_salary_mdl": 62000
      }
    },
    
    "seniority_levels": {
      "senior": {
        "name": "Senior",
        "jobs_count": 234,
        "pages": [1, 2, 3],
        "avg_salary_mdl": 85000
      }
    },
    
    "remote_work": {
      "hybrid": {
        "jobs_count": 456,
        "pages": [1, 2, 3, 4, 5]
      }
    },
    
    "skills": {
      "Python": {
        "jobs_count": 180,
        "pages": [1, 2]
      }
    }
    
    // ... all other filter dimensions
  },
  
  "combination_index": {
    // Pre-computed valid combinations for fast lookup
    // Format: "filter1_id:filter2_id:..." → [page numbers]
    "industry_5:department_12": [1, 2, 3, 4],
    "industry_5:department_12:city_1": [1, 2, 3],
    "industry_5:seniority_senior": [1, 2]
  }
}
```

**Purpose**: 
- Enable instant filter validation (don't show options with 0 results)
- Jump directly to relevant pages
- Show job counts in filter UI
- Compute statistics without loading all pages

#### `/api/jobs/page-n.json`

```json
{
  "page": 1,
  "jobs": [
    {
      "id": "job_001",
      "title_display": "Senior Backend Developer",
      "title": "Senior Backend Developer",
      "company": "TechCorp",
      "company_id": 42,
      
      "sites": ["rabota.md", "jobs.md"],
      "urls": {
        "rabota.md": "https://rabota.md/job/12345",
        "jobs.md": "https://jobs.md/vacancy/67890"
      },
      
      "days_open": 5,
      "posting_date": "2025-12-23",
      
      // All filter IDs (for filtering logic)
      "industry_id": 5,
      "department_id": 12,
      "job_family_id": 25,
      "specialization_id": 45,
      "seniority_level_id": "senior",
      "city_id": 1,
      "region_id": 1,
      "country_id": 1,
      "remote_work_id": "hybrid",
      "employment_type_id": "full-time",
      "contract_type_id": "permanent",
      "work_schedule_id": "flexible",
      "required_education_id": "bachelor",
      "company_size_id": "medium",
      "travel_required_id": null,
      "shift_details_id": null,
      
      // Display values (from processed data.db)
      "city": "Chisinau",
      "region": "Chisinau Municipality",
      "country": "Moldova",
      "seniority_level": "Senior",
      "remote_work": "Hybrid",
      "employment_type": "Full-time",
      
      // Salary (normalized to MDL)
      "min_salary_mdl": 90000,
      "max_salary_mdl": 144000,
      "salary_period": "month",
      "has_salary": true,
      "original_currency": "EUR",
      "original_min_salary": 2500,
      "original_max_salary": 4000,
      
      // Requirements preview
      "experience_years": 5,
      "required_education": "Bachelor",
      "skills_preview": ["Python", "Django", "PostgreSQL"],
      "total_skills": 8,
      "languages_required": ["Romanian", "English"],
      
      // Quick indicators
      "has_certifications": true,
      "has_benefits": true
    }
    // ... 99 more jobs
  ]
}
```

#### `/api/jobs/details/job_001.json` (Loaded on demand when job clicked)

```json
{
  "id": "job_001",
  
  "basic": {
    "title": "Senior Backend Developer",
    "title_display": "Senior Backend Developer",
    "company": "TechCorp",
    "sites": ["rabota.md", "jobs.md"],
    "urls": {
      "rabota.md": "https://...",
      "jobs.md": "https://..."
    },
    "days_open": 5,
    "posting_date": "2025-12-23",
    "last_seen": "2025-12-28"
  },
  
  "classification": {
    "title_extracted": "Backend Developer",
    "job_function": "Software Development",
    "seniority_level": "Senior",
    "industry": "Information Technology",
    "department": "Software Engineering",
    "job_family": "Backend Development",
    "specialization": "Python Development"
  },
  
  "compensation": {
    "min_salary_mdl": 90000,
    "max_salary_mdl": 144000,
    "salary_period": "month",
    "original_currency": "EUR",
    "original_min_salary": 2500,
    "original_max_salary": 4000,
    "exchange_rate": 18.0
  },
  
  "requirements": {
    "education": "Bachelor",
    "experience_years": 5,
    "languages": [
      {"language": "Romanian", "proficiency": "fluent"},
      {"language": "English", "proficiency": "intermediate"}
    ],
    "hard_skills": ["Python", "Django", "REST API", "PostgreSQL", "Redis", "Docker", "Git", "AWS"],
    "soft_skills": ["Communication", "Problem Solving", "Team Collaboration"],
    "certifications": ["AWS Certified Developer"],
    "licenses": []
  },
  
  "work_details": {
    "employment_type": "Full-time",
    "contract_type": "Permanent",
    "work_schedule": "Flexible",
    "shift_details": null,
    "remote_work": "Hybrid",
    "travel_required": "Occasional"
  },
  
  "location": {
    "city": "Chisinau",
    "region": "Chisinau Municipality",
    "country": "Moldova",
    "full_address": "Stefan cel Mare 123, Chisinau"
  },
  
  "company_info": {
    "name": "TechCorp",
    "size": "Medium",
    "contact_person": "John Doe",
    "contact_emails": ["hr@techcorp.md"],
    "contact_phones": ["+373 22 123456"]
  },
  
  "details": {
    "responsibilities": [
      {"description": "Design and implement REST APIs", "order": 1},
      {"description": "Optimize database queries", "order": 2},
      {"description": "Mentor junior developers", "order": 3}
    ],
    "benefits": ["Health insurance", "Performance bonuses", "Remote work options"],
    "work_environment": ["Modern office", "Collaborative team"],
    "professional_development": ["Training budget", "Conference attendance"],
    "work_life_balance": ["Flexible hours", "25 vacation days"],
    "physical_requirements": [],
    "work_conditions": ["Office environment"],
    "special_requirements": []
  },
  
  "metadata": {
    "posting_date": "2025-12-23",
    "last_seen": "2025-12-28",
    "original_language": "ro",
    "processed_at": "2025-12-23T10:30:00Z"
  },
  
  "raw_data": {
    "sites": {
      "rabota.md": {
        "url": "https://rabota.md/job/12345",
        "job_title": "Senior Backend Developer",
        "company_name": "TechCorp SRL",
        "job_description": "<p>Original HTML content from rabota.md...</p>",
        "scraped_at": "2025-12-23T08:00:00Z"
      },
      "jobs.md": {
        "url": "https://jobs.md/vacancy/67890",
        "job_title": "Senior Backend Developer",
        "company_name": "TechCorp",
        "job_description": "<div>Original HTML content from jobs.md...</div>",
        "scraped_at": "2025-12-23T09:15:00Z"
      }
    }
  }
}
```

**Note**: The `raw_data.sites` section allows tab-based comparison of original scraped content per site.

#### `/api/lookups/industries.json`

```json
{
  "industries": [
    {
      "id": 5,
      "name": "Information Technology",
      "jobs_count": 450,
      "departments": [12, 15, 18],
      "avg_salary_mdl": 65000
    },
    {
      "id": 8,
      "name": "Finance",
      "jobs_count": 120,
      "departments": [20, 21],
      "avg_salary_mdl": 55000
    }
  ]
}
```

**All lookup files follow similar pattern**:
- `id` - unique identifier
- `name` - display name
- `jobs_count` - number of jobs with this value
- `parent_*` - for hierarchical lookups (departments have `parent_industry_id`)
- `children` - array of child IDs for hierarchical lookups
- Statistics where relevant (avg_salary, etc.)

## 4. UI Specification

### 4.1 Filter Panel (Left Sidebar)

**Hierarchical Filters** (industry → department → job_family → specialization):
- Show as cascading dropdowns
- Each level disabled until parent selected
- Show job counts: "Software Engineering (320)"
- Hide options with 0 jobs based on other active filters

**Location Filters**:
- Country dropdown (multi-select)
- Region dropdown (filtered by selected countries)
- City dropdown (filtered by selected regions)

**Other Filters**:
- Seniority Level (multi-select)
- Employment Type (multi-select)
- Contract Type (multi-select)
- Work Schedule (multi-select)
- Remote Work (multi-select)
- Education Level (single-select or range)
- Company Size (multi-select)
- Travel Required (multi-select)

**Range Filters**:
- Salary Range (slider, in MDL): min-max
- Experience (slider): 0-20+ years

**Multi-select Filters**:
- Skills (autocomplete, show top skills)
- Languages (multi-select)
- Certifications (autocomplete)

**Boolean Filters**:
- Has Salary checkbox
- Remote Only checkbox
- Hybrid Only checkbox

**Date Filters**:
- Posted After (date picker)
- Posted Before (date picker)
- Posted in Last N Days (quick buttons: 7, 14, 30 days)

**Clear Filters Button**: Reset all filters to default

### 4.2 Job List View

**Display**:
- Grid or list layout (user toggleable)
- 100 jobs per page
- Show: title, company, location, salary, remote badge, days open, skills preview
- Multiple site indicators (badges for rabota.md, jobs.md, 999.md)

**Sorting Options**:
- Most Recent (default)
- Salary: High to Low
- Salary: Low to High
- Company A-Z
- Days Open: Newest to Oldest

**Click behavior**: Open job detail modal

### 4.3 Job Detail Modal

**Two Tabs**:

**Tab 1: Structured Details** (default, prominent):
- All sections from `details` JSON
- Clean, organized layout
- Skills as badges
- Apply buttons for each site
- If multiple sites: show "Found on 3 sites" with site badges

**Tab 2: Raw Data** (debug, less prominent):
- **Per-site tabs** if multiple sites:
  - Tab for rabota.md
  - Tab for jobs.md
  - Tab for 999.md
- Show original scraped HTML/text
- Collapsible sections
- Purpose: Debug and comparison

### 4.4 Search

- Free-text search box (top of page)
- Searches: title, company, description, skills
- Real-time filtering (debounced)
- Reflected in URL: `?search=python+developer`

### 4.5 Pagination

- Show current page and total pages
- Previous/Next buttons
- Page number input (jump to page)
- First/Last buttons
- Show: "Showing 101-200 of 1,523 jobs"

## 5. Implementation Notes

### 5.1 Export Script (Python)

**Location**: `src/generate_html_page.py`

**Main Functions**:
```python
def export_to_github_pages():
    """Main export function"""
    # 1. Query alive jobs from databases
    # 2. Deduplicate based on title + company
    # 3. Convert salaries to MDL
    # 4. Generate metadata (filter_metadata, combination_index)
    # 5. Paginate jobs (100 per page)
    # 6. Generate lookup files
    # 7. Generate analytics
    # 8. Copy Vue.js SPA files
    # 9. Write all JSON files
    pass

def get_alive_jobs() -> List[Job]:
    """Get only alive jobs (seen within 7 days)"""
    pass

def deduplicate_jobs(jobs: List[Job]) -> List[Dict]:
    """Deduplicate and merge multi-site jobs"""
    pass

def convert_salaries_to_mdl(jobs: List[Dict]) -> List[Dict]:
    """Convert all salaries to MDL"""
    pass

def generate_filter_metadata(jobs: List[Dict]) -> Dict:
    """Generate filter_metadata section for index.json"""
    pass

def generate_combination_index(jobs: List[Dict]) -> Dict:
    """Generate combination_index for fast filter combinations"""
    pass
```

**Configurable Section** (at top of file):
```python
# ============ EXPORT CONFIGURATION ============

# What to include in export (comment out to exclude)
EXPORT_SECTIONS = [
    'basic',
    'classification',
    'compensation',
    'requirements',
    'work_details',
    'location',
    'company_info',
    'details',
    'metadata',
    # 'raw_data',  # Uncomment to include debug data
]

# Lookup tables to generate
EXPORT_LOOKUPS = [
    'industries',
    'departments',
    'job_families',
    'specializations',
    'cities',
    'regions',
    'countries',
    'companies',
    'company_sizes',
    'seniority_levels',
    # ... add/remove as needed
]

# Page settings
JOBS_PER_PAGE = 100

# Job status
ALIVE_THRESHOLD_DAYS = 7

# Currency conversion
TARGET_CURRENCY = 'MDL'
EXCHANGE_RATES = {
    'EUR': 19.5,
    'USD': 18.0,
    'GBP': 22.5,
    'MDL': 1.0
}
```

### 5.2 Git Deployment

**Location**: `src/deploy_pages.py` or integrated in main menu

**Workflow**:
1. Remove `pages/` directory if exists
2. Run `generate_html_page.py` to create fresh `pages/`
3. `cd pages/`
4. `rm -rf .git` (if exists)
5. `git init`
6. `git add .`
7. `git commit -m "Deploy to GitHub Pages"`
8. `git branch -M main`
9. `git remote add origin <REPO_URL>`
10. `git push -f origin main`
11. Optionally create `.github/workflows/pages.yml` if needed

**Repository**: Separate git repo for GitHub Pages (not main project repo)

### 5.3 Vue.js Components

**Technology Stack**:
- Vue.js 3 (from CDN, no build step)
- Plain CSS (or Tailwind CSS from CDN)
- No backend, purely static

**Component Structure** (in separate `.js` files):
```
js/components/
├── JobList.js       # Grid/list of job cards
├── JobCard.js       # Individual job card
├── JobDetail.js     # Job detail modal
├── FilterPanel.js   # Smart filter sidebar
├── SearchBar.js     # Search input
├── Pagination.js    # Pagination controls
└── DebugPanel.js    # Raw data tabs
```

**State Management**:
- Use Vue 3 Composition API
- Centralized state in `js/store/state.js`
- URL as source of truth for filters

## 6. Open Questions / Future Implementation

### 6.1 Analytics Implementation (TBD)

**Deferred to later phase**:
- Salary trends over time
- Top skills word clouds
- Industry distribution charts
- Hiring trends by company

**Note**: Structure `api/analytics/` folder but leave implementation details open.

### 6.2 Search Implementation (TBD)

**Options**:
- Client-side search (load all job titles/companies)
- Pre-computed search index
- Full-text search on descriptions

**Decision**: Defer to implementation phase.

### 6.3 Advanced Features (Future)

- Job alerts / saved searches
- Compare jobs side-by-side
- Company profiles
- Job recommendations
- Export to CSV/PDF

## 7. Success Criteria

1. ✅ Load time < 2 seconds for any page
2. ✅ All filters reflected in URL
3. ✅ Smart filtering (no 0-result selections)
4. ✅ Jump to page N with filters without loading all pages
5. ✅ Deduplicated jobs show all source sites
6. ✅ Per-site raw data comparison in debug tab
7. ✅ All salaries normalized to MDL
8. ✅ Only alive jobs (< 7 days old)
9. ✅ Responsive design (mobile-friendly)
10. ✅ Reproducible state (URL sharing works)

## 8. File Size Considerations

**Estimates**:
- `/api/jobs/index.json`: ~500KB-2MB (with all metadata)
- `/api/jobs/page-n.json`: ~200-500KB per page (100 jobs)
- `/api/jobs/details/job_*.json`: ~5-20KB per job
- Total for 1,500 jobs: ~20-40MB

**Optimization**:
- Gzip compression (GitHub Pages auto-serves gzipped)
- Lazy load job details
- Paginated loading
- Consider splitting `index.json` if > 2MB
