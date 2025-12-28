# Job Market Scraper - Agent Guidelines

This document provides essential information for AI agents working in the Job Market Scraper repository.

## Project Overview

**Purpose**: A comprehensive job scraping and analysis tool for the Moldovan job market across all industries and sectors.

**Architecture**:
- **Two-stage scraping pipeline**: URL collection → Detail extraction
- **Dual database system**: Raw data (`scrape.db`) + Processed data (`data.db`)
- **LLM-powered data extraction**: Structured extraction from unstructured job descriptions
- **Scheduled execution**: Automated daily/ hourly runs with smart scheduling

## Essential Commands

### Python Execution
```bash
# Main application
python main.py

# Direct module execution (for development)
python -m src.scrape_jobs_list
python -m src.scrape_job_details
python -m src.structure_data_with_llm
```

### Development Tools
```bash
# Code formatting and linting
ruff check src/ config/  # Linting
black src/ config/       # Formatting

# Install dependencies (if needed)
uv add rich openai python-dotenv requests beautifulsoup4 aiohttp ipykernel matplotlib pandas jinja2 sqlalchemy
```

## File Structure

```
/home/catalin/dev/job-market/
├── src/                          # Core source code
│   ├── scrape_jobs_list.py      # Stage 1: URL collection with smart termination
│   ├── scrape_job_details.py    # Stage 2: Detail extraction
│   ├── scrape_job_recheck.py    # Stage 3: Alive job verification
│   ├── structure_data_with_llm.py # LLM processing pipeline
│   ├── generate_html_page.py    # HTML report generation
│   ├── scrape_database.py       # Raw data database models
│   ├── data_database.py         # Processed data database models
│   ├── job_identification.py    # Job matching and resurrection logic
│   ├── repository.py           # Database operations
│   ├── rich_logger.py          # Rich terminal logging
│   └── ... (other modules)
├── config/
│   ├── settings.py             # Main configuration (API keys, paths, thresholds)
│   └── scraper_rules.json      # Site-specific scraping rules
├── databases/                  # SQLite databases (created at runtime)
│   ├── scrape.db              # Raw scraped data
│   └── data.db                # LLM-processed structured data
├── main.py                     # Main CLI application with menu system
└── pyproject.toml             # Python project configuration
```

## Key Configuration Points

### Critical Settings (config/settings.py)
- **LLM API**: `llm_api_key`, `llm_api`, `llm_model` - OpenRouter credentials
- **Database paths**: `scrape_db_path`, `data_db_path` - SQLite database locations
- **Job resurrection**: `job_resurrection_threshold_days` (default: 7) - When to treat reopened jobs as new
- **Stage 1 efficiency**: `stage1_consecutive_known_threshold` (default: 30) - Early termination threshold
- **Max pages**: `max_page` (default: 500) - Maximum pages to scrape per site
- **Crawl delays**: `default_crawl_delay`, `min_crawl_delay`, `max_crawl_delay` - Rate limiting

### Scraper Rules (config/scraper_rules.json)
Site-specific CSS selectors for:
- `pagination`: URL pattern with `{page}` placeholder
- `job-card`: Container for each job listing
- `job-url`: Link to job detail page
- `job-title`: Job title text
- `company-name`: Company name
- `page-number`: Pagination indicator for page validation
- `details`: CSS selectors for job description extraction

## Code Patterns and Conventions

### Database Access Pattern
```python
from src.scrape_database import ScrapeSessionLocal, Job
from src.data_database import DataSessionLocal, JobDetail

# Raw data (scrape.db)
with ScrapeSessionLocal() as db:
    jobs = db.query(Job).filter(Job.site == 'jobber.md').all()

# Processed data (data.db)  
with DataSessionLocal() as db:
    details = db.query(JobDetail).filter(JobDetail.site == 'jobber.md').all()
```

### Job Processing Pipeline
1. **Stage 1**: `scrape_jobs_list()` - Collect URLs with smart termination
2. **Stage 2**: `scrape_job_details()` - Extract descriptions with HTTP status tracking
3. **Stage 3**: `recheck_alive_jobs()` - Verify job status
4. **LLM Stage**: `structure_data_with_llm()` - Structured data extraction

