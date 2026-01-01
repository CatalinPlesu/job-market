# GitHub Pages & Pseudo API Strategy - Planning Documents

## Overview
This folder contains comprehensive planning documents for transforming the job market scraper into a public-facing GitHub Pages site with a JSON-based pseudo-API architecture.

## Purpose
These documents enable **parallel development** by multiple AI agents or developers. Each component can be built independently with clear contracts and integration points.

## Document Structure

### 1. Architecture & Strategy
**File:** `01-architecture-strategy.md`

**Purpose:** High-level system design and technology decisions

**Contents:**
- Overall system architecture diagram
- Technology stack recommendations (React, Vite, etc.)
- Component interaction patterns
- Subrepository decoupling strategy
- Integration points and data flows
- Risk mitigation strategies

**Audience:** All agents - read first for context

---

### 2. JSON API Generation
**File:** `02-json-api-generation.md`

**Purpose:** Specification for generating paginated JSON files from databases

**Contents:**
- Input requirements (database schemas)
- Output JSON structures (index.json, page-N.json, detail.json)
- Pagination strategy with intelligent indexing
- Data sanitization rules (privacy/security)
- Implementation algorithms
- Performance targets

**Audience:** Agent implementing Issue #1 (JSON Generation System)

---

### 3. SPA Frontend Structure
**File:** `03-spa-frontend-structure.md`

**Purpose:** Specification for the React single-page application

**Contents:**
- Technology stack (React, TypeScript, Vite, Tailwind)
- Project structure and component architecture
- API integration with TypeScript types
- Key features (job browsing, filtering, charts)
- Routing and state management
- Mobile responsiveness
- Performance optimization

**Audience:** Agent implementing Issue #3 (Frontend SPA)

---

### 4. Deployment Automation
**File:** `04-deployment-automation.md`

**Purpose:** Specification for GitHub Actions deployment pipeline

**Contents:**
- GitHub Pages deployment architecture
- Workflow file structure
- File preservation strategy (.git, CNAME)
- Error handling and rollback
- Monitoring and notifications
- Testing strategy

**Audience:** Agent implementing Issue #4 (Deployment Pipeline)

---

### 5. Analysis System
**File:** `05-analysis-system.md`

**Purpose:** Specification for computing market statistics and trends

**Contents:**
- 20+ proposed analyses (static and temporal)
- Static analyses: Current market snapshot (salary distributions, skills demand)
- Temporal analyses: Trends over time (posting volume, salary evolution)
- Dynamic hierarchy analysis (job_function → specialization → seniority)
- Time-series data structures
- Implementation approaches with code examples
- Performance optimization

**Audience:** Agent implementing Issue #2 (Analysis Engine)

---

### 6. GitHub Issue Templates
**Folder:** `issues/`

**Purpose:** Individual issue specifications for starting parallel development work

**Contents:**
- **Issue #1:** `01-json-generation-system.md` - JSON Generation System
- **Issue #2:** `02-analysis-engine.md` - Analysis Engine Implementation  
- **Issue #3:** `03-frontend-spa.md` - Frontend SPA Implementation
- **Issue #4:** `04-deployment-pipeline.md` - Deployment Pipeline Automation
- **README.md** - Overview of all issues with dependency graph

