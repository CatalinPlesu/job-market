# GitHub Issue Templates for Parallel Development

## Overview
These issue specifications enable independent, parallel development of the GitHub Pages & Pseudo API system. Each issue is self-contained with clear boundaries, minimal dependencies, and defined integration points.

---

## Issue 1: JSON Generation System

### Title
Implement JSON API Generation from Database

### Labels
`enhancement`, `json-api`, `backend`

### Description

#### Objective
Build a system that exports job market data from SQLite databases to paginated JSON files, creating a pseudo-API for static hosting on GitHub Pages.

#### Scope
- Query data from `scrape.db` and `data.db`
- Generate paginated job listings as JSON files
- Create intelligent index.json with metadata for filtering
- Sanitize data (remove contact information)
- Support company opt-out blacklist

#### Context
This system transforms our private databases into a public-facing API. The job market scraper collects data into two SQLite databases:
- **scrape.db**: Raw scraped jobs (Job, JobCheck tables)
- **data.db**: LLM-processed structured data (JobDetail + 50+ lookup tables)

**Database schemas:** Explore `src/scrape_database.py` and `src/data_database.py` for table structure.

**Configuration:** Database paths are in `config/settings.py`.

#### Input Requirements
- Access to SQLite databases (scrape.db, data.db)
- Configuration for pagination size (default: 100 jobs/page)
- Company blacklist file (optional)

#### Output Definition

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
- `/api/jobs/index.json` contains metadata showing which pages have jobs matching specific filters
- Each page JSON contains 100 jobs (configurable)
- No contact emails, phones, or person names in output
- Company names anonymized if on blacklist

#### Independence
- Can develop with local copy of databases
- No dependency on frontend (use mock JSON for testing)
- No dependency on deployment (generate to local directory)
- Analysis system is separate (different issue)

#### Integration Points

**Input:** Database files
- Use SQLAlchemy models from existing codebase
- Query both databases (can join via job_url field)

**Output:** JSON files in `pages/api/` directory
- Must follow schemas defined in specification
- Include version field for future compatibility

**Called by:** Deployment pipeline (GitHub Actions)
- Entry point: `python -m json_generator --output pages/api`
- Exit code: 0 for success, non-zero for errors

#### Success Criteria
- [ ] Generates valid JSON according to schemas
- [ ] All jobs appear exactly once across pages
- [ ] Index metadata accurately maps filters to pages
- [ ] No sensitive data (emails, phones) in output
- [ ] Generation completes in <30 seconds for 10,000 jobs
- [ ] Total API size <20MB
- [ ] Handles missing data gracefully (null values)
- [ ] Unit tests with 80%+ coverage

#### What This Does NOT Depend On
- Frontend SPA implementation
- Deployment automation
- Analysis system
- GitHub Pages configuration

