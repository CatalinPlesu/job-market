# Issue 2: Analysis Engine Implementation

## Title
Implement Job Market Analysis System with Temporal Support

## Labels
`enhancement`, `analytics`, `backend`

## Description

### Objective
Build an analysis engine that computes ~20 meaningful statistics and trends from job market data, supporting both static snapshots and time-series analysis.

### Scope
- Compute static analyses (current market snapshot)
- Generate temporal analyses (trends over time)
- Support dynamic hierarchy analysis (job_function → specialization → seniority)
- Handle missing data gracefully
- Export results as JSON files

### Context
The analysis system processes data from `data.db` to generate insights for job seekers. It must support:
- **Static analyses:** Current market state (salary distributions, skill demand, etc.)
- **Temporal analyses:** How metrics evolve over time (salary trends, posting volume, etc.)
- **Hierarchy analyses:** Drill-down from job functions to specializations to seniority levels

**Database timestamps:**
- `jobs.created_at` - When job first scraped
- `job_checks.check_date` + `http_status` - When jobs closed
- `job_details.posting_date` - Original posting date

**Existing spec:** See `ANALYTICS_SPEC.md` for analytics requirements.

### Input Requirements
- Access to `data.db` (JobDetail + lookup tables)
- Access to `scrape.db` (Job + JobCheck for temporal data)
- Configuration for analysis parameters (min sample size, granularity, etc.)

### Output Definition

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

### Independence
- Can develop with local database
- No dependency on frontend (JSON consumed by separate component)
- No dependency on job list generation (separate JSON files)
- No dependency on deployment (generate to local directory)

### Integration Points

**Input:** Database files
- Use SQLAlchemy models from existing codebase
- Query both scrape.db and data.db

**Output:** JSON files in `pages/api/analysis/` directory
- Must follow schemas defined in specification
- Include visualization hints for frontend

**Called by:** JSON generator or deployment pipeline
- Entry point: `python -m analysis_engine --output pages/api/analysis`
- Exit code: 0 for success, non-zero for errors

### Success Criteria
- [ ] All 20+ analyses implemented
- [ ] Each analysis produces valid JSON
- [ ] Temporal analyses include time series data
- [ ] Hierarchy analysis supports drill-down
- [ ] Handle missing data gracefully (no crashes)
- [ ] Generation completes in <5 minutes for 10,000 jobs
- [ ] Outlier detection prevents skewed results
- [ ] Test coverage >80%

### What This Does NOT Depend On
- Frontend visualization implementation
- Job list JSON generation
- Deployment automation
- GitHub Pages configuration

### References
- **Specification:** `planning/github-pages-pseudo-api/05-analysis-system.md`
- **Requirements:** `ANALYTICS_SPEC.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **Database models:** `src/scrape_database.py`, `src/data_database.py`

### Implementation Hints
1. Start with base analysis class and one simple analysis (salary overview)
2. Add temporal analysis infrastructure
3. Implement hierarchy analysis framework
4. Add remaining analyses incrementally
5. Test with various data sizes and edge cases
