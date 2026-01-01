# Overall Architecture & Strategy

## Document Purpose
This document defines the high-level system design for transforming the job market scraper into a public-facing GitHub Pages site with a pseudo-API architecture. It establishes the foundation for parallel development of independent components.

## System Overview

### Big Picture Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      Current System (Private)                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ Scrapers │──▶│ scrape.db│──▶│   LLM    │──▶│ data.db  │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   JSON Generation System                        │
│  - Query data.db + scrape.db                                    │
│  - Generate paginated JSON files                                │
│  - Create index.json with metadata                              │
│  - Compute analysis statistics                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Deployment Pipeline (GitHub Actions)               │
│  - Generate fresh JSON files                                    │
│  - Clean pages folder (preserve .git)                           │
│  - Copy static SPA assets                                       │
│  - Force push to gh-pages branch                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Pages (Public)                        │
│  ┌─────────────────────┐       ┌────────────────────────┐      │
│  │   Static SPA        │◀─────▶│  JSON API Files        │      │
│  │   (React/Vue/etc)   │       │  /jobs/index.json      │      │
│  │                     │       │  /jobs/page-1.json     │      │
│  │  - Job browsing     │       │  /analysis/index.json  │      │
│  │  - Filtering        │       │  /analysis/salaries... │      │
│  │  - Visualizations   │       │  ...                   │      │
│  └─────────────────────┘       └────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Static-First Architecture
- **No backend server required** - Everything served as static files
- **No API keys exposed** - All data pre-computed and embedded
- **Fast loading** - CDN-friendly, cacheable resources
- **Zero maintenance cost** - GitHub Pages hosting is free

### 2. Data Privacy & Security
- **No sensitive data** - Filter out contact emails, phones, names from public JSON
- **Aggregation only** - No individual job details exposed unless in aggregate views
- **Company respect** - Allow opt-out mechanism for company-specific data

### 3. Performance Optimization
- **Lazy loading** - Load only what's needed when needed
- **Smart pagination** - Jump to any page without loading intermediates
- **Efficient filtering** - Rich index.json enables client-side filtering without loading all data
- **Compressed assets** - Minified JS/CSS, gzipped JSON where beneficial

### 4. Maintainability
- **Decoupled components** - Each system can be developed/tested independently
- **Clear contracts** - Well-defined JSON schemas for all APIs
- **Version control** - Tag releases for rollback capability
- **Automated testing** - Validate JSON structure before deployment

## Technology Selection

### Frontend SPA Framework

**Recommended: React**
- **Rationale:**
  - Industry standard with massive ecosystem
  - Excellent AI/LLM code generation support
  - Rich charting libraries (Recharts, Victory, Nivo)
  - Strong TypeScript support for type safety
  - Great developer experience with Create React App / Vite

**Alternative: Vue.js**
- Simpler learning curve
- Good AI code generation support
- Lighter weight
- Less verbose than React

**Alternative: Svelte**
- Smallest bundle size
- Excellent performance
- Compiles to vanilla JS
- Less mature AI code generation

**Decision factors:**
- AI agent familiarity with codebase patterns
- Availability of visualization libraries
- Bundle size requirements
- Team/contributor experience

### Charting & Visualization

**Recommended Stack:**
- **Recharts** (React) - Simple, declarative charts
- **Chart.js** - Framework-agnostic, lightweight
- **D3.js** - Complex custom visualizations (maps, network graphs)
- **DataTables** or **TanStack Table** - Interactive data tables

### Build & Deployment

**Build Tool: Vite**
- Fast development server
- Efficient bundling
- Modern defaults

**CI/CD: GitHub Actions**
- Native GitHub integration
- Free for public repos
- Can trigger on schedule or manual dispatch

## Component Interaction

### JSON Generation ↔ Databases
- **Input:** SQLite databases (scrape.db, data.db)
- **Process:** Query, transform, paginate
- **Output:** Structured JSON files
- **Independence:** Can run standalone with just database access

### Deployment Pipeline ↔ JSON Generation
- **Input:** Fresh databases
- **Process:** Trigger JSON generation, copy static assets, deploy
- **Output:** Updated GitHub Pages site
- **Independence:** Can be triggered manually or on schedule