#### References
- **Specification:** `planning/github-pages-pseudo-api/02-json-api-generation.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **Database models:** `src/scrape_database.py`, `src/data_database.py`

#### Implementation Hints
1. Start with basic pagination (all jobs, no filtering)
2. Add index.json generation with metadata
3. Implement data sanitization
4. Add tests for edge cases (missing data, large datasets)
5. Optimize for performance

---

## Issue 2: Analysis Engine Implementation

### Title
Implement Job Market Analysis System with Temporal Support

### Labels
`enhancement`, `analytics`, `backend`

### Description

#### Objective
Build an analysis engine that computes ~20 meaningful statistics and trends from job market data, supporting both static snapshots and time-series analysis.

#### Scope
- Compute static analyses (current market snapshot)
- Generate temporal analyses (trends over time)
- Support dynamic hierarchy analysis (job_function → specialization → seniority)
- Handle missing data gracefully
- Export results as JSON files

#### Context
The analysis system processes data from `data.db` to generate insights for job seekers. It must support:
- **Static analyses:** Current market state (salary distributions, skill demand, etc.)
- **Temporal analyses:** How metrics evolve over time (salary trends, posting volume, etc.)
- **Hierarchy analyses:** Drill-down from job functions to specializations to seniority levels

**Database timestamps:**
- `jobs.created_at` - When job first scraped
- `job_checks.check_date` + `http_status` - When jobs closed
- `job_details.posting_date` - Original posting date

**Existing spec:** See `ANALYTICS_SPEC.md` for analytics requirements.

#### Input Requirements
- Access to `data.db` (JobDetail + lookup tables)
- Access to `scrape.db` (Job + JobCheck for temporal data)
- Configuration for analysis parameters (min sample size, granularity, etc.)

#### Output Definition

**File Structure:**
```
pages/api/analysis/
├── index.json                   # List of available analyses
├── salary-overview.json         # Static: Overall salary stats
├── salary-by-function.json      # Static: By job function
├── salary-trends.json           # Temporal: Salary over time
├── posting-trends.json          # Temporal: Job volume trends
├── skills-demand.json           # Static: Top skills
├── skills-trends.json           # Temporal: Skill popularity over time
└── ... (15+ more analyses)
```

**JSON Schemas:** See `planning/github-pages-pseudo-api/05-analysis-system.md` for detailed schemas.

**Required Analyses (~20):**
1. Salary overview (overall stats)
2. Salary by job function
3. Salary by seniority level
4. Salary by location
5. Salary by company size
6. Salary by education
7. Top in-demand skills
8. Skills to salary correlation
9. Skill combinations
10. Employment types distribution
11. Remote work availability
12. Benefits analysis
13. Job requirements overview
14. Top hiring companies
15. Job posting volume trends (temporal)
16. Salary evolution over time (temporal)
17. Skills demand trends (temporal)
18. Remote work adoption trends (temporal)
19. Job duration analysis (time to fill)
20. Market health indicators (temporal)
21. Salary by hierarchy (dynamic drill-down)

#### Independence
- Can develop with local database
- No dependency on frontend (JSON consumed by separate component)
- No dependency on job list generation (separate JSON files)
- No dependency on deployment (generate to local directory)

#### Integration Points

**Input:** Database files
- Use SQLAlchemy models from existing codebase
- Query both scrape.db and data.db

**Output:** JSON files in `pages/api/analysis/` directory
- Must follow schemas defined in specification
- Include visualization hints for frontend

**Called by:** JSON generator or deployment pipeline
- Entry point: `python -m analysis_engine --output pages/api/analysis`
- Exit code: 0 for success, non-zero for errors

#### Success Criteria
- [ ] All 20+ analyses implemented
- [ ] Each analysis produces valid JSON
- [ ] Temporal analyses include time series data
- [ ] Hierarchy analysis supports drill-down
- [ ] Handle missing data gracefully (no crashes)
- [ ] Generation completes in <5 minutes for 10,000 jobs
- [ ] Outlier detection prevents skewed results
- [ ] Test coverage >80%

#### What This Does NOT Depend On
- Frontend visualization implementation
- Job list JSON generation
- Deployment automation
- GitHub Pages configuration

#### References
- **Specification:** `planning/github-pages-pseudo-api/05-analysis-system.md`
- **Requirements:** `ANALYTICS_SPEC.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **Database models:** `src/scrape_database.py`, `src/data_database.py`

#### Implementation Hints
1. Start with base analysis class and one simple analysis (salary overview)
2. Add temporal analysis infrastructure
3. Implement hierarchy analysis framework
4. Add remaining analyses incrementally
5. Test with various data sizes and edge cases

---

## Issue 3: Frontend SPA Implementation

### Title
Build React SPA for Job Market Browsing and Analysis Visualization

### Labels
`enhancement`, `frontend`, `react`

### Description

#### Objective
Create a single-page application (SPA) that consumes JSON API files to provide an interactive interface for browsing jobs and viewing market analytics.

