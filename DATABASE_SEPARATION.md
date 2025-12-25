# Database Separation Architecture

## Overview

The job market scraper now uses **two separate databases** to enable independent scraping and processing workflows:

1. **scrape.db** - Stores raw scraped data
2. **data.db** - Stores LLM-processed structured data

This separation allows for flexible deployment scenarios where scraping and processing can happen on different machines.

## Database Structure

### scrape.db (Scraping Database)
Located at: `databases/scrape.db`

**Tables:**
- `jobs` - Raw job postings with basic information
  - id, site, job_title, company_name, job_url, job_description, created_at, updated_at
- `job_checks` - Historical check records for job availability
  - id, job_id, check_date, http_status

**Purpose:** Stores all scraped job data. This database is written to by:
- Stage 1: Scrape job listings (job URLs, titles, companies)
- Stage 2: Scrape job details (job descriptions)
- Stage 3: Re-check job availability

### data.db (Processed Data Database)
Located at: `databases/data.db`

**Tables:**
- `job_details` - Processed and structured job information
  - Links to job via `job_url` (not job_id since they're in different DBs)
  - Contains all normalized fields extracted by LLM
- 30+ lookup tables for normalized data (titles, skills, locations, etc.)
- Child tables (responsibilities, languages, contact info)

**Purpose:** Stores expensive LLM-processed structured data. This database is written to by:
- LLM processing stage: Extracts structured information from job descriptions

## Workflow

### Typical Scraping Machine Workflow
```
1. Run Stage 1-3 (scrape_jobs_list, scrape_job_details, recheck)
   → Writes to scrape.db
2. Copy scrape.db to processing machine
```

### Typical Processing Machine Workflow
```
1. Receive scrape.db from scraping machine
2. Run LLM processing (structure_data_with_llm)
   → Reads from scrape.db
   → Writes to data.db
3. data.db now contains expensive processed data
```

### Benefits
- **No data loss:** Copying scrape.db won't overwrite expensive LLM-processed data in data.db
- **Independent operation:** Scraping can run daily without needing LLM processing
- **Cost efficiency:** LLM processing can be triggered manually/selectively
- **Flexible deployment:** Different machines for scraping vs processing

## Database Backups

Both databases are backed up automatically:
- Location: `backups/` directory
- Retention: Last 3 days by default
- Format: `scrape_backup_YYYY-MM-DD_HH-MM-SS.db` and `data_backup_YYYY-MM-DD_HH-MM-SS.db`

Use `backup_all_databases()` from `src/database_backup.py` to backup both databases.

## Code Organization

### Scraping Operations (use scrape.db)
- `src/scrape_database.py` - Scrape database models
- `src/scrape_jobs_list.py` - Stage 1: Scrape job listings
- `src/scrape_job_details.py` - Stage 2: Scrape job details
- `src/scrape_job_recheck.py` - Stage 3: Re-check jobs
- `src/db_operations.py` - Basic DB operations for scraping

### Processing Operations (use data.db)
- `src/data_database.py` - Data database models
- `src/data_repository.py` - Repository pattern for data.db
- `src/structure_data_with_llm.py` - LLM processing (reads scrape.db, writes data.db)

### Configuration
- `config/settings.py`:
  - `scrape_db_path = "databases/scrape.db"`
  - `data_db_path = "databases/data.db"`
  - `db_path = "databases/data.db"` (legacy compatibility)

## Migration Notes

If you have an existing `data.db` with scraped jobs:
1. The old `database.py` is no longer used by the application
2. Jobs table has been split:
   - Basic job info → `scrape.db`
   - Processed details → `data.db`
3. To migrate existing data, you would need to:
   - Copy jobs table to scrape.db
   - Keep job_details and lookups in data.db

## Cross-Database Reference

Since jobs are in scrape.db and job_details are in data.db:
- JobDetail uses `job_url` (string) instead of `job_id` (foreign key)
- This allows cross-database reference without foreign key constraints
- LLM processing matches jobs by URL when checking if already processed

## Example Usage

### Scraping Only
```python
from src.scrape_jobs_list import scrape_jobs_list
from src.scrape_job_details import scrape_job_details

# Stage 1: Get job listings
scrape_jobs_list()  # Writes to scrape.db

# Stage 2: Get job details
scrape_job_details()  # Writes to scrape.db
```

### LLM Processing
```python
from src.structure_data_with_llm import structure_data_with_llm

# Process jobs with LLM
structure_data_with_llm()  # Reads scrape.db, writes data.db
```

### Querying Processed Data
```python
from src.data_repository import JobRepository

with JobRepository() as repo:
    # Get all processed jobs
    jobs = repo.get_all_jobs(limit=10)
    
    # Find jobs by skill
    python_jobs = repo.find_jobs_by_skill('Python')
    
    # Find jobs by location
    local_jobs = repo.find_jobs_by_location(city='Chisinau')
```
