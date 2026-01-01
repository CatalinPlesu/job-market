# Job Market Scraper - Moldova

A comprehensive job scraping and analysis tool for the Moldovan job market across all industries and sectors. Collects job postings from multiple job sites, processes them with LLM for structured data extraction, generates reports, and provides an interactive web interface.

## Features

- 🔍 **Job Scraping**: Automated collection from multiple job sites
- 🤖 **LLM Processing**: Structured data extraction from raw job postings
- 📊 **Analytics**: Market insights and salary analysis
- 🌐 **Web Interface**: Interactive SPA for browsing jobs and analytics
- 💾 **Data Export**: JSON API generation for static hosting
- 🔄 **Automation**: Scheduled scraping with intelligent optimization

## Quick Links

- [Frontend Documentation](frontend/README.md) - Interactive web interface
- [Deployment Guide](DEPLOYMENT.md) - Deploy to GitHub Pages, Netlify, etc.
- [Analytics Specification](ANALYTICS_SPEC.md) - Planned analytics features

## Configuration Files

**`config/settings.py`** - Hand-written user configuration
- LLM API credentials (key, endpoint, model)
- Database paths (scrape.db for raw data, data.db for processed data)
- Scraping settings (default delay, max parallel sites)
- Job identification settings (resurrection threshold for treating reopened positions as new)
- Stage 1 efficiency settings (consecutive known jobs threshold for early stopping)
- LLM prompts for data extraction

**`config/scraper_rules.json`** - Hand-written per-site rules
- CSS selectors for each site
- Pagination patterns
- Field mappings for job listings
- Currently written manually (not auto-generated)

## Database Schema

Two SQLite databases managed with SQLAlchemy:

**`databases/scrape.db`** - Raw scraped data
- `jobs` table: Original job postings (site, job_title, company_name, job_url, job_description)
- `job_checks` table: Job status tracking (check_date, http_status)
- `site_statistics` table: Scraping performance metrics per site (total_runs, total_pages, average_pages)

**`databases/data.db`** - Processed and normalized data
- `job_details` table: LLM-extracted and structured job information
- 50+ lookup tables for normalized data (titles, companies, cities, skills, etc.)
- Many-to-many relationships for skills, benefits, certifications, etc.

The schema uses full normalization with foreign keys and relationship mapping for efficient querying and data integrity.

## Menu Options

### 1. Run Scheduled Scraping (Stages 1&2 hourly, Stage 3 daily)
Execute scraping stages on optimized schedules based on their speed:
- **Stage 1 & 2: Every HOUR** (fast with early stopping at 100+ consecutive existing jobs)
  - Stage 1: Scrape job listings from all sites
  - Stage 2: Get job details for new listings
- **Stage 3: Daily at 00:00** (slow - rechecks all alive jobs)
  - Stage 3: Re-check alive jobs to detect removed postings
- Separate schedules optimize for each stage's performance characteristics
- Database backup before each run (keeps last 3 days)
- Error-only logging (weekly log files)
- Daily reports with statistics per site
- Simply select this option to start the scheduler with default settings

### 2. Scrape Job Listings (Stage 1 - Smart Mode)
Collect job URLs from listing pages with intelligent early termination:
- Navigate pagination starting from page 1
- Extract job post URLs from listing pages
- Store in `scrape.db` database
- Intelligent job identification: Jobs with same (site, title, company) are tracked
- **Job Resurrection**: If a job dies and reappears after the threshold (default 7 days), it's treated as a new position
- **Efficiency Optimization**: Automatically stops when finding 100+ consecutive jobs that already exist in the database (configurable via `stage1_consecutive_known_threshold`)
- **Duplicate Page Detection**: Stops if two consecutive pages contain identical job URLs (prevents infinite loops)
- **Page Statistics**: Tracks average pages scraped per site in the `site_statistics` table in `scrape.db`
- Maximum page limit: 500 pages (configurable via `max_page` in settings)