#### Scope
- Job browsing with pagination
- Client-side filtering (function, location, salary, etc.)
- Job detail view with parsed/raw tabs
- Analysis dashboard with interactive charts
- Mobile-responsive design
- Routing and navigation

#### Context
This SPA will be hosted on GitHub Pages and consume static JSON files as a pseudo-API. It should work entirely client-side with no backend.

**Key Features:**
- Smart pagination: Use index.json metadata to load only relevant pages when filtering
- Two-tab job view: Parsed (structured LLM data) vs Raw (original posting)
- Interactive charts: Line charts for trends, bar charts for comparisons, tables for details

**JSON API contracts:** See `planning/github-pages-pseudo-api/02-json-api-generation.md` and `05-analysis-system.md`.

#### Input Requirements
- Mock JSON files for development (or wait for JSON generator)
- API endpoints structure:
  - `/api/jobs/index.json` - Job metadata
  - `/api/jobs/page-{N}.json` - Paginated jobs
  - `/api/analysis/index.json` - Analysis metadata
  - `/api/analysis/{analysis-id}.json` - Individual analyses

#### Output Definition

**Build Output:**
```
frontend/dist/
├── index.html
├── assets/
│   ├── index-abc123.js
│   ├── index-def456.css
│   └── ...
└── ...
```

**Pages/Routes:**
- `/` - Home page (overview)
- `/jobs` - Job list with filters
- `/jobs/:id` - Job detail (parsed/raw tabs)
- `/analysis` - Analysis dashboard

**Technology Stack:**
- React 18+ with TypeScript
- Vite for build
- React Router for routing
- TanStack Query for data fetching
- Recharts/Chart.js for visualizations
- Tailwind CSS for styling

#### Independence
- Can develop with mock JSON files
- No dependency on JSON generation (use sample data)
- No dependency on deployment (test locally with `npm run dev`)
- No dependency on analysis system (mock analysis data)

#### Integration Points

**Input:** JSON API files
- Fetch from `/api/` paths
- Type safety via TypeScript interfaces
- Error handling for missing data

**Output:** Static build artifacts
- Build command: `npm run build`
- Output: `frontend/dist/` directory
- Ready for GitHub Pages deployment

**Called by:** Deployment pipeline
- Build step in GitHub Actions
- Copy `dist/` contents to gh-pages root

#### Success Criteria
- [ ] Initial page load <2 seconds
- [ ] Filtering updates <100ms
- [ ] All routes work correctly
- [ ] Mobile responsive (tested on phones/tablets)
- [ ] Charts render without errors
- [ ] No accessibility violations (WCAG AA)
- [ ] Works in Chrome, Firefox, Safari, Edge
- [ ] Filtering correctly loads only relevant pages
- [ ] Job detail view shows both tabs
- [ ] Analysis visualizations are interactive

#### What This Does NOT Depend On
- JSON generation implementation (use mock data)
- Analysis system implementation (use mock data)
- Deployment automation (test locally)
- Real database access

