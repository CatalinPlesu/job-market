# Job Market Scraper - Moldova

A comprehensive job scraping and analysis tool for the Moldovan job market across all industries and sectors. Collects job postings from multiple job sites, processes them with LLM for structured data extraction, generates reports, and provides an interactive web interface.

## Features

- 🔍 **Job Scraping**: Automated collection from multiple job sites
- 🤖 **LLM Processing**: Structured data extraction from raw job postings
- 📊 **Analytics**: Market insights and salary analysis
- 🌐 **Web Interface**: Interactive SPA for browsing jobs and analytics
- 💾 **Database Copy**: Copy SQLite databases to frontend/api directory
- 🔄 **Automation**: Scheduled scraping with intelligent optimization
- 🚀 **Auto-Deploy**: Automatic git push to frontend repository (e.g., GitHub Pages) after daily scraping

## Quick Links

- [Frontend Documentation](frontend/README.md) - Interactive web interface
- [Deployment Guide](DEPLOYMENT.md) - Deploy to GitHub Pages, Netlify, etc.
- [Analytics Specification](ANALYTICS_SPEC.md) - Planned analytics features

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or with uv
   uv pip install -e .
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Required configuration:**
   - `ENDPOINT`: LLM API endpoint
   - `LLM_API_KEY`: Your LLM API key
   - `MODEL`: LLM model name
   
4. **Optional - Automated frontend deployment:**
   - **Install Git LFS** (required for large database files):
     - Ubuntu/Debian: `sudo apt-get install git-lfs`
     - macOS: `brew install git-lfs`
   - `FRONTEND_GIT_REMOTE_URL`: Your frontend git repository URL (e.g., `https://github.com/user/frontend.git`)
   - `FRONTEND_GIT_BRANCH`: Branch to push to (default: `main`)
   - `FRONTEND_GIT_FRESH_APPROACH`: Use fresh repo approach (default: `true`)
   - Database files in `frontend/api/` are automatically tracked with Git LFS

5. **Run the application:**
   ```bash
   python main.py
   ```

## Configuration Files

**`.env`** - Environment variables (create from `.env.example`)
- LLM API credentials (ENDPOINT, LLM_API_KEY, MODEL)
- Frontend git operations (FRONTEND_GIT_REMOTE_URL, FRONTEND_GIT_BRANCH, FRONTEND_GIT_FRESH_APPROACH)

**`config/settings.py`** - Hand-written user configuration
- LLM API credentials (key, endpoint, model)
- Database paths (scrape.db for raw data, data.db for processed data)
- Scraping settings (default delay, max parallel sites)
- Job identification settings (resurrection threshold for treating reopened positions as new)
- Stage 1 efficiency settings (consecutive known jobs threshold for early stopping)
- Frontend git settings (remote URL, branch, fresh approach)
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
  - **After Stage 3**: Automatically copies databases to frontend/api and pushes to git (if configured)
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

### 8. Copy Database Files to Frontend API
Copy both SQLite database files to frontend/api directory:
- Automatically copies scrape.db and data.db to frontend/api
- Creates frontend/api directory if it doesn't exist
- Useful for making databases accessible to the frontend
- Shows file sizes during copy operation

### 9. Push Frontend to Git (Copy DBs + Commit + Push)
Copy databases to frontend and push to git repository (e.g., GitHub Pages):
- Copies both databases to frontend/api directory
- Initializes/updates git repository in frontend directory
- Commits and pushes changes to remote repository
- **Configuration required**: Set `FRONTEND_GIT_REMOTE_URL` in environment
- **Two approaches**:
  - **Fresh (default)**: Removes .git history and force pushes (keeps repo size small)
  - **Incremental**: Preserves git history with regular commits
- Interactive prompt for remote URL if not configured
- **Automated deployment**: Stage 3 (daily at 00:00) automatically runs this after completion

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
- **Architecture:** Static SPA with SQLite database access

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
- **Database Copy**: Copy SQLite database files to frontend/api directory via menu
  - Automatically copies both scrape.db and data.db to frontend/api
  - Creates destination directory if needed
  - Shows file sizes during copy operation
- **Interactive Web Interface**: Modern SPA for job browsing and analytics
  - Extra slim job listings (Hacker News style)
  - Client-side filtering on multiple fields with hierarchical filtering
  - Job detail view with parsed/raw tabs
  - **Custom Analysis Builder**: SQL.js + Chart.js for custom data analysis
    - 15+ predefined analysis queries (skills, salary, trends, etc.)
    - Custom SQL query builder with live visualization
    - Multiple chart types (bar, line, doughnut, pie)
    - Save queries to browser localStorage
    - Database structure documentation for users
  - Dark/light theme toggle
  - Mobile responsive design
  - See [frontend/README.md](frontend/README.md) for details

## Planned Features

See [ANALYTICS_SPEC.md](ANALYTICS_SPEC.md) for detailed specifications of planned analytics and reporting features.