### SPA Frontend ↔ JSON API
- **Input:** JSON files via HTTP fetch
- **Process:** Parse, filter, render, visualize
- **Output:** Interactive user interface
- **Independence:** Can be developed with mock JSON data

### Analysis Engine ↔ Databases
- **Input:** data.db with job_details and lookup tables
- **Process:** Aggregate, compute statistics, generate time series
- **Output:** Analysis JSON files
- **Independence:** Can be tested with sample databases

## Subrepository Decoupling Strategy

### Phase 1: Monorepo with Clear Separation
```
job-market/
├── src/                    # Existing scraper code
├── planning/               # This planning folder
├── json-generator/         # New: JSON API generation
├── frontend/               # New: SPA application
└── .github/workflows/      # New: Deployment automation
```

### Phase 2: Separate Repository (Future)
```
job-market/              # Private: Scrapers + databases
job-market-frontend/     # Public: SPA + JSON generation for Pages

# Deployment flow:
# 1. job-market generates fresh databases
# 2. Trigger webhook to job-market-frontend
# 3. job-market-frontend pulls databases, generates JSON, deploys
```

**Migration path:**
- Start with monorepo for simplicity
- Use clear directory boundaries
- Minimize cross-dependencies
- When ready, split using git subtree or submodule

## Integration Points

### 1. Database Schema Contract
- **Owner:** Existing scraper system
- **Consumers:** JSON generator, analysis engine
- **Contract:** SQLAlchemy models in `src/scrape_database.py` and `src/data_database.py`
- **Stability:** Schema should be stable; additions are safe, removals require coordination

### 2. JSON API Schema
- **Owner:** JSON generator
- **Consumers:** SPA frontend
- **Contract:** JSON schemas defined in JSON generation spec
- **Versioning:** Include version field in all JSON responses for future compatibility

### 3. Static Asset Paths
- **Owner:** SPA frontend build process
- **Consumers:** Deployment pipeline
- **Contract:** All built assets in `frontend/dist/` or `frontend/build/`
- **Stability:** Output directory is configurable but should remain consistent

### 4. GitHub Pages Deployment
- **Owner:** Deployment pipeline
- **Consumers:** End users via web browsers
- **Contract:** 
  - Static files in root of gh-pages branch
  - API files in `/api/` subdirectory
  - SPA entry point at `/index.html`
  - 404 handling via `/404.html` for SPA routing

## Data Flow & Timing

### Generation Schedule
```
Daily at 00:00 (after scraper Stage 3):
├─ 1. Database backup
├─ 2. Generate JSON API files (10-30 seconds)
├─ 3. Run analysis computations (1-5 minutes)
├─ 4. Copy static SPA assets (5 seconds)
├─ 5. Commit and force push to gh-pages (10 seconds)
└─ 6. GitHub Pages deployment (1-2 minutes)

Total: ~5-10 minutes from data update to live site
```

### Data Freshness
- **Job listings:** Updated daily
- **Analysis trends:** Recomputed daily with new data points
- **Time series:** Historical data preserved, new points appended
- **User experience:** Banner showing "Last updated: YYYY-MM-DD HH:MM UTC"

## Scalability Considerations

### Current Scale (Estimate)
- ~5,000-10,000 jobs total
- ~500-1,000 new jobs per day
- ~50-100 companies
- ~20-30 job functions

### JSON Size Management
- **Pagination:** 50-100 jobs per page → 50-200 pages
- **Index file:** ~100-500KB with rich metadata
- **Analysis files:** ~50-200KB per analysis category
- **Total API size:** ~5-20MB for all JSON files

### Performance Targets
- **Initial page load:** <2 seconds
- **Page navigation:** <500ms
- **Filter application:** <100ms (client-side)
- **Chart rendering:** <1 second

## Security & Privacy

### Data Sanitization Rules
1. **Remove all contact information** from public JSON:
   - Email addresses
   - Phone numbers
   - Contact person names
   