#### References
- **Specification:** `planning/github-pages-pseudo-api/03-spa-frontend-structure.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **JSON schemas:** `02-json-api-generation.md`, `05-analysis-system.md`
- **Analytics requirements:** `ANALYTICS_SPEC.md`

#### Implementation Hints
1. Scaffold React app with Vite
2. Set up routing and basic layout
3. Implement job browsing with mock data
4. Add filtering logic
5. Implement job detail view
6. Add analysis dashboard with one chart type
7. Expand to all analysis types
8. Polish UI and add responsiveness

---

## Issue 4: Deployment Pipeline Automation

### Title
Implement GitHub Actions Workflow for Automated Deployment

### Labels
`enhancement`, `devops`, `github-actions`

### Description

#### Objective
Create an automated deployment pipeline that generates fresh JSON files, builds the SPA, and deploys to GitHub Pages daily.

#### Scope
- GitHub Actions workflow for daily deployment
- JSON generation step
- Frontend build step
- File preservation (keep .git, CNAME, etc.)
- Deployment to gh-pages branch
- Error handling and rollback
- Verification and monitoring

#### Context
The deployment pipeline orchestrates the entire system, running daily after the scraper completes. It must:
1. Generate JSON API files from fresh databases
2. Build static SPA assets
3. Deploy to GitHub Pages without downtime
4. Preserve critical files (.git, CNAME)

**Deployment target:** `gh-pages` branch on `CatalinPlesu/job-market` repo.

#### Input Requirements
- JSON generator implementation (Issue #1)
- Frontend build setup (Issue #3)
- Access to repository databases
- GitHub Actions runner environment

#### Output Definition

**Workflow File:**
`.github/workflows/deploy-pages.yml`

**Deployment Schedule:**
- Daily at 00:30 UTC (after scraper completes)
- Manual trigger via `workflow_dispatch`

**gh-pages Branch Structure:**
```
/
├── index.html              # SPA entry
├── assets/                 # JS, CSS
├── api/                    # JSON files
│   ├── jobs/
│   └── analysis/
├── .nojekyll              # Disable Jekyll
└── CNAME                   # Custom domain (if configured)
```

#### Independence
- Requires JSON generator and frontend to be implemented
- Can test workflow with mock implementations
- Can use staging branch for testing before production

#### Integration Points

**Calls:** JSON generator
- Command: `python -m json_generator --output pages/api`
- Exit code check for success/failure

**Calls:** Frontend build
- Command: `cd frontend && npm run build`
- Output: `frontend/dist/`

**Deploys to:** GitHub Pages
- Method: Force push to gh-pages branch
- Preservation: Keep .git, CNAME, .nojekyll

#### Success Criteria
- [ ] Deployment completes in <10 minutes
- [ ] Zero downtime during deployment
- [ ] All files preserved correctly
- [ ] Site accessible immediately after deployment
- [ ] API endpoints return valid JSON
- [ ] Rollback works if deployment fails
- [ ] Deployment logs captured
- [ ] Can trigger manually via workflow_dispatch
- [ ] Scheduled deployments run reliably

#### What This Does NOT Depend On
- Specific implementation details of JSON generator or frontend
- Just needs working entry points and expected outputs

#### References
- **Specification:** `planning/github-pages-pseudo-api/04-deployment-automation.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **JSON generator interface:** Issue #1
- **Frontend build interface:** Issue #3

#### Implementation Hints
1. Start with basic workflow (checkout, setup Python/Node)
2. Add JSON generation step
3. Add frontend build step
4. Implement file preservation logic
5. Add deployment to gh-pages
6. Add error handling and verification
7. Test with manual trigger first
8. Enable scheduled runs

---

## Coordination Guidelines

### Parallel Development
These issues can be worked on simultaneously:
- **Issue #1 & #2** can work in parallel (separate output directories)
- **Issue #3** can start immediately with mock JSON data
- **Issue #4** can be developed with placeholders for #1-3, testing integration as they complete

### Integration Testing
Once individual issues are complete:
1. Test JSON generation → Frontend consumption
2. Test Analysis generation → Frontend visualization
3. Test full deployment pipeline end-to-end

### Communication
- Document any changes to JSON schemas (affects integration)
- Share sample JSON files for frontend development
- Coordinate on repository structure (avoid path conflicts)

### Testing Strategy
- Each issue has its own unit tests
- Integration tests added after components are complete
- End-to-end test in staging before production

---

## Notes for AI Agents

**Exploration:**
- Read the referenced specification documents
- Explore database schemas in the codebase
- Check existing configuration files
- Don't hardcode paths - use config variables

**Independence:**
- Work can proceed without other issues being complete
- Use mock data or placeholders where needed
- Focus on your component's contract fulfillment

**Integration:**
- Follow the defined JSON schemas strictly
- Use the specified entry points (CLI commands)
- Document any deviations from specifications

**Success:**
- Complete all success criteria
- Write tests (80%+ coverage)
- Document your implementation
- Coordinate for integration testing