Each issue includes:
- Clear scope and boundaries
- Context and background
- Input/output definitions
- Independence statement (what it doesn't depend on)
- Integration points
- Success criteria
- Implementation hints

**Audience:** Project managers, AI agent coordinators

**Quick Start:**
- Go to `issues/` folder to see individual issue specifications
- Each issue is a standalone file ready to be assigned to an agent
- Start with `issues/README.md` for overview and dependency graph

---

## Key Concepts

### Pseudo-API Architecture
Instead of a traditional backend, we generate static JSON files that act as an API:
- **Paginated endpoints:** `/api/jobs/page-1.json`, `/api/jobs/page-2.json`
- **Intelligent indexing:** `/api/jobs/index.json` contains metadata for efficient filtering
- **Analysis endpoints:** `/api/analysis/salary-overview.json`, etc.

### Static-First Design
- No backend server required
- All data pre-computed and cached in JSON
- Hosted on GitHub Pages (free, fast CDN)
- Zero maintenance cost

### Temporal Analysis Support
Unlike typical static analytics, this system tracks trends over time:
- Uses `jobs.created_at` for posting dates
- Uses `job_checks.check_date` + `http_status` for closure dates
- Aggregates by month/week/day for time series
- Enables trend visualization (salary evolution, skill demand shifts, etc.)

### Dynamic Hierarchy
Supports drill-down analysis:
```
Job Function (e.g., Engineering)
  └─ Specialization (e.g., Software Development)
      └─ Seniority Level (e.g., Mid-level)
          └─ Statistics (avg salary, count, etc.)
```

## How to Use These Documents

### For AI Agents
1. **Start with** `01-architecture-strategy.md` for overall context
2. **Read your specific issue** from the `issues/` folder (e.g., `issues/01-json-generation-system.md`)
3. **Deep-dive** into your component's specification document (referenced in your issue)
4. **Explore** referenced code files in the repository
5. **Implement** following the specification
6. **Test** according to success criteria
7. **Document** any deviations or changes

### For Project Coordinators
1. Review `issues/README.md` for overview of all implementation tasks
2. Create GitHub issues using specifications from `issues/` folder
3. Assign issues to different agents for parallel work
4. Monitor progress using success criteria checklists in each issue
5. Coordinate integration testing when components are ready

### For Future Maintainers
1. Read `01-architecture-strategy.md` for system overview
2. Refer to component specs for detailed documentation
3. Check `issues/` folder to understand implementation tasks
4. Update specs when making architectural changes
5. Keep JSON schemas in sync between components

## Development Timeline

### Week 1-2: Foundation
- **Parallel:** JSON Generation (#1) + Frontend scaffolding (#3)
- **Parallel:** Analysis Engine (#2) starts
- **Sequential:** Deployment pipeline (#4) basic structure

### Week 3-4: Integration
- **Integration:** Frontend consumes real JSON from generator
- **Integration:** Frontend visualizes real analysis data
- **Testing:** End-to-end tests with real data

### Week 5-6: Polish & Deploy
- **Optimization:** Performance tuning
- **Testing:** Full deployment pipeline testing
- **Documentation:** User guides, API documentation
- **Launch:** Deploy to production

## Integration Points Summary

| Component | Provides | Consumes |
|-----------|----------|----------|
| JSON Generator | JSON files in `/api/jobs/` | Database files (scrape.db, data.db) |
| Analysis Engine | JSON files in `/api/analysis/` | Database files (both databases) |
| Frontend SPA | Static assets in `/dist/` | JSON files from API endpoints |
| Deployment Pipeline | Deployed GitHub Pages site | All above components |

## Success Criteria Checklist

### Overall Project
- [ ] Strategy documents created and reviewed
- [ ] GitHub issues created and assigned
- [ ] All components can be developed in parallel
- [ ] Integration points are well-defined
- [ ] No hardcoded paths or details
- [ ] Documentation is AI-agent friendly
- [ ] Temporal analysis is fully specified
- [ ] Hierarchy analysis is well-structured

### Component-Specific
See individual specification documents for detailed success criteria.

## References to Existing Code

### Database Schemas
- `src/scrape_database.py` - Raw scraped data (Job, JobCheck)
- `src/data_database.py` - Processed data (JobDetail + 50+ lookups)

### Configuration
- `config/settings.py` - Database paths, LLM prompts, settings
- `config/scraper_rules.json` - Site-specific scraping rules

### Documentation
- `README.md` - Project overview
- `ANALYTICS_SPEC.md` - Original analytics requirements

## Contact & Questions

For questions or clarifications:
1. Read the relevant specification document thoroughly
2. Explore referenced code files in the repository
3. Check existing issues for similar questions
4. Create a new discussion issue with specific questions

## Version History

- **v1.0** (2026-01-01): Initial planning documents created
  - Overall architecture defined
  - JSON API generation specified
  - Frontend structure outlined
  - Deployment automation planned
  - Analysis system designed with temporal support
  - GitHub issue templates prepared

---

**Note:** These are planning documents only. No implementation code is included. Implementation should follow these specifications while remaining flexible to necessary adjustments discovered during development.