### Error Handling Pattern
- Use try/except blocks around external requests
- Always close database sessions in finally blocks
- Log errors with context (site, job ID, error type)
- Distinguish between HTTP errors vs. parsing errors vs. database errors

### Threading Pattern
- Use `ThreadPoolExecutor` for parallel site processing
- Each thread gets its own database session
- Use `threading.Lock` for shared resources
- Implement progress tracking with `print_threaded()` for organized output

## Testing Approach

### Unit Testing
- Test individual functions in isolation
- Mock external dependencies (requests, database)
- Test edge cases (empty responses, malformed HTML, API failures)

### Integration Testing
- Test full scraping pipeline with real sites
- Verify database consistency and relationships
- Test LLM processing with sample job descriptions

### Manual Testing Commands
```bash
# Test single site scraping
python -c "from src.scrape_jobs_list import scrape_jobs_list; scrape_jobs_list(full_scrape=False)"

# Test LLM processing
python -c "from src.structure_data_with_llm import structure_data_with_llm; structure_data_with_llm()"

# Test database operations
python -c "from src.scrape_database import ScrapeSessionLocal, Job; db = ScrapeSessionLocal(); print(db.query(Job).count()); db.close()"
```

## Important Gotchas and Non-Obvious Patterns

### Job Identification Logic
```python
# Jobs are identified by (site, title, company) combination
# NOT by URL alone - same job can have different URLs over time
from src.job_identification import should_create_new_job

should_create, existing_job = should_create_new_job(db, site, title, company)
```

### Smart Termination in Stage 1
- Stops when finding 30+ consecutive existing jobs (configurable)
- Prevents infinite loops by detecting duplicate pages
- Tracks site statistics for optimization

### LLM Error Handling
- Multiple JSON extraction strategies (direct, object extraction, array handling, markdown cleanup)
- Robust fallback for malformed LLM responses
- Detailed error logging with response content for debugging

### Database Transaction Management
- Always use context managers for database sessions
- Commit after each logical operation
- Rollback on exceptions to maintain consistency

### Rate Limiting
- Respects robots.txt crawl delays
- Configurable minimum/maximum delays
- Exponential backoff for failed requests

## Project-Specific Context

### Two-Database Architecture
- **scrape.db**: Raw scraped data, temporary storage, job status tracking
- **data.db**: Clean, normalized data with foreign key relationships
- Data flows from scrape.db → LLM processing → data.db

### Site Coverage
Currently configured for Moldovan job sites:
- jobber.md
- rabota.md  
- delucru.md

To add new sites, update `config/scraper_rules.json` with appropriate CSS selectors.

### Performance Optimization
- Multi-threaded scraping (1 thread per site)
- Parallel LLM processing (8 threads)
- Batch processing for database operations
- Smart early termination to avoid redundant work

### Data Quality Features
- Job resurrection tracking (treats re-opened positions as new after threshold)
- HTTP status tracking for job availability
- Duplicate detection and prevention
- Comprehensive error logging and retry logic

## Development Workflow

1. **Add new site**: Update `config/scraper_rules.json` with CSS selectors
2. **Test scraping**: Run Stage 1 in debug mode to verify selectors
3. **Test processing**: Run LLM stage with sample data
4. **Validate data**: Check database consistency and relationships
5. **Performance test**: Run full pipeline and monitor resource usage

## Debugging Tips

### Common Issues
- **Selector failures**: Check site structure changes, update CSS selectors
- **LLM errors**: Verify API credentials, check response formatting
- **Database errors**: Ensure proper session management, check foreign key constraints
- **Rate limiting**: Monitor HTTP 429 responses, adjust delays

### Debug Tools
- Use `DEBUG = True` in LLM processing for detailed logging
- Check `llm_errors_*.log` files for LLM processing failures
- Use `scrape.db` for debugging raw data issues
- Monitor `site_statistics` table for performance insights

### Performance Monitoring
- Track scraping times per site
- Monitor LLM processing speed and success rates
- Watch database growth and query performance
- Use the built-in progress display for real-time monitoring