# Issue 1: JSON Generation System

## Title
Implement JSON API Generation from Database

## Labels
`enhancement`, `json-api`, `backend`

## Description

### Objective
Build a system that exports job market data from SQLite databases to paginated JSON files, creating a pseudo-API for static hosting on GitHub Pages.

### Scope
- Query data from `scrape.db` and `data.db`
- Generate paginated job listings as JSON files
- Create intelligent index.json with metadata for filtering
- Sanitize data (remove contact information)
- Support company opt-out blacklist

### Context
This system transforms our private databases into a public-facing API. The job market scraper collects data into two SQLite databases:
- **scrape.db**: Raw scraped jobs (Job, JobCheck tables)
- **data.db**: LLM-processed structured data (JobDetail + 50+ lookup tables)

**Database schemas:** Explore `src/scrape_database.py` and `src/data_database.py` for table structure.

**Configuration:** Database paths are in `config/settings.py`.

### Input Requirements
- Access to SQLite databases (scrape.db, data.db)
- Configuration for pagination size (default: 100 jobs/page)
- Company blacklist file (optional)

### Output Definition

**File Structure:**
```
pages/api/
├── jobs/
│   ├── index.json       # Metadata + filters
│   ├── page-1.json      # Jobs 1-100
│   ├── page-2.json      # Jobs 101-200
│   └── ...
└── (analysis files created by separate issue)
```

**JSON Schemas:** See `planning/github-pages-pseudo-api/02-json-api-generation.md` for detailed schemas.

**Key Features:**
- `/api/jobs/index.json` contains comprehensive metadata for ALL filterable database fields
- Metadata includes which pages have matching jobs WITH per-page item counts
- Enhanced page structure: `{"page": 1, "count": 45}` instead of just page numbers
- Supports complex filtering on all JobDetail fields (job_function, specialization, industry, seniority, location, education, employment type, contract type, work schedule, company size, etc.)
- Each page JSON contains 100 jobs (configurable)
- No contact emails, phones, or person names in output
- Company names anonymized if on blacklist

### Independence
- Can develop with local copy of databases
- No dependency on frontend (use mock JSON for testing)
- No dependency on deployment (generate to local directory)
- Analysis system is separate (different issue)

### Integration Points

**Input:** Database files
- Use SQLAlchemy models from existing codebase
- Query both databases (can join via job_url field)

**Output:** JSON files in `pages/api/` directory
- Must follow schemas defined in specification
- Include version field for future compatibility

**Called by:** Deployment pipeline (GitHub Actions)
- Entry point: `python -m json_generator --output pages/api`
- Exit code: 0 for success, non-zero for errors

### Success Criteria
- [ ] Generates valid JSON according to schemas
- [ ] All jobs appear exactly once across pages
- [ ] Index metadata accurately maps ALL filterable fields to pages with per-page counts
- [ ] Page metadata includes `{"page": N, "count": X}` format for every field
- [ ] Metadata covers all database fields: job_function, specialization, industry, seniority_level, education_level, employment_type, contract_type, work_schedule, city, region, remote_work, company_name, company_size, and others
- [ ] No sensitive data (emails, phones) in output
- [ ] Generation completes in <30 seconds for 10,000 jobs
- [ ] Total API size <20MB
- [ ] Handles missing data gracefully (null values)
- [ ] Unit tests with 80%+ coverage

### What This Does NOT Depend On
- Frontend SPA implementation
- Deployment automation
- Analysis system
- GitHub Pages configuration

### References
- **Specification:** `planning/github-pages-pseudo-api/02-json-api-generation.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **Database models:** `src/scrape_database.py`, `src/data_database.py`

### Implementation Hints
1. Start with basic pagination (all jobs, no filtering)
2. Add index.json generation with metadata
3. Implement data sanitization
4. Add tests for edge cases (missing data, large datasets)
5. Optimize for performance