### 3. Scrape Job Listings (Stage 1 - Full Scrape)
Full scraping mode without early termination:
- Scrapes all available pages up to the maximum limit (500 pages)
- No early stopping based on consecutive existing jobs
- Useful for initial database population or when you want to ensure all jobs are captured
- Still includes duplicate page detection to prevent infinite loops
- Still tracks page statistics

### 4. Scrape Job Details (Stage 2)
Get detailed information for each job:
- Visit each job URL collected in Stage 1
- Extract full job description and details
- Store raw HTML/text in `scrape.db`

### 5. Re-check Alive Jobs
Verify job postings are still active:
- Check HTTP status of previously scraped jobs
- Track check date and status in `job_checks` table
- Identify jobs that have been removed or expired

### 6. Re-check All (Including Rotten) Jobs
Re-check all jobs including those previously marked as inactive

### 7. Structure Data with LLM
Process raw job descriptions with LLM:
- Send job descriptions to LLM with extraction prompt
- Parse structured JSON response
- Store normalized data in `data.db` with proper relationships

### 8. Process Data
Additional data processing and normalization tasks (placeholder - not yet implemented)

### 9. Generate HTML Page
Create static HTML report with job listings and statistics (placeholder - not yet implemented)

### 10. Database Rollback
Restore databases from previous backups:
- Select which database to restore (scrape.db or data.db)
- View available backups with timestamps and sizes
- Restore database to a previous state
- Useful for recovering from errors or testing

## Tech Stack

### Backend
- **HTTP:** `requests`, `aiohttp`
- **HTML parsing:** `BeautifulSoup4`
- **Database:** SQLite with `SQLAlchemy` ORM
- **LLM Integration:** `openai` (OpenRouter API)
- **Data Analysis:** `pandas`, `matplotlib`
- **UI:** `rich` (terminal UI components)

### Frontend (SPA)
- **Framework:** Mithril.js (via CDN)
- **UI:** DaisyUI + Tailwind CSS (via CDN)
- **Charts:** Chart.js (via CDN)
- **Routing:** Client-side hash routing
- **Architecture:** Static SPA with JSON API

## Current Features

- **Two-stage scraping**: Separate collection of URLs and detail scraping
- **Dual database architecture**: Raw data (`scrape.db`) and processed data (`data.db`)
- **LLM-powered data extraction**: Structured extraction from unstructured job descriptions
- **Intelligent job identification**: Jobs are identified by (site, title, company) with resurrection logic
  - Tracks multiple postings of the same position over time
  - Configurable threshold (default 7 days) to treat reopened positions as new
  - Maintains backward compatibility with existing databases
- **Job status tracking**: Monitor when jobs become inactive
- **Scheduled execution**: Built-in scheduler for automated daily runs
- **Database backups**: Automatic backups with retention policy
- **Comprehensive data model**: 50+ normalized tables with proper relationships
- **Scraping reports**: Daily JSON/text reports with per-site and aggregated statistics
- **JSON API Generation**: Export paginated job data as JSON for static hosting (GitHub Pages)
  - Generates paginated job listings (page-1.json, page-2.json, etc.)
  - Creates comprehensive index.json with metadata for ALL 50+ filterable fields
  - Includes per-page item counts for efficient filtering
  - Sanitizes sensitive data (removes contact information)
  - Command: `python -m json_generator --output pages/api`
- **Interactive Web Interface**: Modern SPA for job browsing and analytics
  - Extra slim job listings (Hacker News style)
  - Client-side filtering on multiple fields with hierarchical filtering
  - Job detail view with parsed/raw tabs
  - Analysis dashboard with charts
  - Dark/light theme toggle
  - Mobile responsive design
  - See [frontend/README.md](frontend/README.md) for details
  - See [json_generator/README.md](json_generator/README.md) for details

## Planned Features

See [ANALYTICS_SPEC.md](ANALYTICS_SPEC.md) for detailed specifications of planned analytics and reporting features.