2. **Aggregate small populations:**
   - If category has <10 jobs, group into "Other" or hide
   - Prevents identification of specific companies/roles

3. **Company opt-out:**
   - Maintain blacklist of companies requesting removal
   - Filter during JSON generation

4. **Rate limiting:**
   - GitHub Pages has no server-side rate limiting
   - Consider: Client-side usage patterns, CDN caching

### Compliance Considerations
- **GDPR:** Publicly posted job ads are public data; no PII collected from users
- **Copyright:** Link to original job postings; don't reproduce full text
- **robots.txt:** Allow search engine indexing for job discovery

## Development Workflow

### Phase 1: JSON Generation (Week 1-2)
- Develop JSON generator standalone
- Test with local databases
- Validate JSON schemas
- Document API contract

### Phase 2: Frontend SPA (Week 2-4)
- Scaffold React application
- Implement job browsing with mock data
- Develop filtering and search
- Integrate charting libraries
- Test with real JSON from Phase 1

### Phase 3: Analysis Engine (Week 2-4, parallel)
- Design time-series data structures
- Implement static analytics
- Implement temporal analytics
- Generate analysis JSON
- Validate with sample data

### Phase 4: Deployment Pipeline (Week 4-5)
- Create GitHub Actions workflow
- Implement file preservation logic
- Test deployment to staging branch
- Configure GitHub Pages
- End-to-end testing

### Phase 5: Integration & Testing (Week 5-6)
- Connect all components
- Performance testing
- Security review
- User acceptance testing
- Documentation

## Success Criteria

### Technical Success
- [ ] JSON API loads in <500ms on average
- [ ] SPA renders initial view in <2 seconds
- [ ] All charts render without errors
- [ ] Filtering works with datasets up to 50,000 jobs
- [ ] Deployment completes in <10 minutes
- [ ] Zero downtime during deployments

### Functional Success
- [ ] Users can browse all jobs with pagination
- [ ] Filtering by salary, location, function works
- [ ] Analysis visualizations render correctly
- [ ] Time series trends show historical data
- [ ] Mobile responsive (works on phones/tablets)
- [ ] No sensitive data exposed in JSON

### Development Success
- [ ] All components can be developed in parallel
- [ ] Clear integration points with tests
- [ ] Documentation enables new contributors
- [ ] AI agents can modify each component independently

## Risk Mitigation

### Risk 1: JSON files too large
- **Mitigation:** Aggressive pagination (50 jobs/page), compression, lazy loading
- **Fallback:** Reduce data per job (remove long text fields), increase pagination

### Risk 2: GitHub Pages rate limits
- **Mitigation:** CDN caching, client-side optimization
- **Fallback:** Move to Cloudflare Pages or Netlify (still free, more generous limits)

### Risk 3: Complex deployment breaks existing scrapers
- **Mitigation:** Keep deployment separate, use feature flags, comprehensive testing
- **Fallback:** Rollback via git revert, maintain stable branch

### Risk 4: SPA framework choice locks in technology
- **Mitigation:** Abstract API layer, use standard web technologies, avoid framework-specific patterns
- **Fallback:** Can rebuild frontend with different framework (API contract remains stable)

## Open Questions for Agent Implementation

1. **Pagination strategy:** Fixed size (100 jobs/page) or dynamic based on data size?
2. **Filtering approach:** Client-side (load index, filter locally) or pre-generated filtered pages?
3. **Time series granularity:** Daily, weekly, or monthly data points for trends?
4. **Analysis caching:** Compute all analyses daily or on-demand with caching?
5. **SPA routing:** Hash routing (#/jobs) or history API (/jobs) with 404 fallback?

## References

- Repository database schemas: `src/scrape_database.py`, `src/data_database.py`
- Existing analytics spec: `ANALYTICS_SPEC.md`
- LLM extraction prompt: `config/settings.py` (job_to_db_prompt)
- Job categorization: Fields include job_function, specialization, industry

## Next Steps

Each implementing agent should:
1. Read this architecture document
2. Read their specific component specification
3. Explore referenced code files
4. Create implementation plan
5. Begin development with tests
6. Document integration points
7. Coordinate with other agents via integration tests
