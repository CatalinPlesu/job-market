# Issue 3: Frontend SPA Implementation

## Title
Build React SPA for Job Market Browsing and Analysis Visualization

## Labels
`enhancement`, `frontend`, `react`

## Description

### Objective
Create a single-page application (SPA) that consumes JSON API files to provide an interactive interface for browsing jobs and viewing market analytics.

### Scope
- Job browsing with pagination
- Client-side filtering (function, location, salary, etc.)
- Job detail view with parsed/raw tabs
- Analysis dashboard with interactive charts
- Mobile-responsive design
- Routing and navigation

### Context
This SPA will be hosted on GitHub Pages and consume static JSON files as a pseudo-API. It should work entirely client-side with no backend.

**Key Features:**
- Smart pagination: Use index.json metadata to load only relevant pages when filtering
- Two-tab job view: Parsed (structured LLM data) vs Raw (original posting)
- Interactive charts: Line charts for trends, bar charts for comparisons, tables for details

**JSON API contracts:** See `planning/github-pages-pseudo-api/02-json-api-generation.md` and `05-analysis-system.md`.

### Input Requirements
- Mock JSON files for development (or wait for JSON generator)
- API endpoints structure:
  - `/api/jobs/index.json` - Job metadata
  - `/api/jobs/page-{N}.json` - Paginated jobs
  - `/api/analysis/index.json` - Analysis metadata
  - `/api/analysis/{analysis-id}.json` - Individual analyses

### Output Definition

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

### Independence
- Can develop with mock JSON files
- No dependency on JSON generation (use sample data)
- No dependency on deployment (test locally with `npm run dev`)
- No dependency on analysis system (mock analysis data)

### Integration Points

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

### Success Criteria
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

### What This Does NOT Depend On
- JSON generation implementation (use mock data)
- Analysis system implementation (use mock data)
- Deployment automation (test locally)
- Real database access

### References
- **Specification:** `planning/github-pages-pseudo-api/03-spa-frontend-structure.md`
- **Architecture:** `planning/github-pages-pseudo-api/01-architecture-strategy.md`
- **JSON schemas:** `02-json-api-generation.md`, `05-analysis-system.md`
- **Analytics requirements:** `ANALYTICS_SPEC.md`

### Implementation Hints
1. Scaffold React app with Vite
2. Set up routing and basic layout
3. Implement job browsing with mock data
4. Add filtering logic
5. Implement job detail view
6. Add analysis dashboard with one chart type
7. Expand to all analysis types
8. Polish UI and add responsiveness
