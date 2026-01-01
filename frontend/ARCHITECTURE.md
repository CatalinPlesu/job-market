# Frontend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Moldova Job Market SPA                    │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Mithril   │  │  DaisyUI   │  │ Chart.js   │   CDN      │
│  │    9KB     │  │    +TW     │  │  Charts    │   Based    │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP Requests
                           ▼
                  ┌─────────────────┐
                  │   JSON API      │
                  │   /api/...      │
                  └─────────────────┘
                           │
                           ├── /api/jobs/index.json
                           ├── /api/jobs/page-1.json
                           ├── /api/jobs/{id}/detail.json
                           └── /api/analysis/...
```

## Application Structure

```
index.html (Entry Point)
    │
    ├── CDN Resources
    │   ├── Mithril.js
    │   ├── DaisyUI + Tailwind
    │   └── Chart.js
    │
    └── app.js (Main Application)
        │
        ├── API Client
        │   ├── getJobsIndex()
        │   ├── getJobsPage(n)
        │   ├── getJobDetail(id)
        │   └── getAnalysis(endpoint)
        │
        ├── State Management
        │   ├── jobsIndex
        │   ├── currentPage
        │   ├── jobs[]
        │   ├── filters{}
        │   └── loading
        │
        ├── Components
        │   ├── Header
        │   ├── Footer
        │   ├── Loading
        │   ├── FilterPanel
        │   ├── JobListItem
        │   └── Layout
        │
        └── Pages
            ├── HomePage (/)
            ├── JobsPage (/jobs)
            ├── JobDetailPage (/jobs/:id)
            └── AnalysisPage (/analysis)
```

## Data Flow

### Job Listing Flow
```
User Action                State Update             UI Update
─────────────────────────────────────────────────────────────
1. Visit /jobs        →   Load index + page    →   Show jobs
2. Apply filter       →   Update filters{}     →   Filter jobs
3. Click next page    →   Increment page       →   Load new jobs
4. Click job          →   Navigate to detail   →   Show detail
```

### Filtering Flow (Client-Side)
```
┌─────────────────┐
│ User selects    │
│ filter option   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update state    │
│ filters[key]    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ matchesFilters()│──────▶│ Filter jobs[]    │
│ function        │      │ client-side      │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐
│ Update UI       │
│ Show filtered   │
│ jobs            │
└─────────────────┘
```

## Component Hierarchy

```
Layout
├── Header
│   ├── Logo
│   ├── Navigation
│   │   ├── Home
│   │   ├── Jobs
│   │   └── Analysis
│   └── ThemeToggle
│
├── Main (Route-based)
│   │
│   ├── HomePage
│   │   ├── Hero Section
│   │   ├── Statistics
│   │   └── CTA Button
│   │
│   ├── JobsPage
│   │   ├── FilterPanel
│   │   │   ├── Basic Filters (6)
│   │   │   ├── Advanced Filters (6)
│   │   │   ├── Filter Badges
│   │   │   └── Clear Button
│   │   ├── Job List
│   │   │   └── JobListItem × N
│   │   └── Pagination
│   │
│   ├── JobDetailPage
│   │   ├── Header
│   │   ├── Tabs
│   │   │   ├── Parsed View
│   │   │   │   ├── Salary
│   │   │   │   ├── Requirements
│   │   │   │   ├── Responsibilities
│   │   │   │   └── Benefits
│   │   │   └── Raw View
│   │   │       ├── Original Info
│   │   │       ├── Description
│   │   │       └── Source Link
│   │   └── Back Button
│   │
│   └── AnalysisPage
│       ├── Statistics Cards
│       ├── Info Alert
│       └── Analysis List
│           └── Analysis Card × N
│
└── Footer
    └── Copyright
```

## State Management

```javascript
state = {
    jobsIndex: {
        total_jobs: number,
        total_pages: number,
        filters: {
            job_function: string[],
            seniority_level: string[],
            // ... 50+ fields
        }
    },
    
    currentPage: number,
    
    jobs: [
        {
            id: number,
            title: string,
            company: string,
            location: {},
            salary: {},
            // ...
        }
    ],
    
    filters: {
        job_function?: string,
        seniority_level?: string,
        // ... applied filters
    },
    
    loading: boolean,
    
    analysisIndex: {
        available_analyses: [],
        data_summary: {}
    }
}
```

## Routing

```
Hash-based routing (#/)

Routes:
  /                 → HomePage
  /jobs             → JobsPage
  /jobs/:id         → JobDetailPage
  /analysis         → AnalysisPage

Example URLs:
  http://site.com/#/
  http://site.com/#/jobs
  http://site.com/#/jobs/123
  http://site.com/#/analysis
```

## Performance Optimizations

### Client-Side Filtering
```
┌──────────────┐
│ 100 jobs     │
│ loaded       │
└──────┬───────┘
       │
       │ Apply filters (client-side)
       │ Time: <100ms
       ▼
┌──────────────┐
│ 25 jobs      │
│ displayed    │
└──────────────┘

No API call needed!
```

### CDN Delivery
```
All libraries from CDN:
- No build step
- No bundling
- Instant deployment
- Browser caching
- Global CDN
```

### Minimal State Updates
```
Mithril's virtual DOM:
- Efficient diffing
- Minimal re-renders
- Fast updates
- Small memory footprint
```

## Extensibility Points

### Adding New Filter Field
```javascript
// 1. Add to filter fields array
{ key: 'new_field', label: 'New Field', basic: false }

// 2. Add to matchesFilters()
case 'new_field':
    if (job.new_field !== value) return false;
    break;

// 3. Ensure index.json has the field
filters: {
    new_field: ["option1", "option2"]
}
```

### Adding New Page
```javascript
// 1. Create component
const NewPage = {
    view: () => m('div', 'New page content')
};

// 2. Add route
'/new': {
    render: () => m(Layout, m(NewPage))
}

// 3. Add navigation link
m('li', m('a', { href: '#!/new' }, 'New Page'))
```

### Adding Chart
```javascript
// 1. Create canvas in component
m('canvas', { id: 'myChart' })

// 2. Initialize Chart.js in oncreate
oncreate: (vnode) => {
    new Chart(vnode.dom, {
        type: 'bar',
        data: {...},
        options: {...}
    });
}
```

## Deployment Architecture

```
┌─────────────────┐
│  GitHub Repo    │
│                 │
│  ┌───────────┐  │
│  │ frontend/ │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ Generate + Copy
         ▼
┌─────────────────┐
│  pages/         │
│  ├── index.html │
│  ├── app.js     │
│  └── api/       │
└────────┬────────┘
         │
         │ Deploy
         ▼
┌─────────────────┐
│  Hosting        │
│  - GitHub Pages │
│  - Netlify      │
│  - Vercel       │
└─────────────────┘
```

## Security Model

```
Frontend (Public)
├── No secrets
├── No auth tokens
├── Read-only access
└── Static files only

API (JSON Files)
├── Pre-generated
├── Sanitized data
├── No personal info
└── No backend needed

Deployment
├── HTTPS only
├── CORS configured
└── CDN secured
```

## Technology Decisions

### Why Mithril.js?
- ✅ Small (9KB gzipped)
- ✅ Fast rendering
- ✅ Simple API
- ✅ No build required
- ✅ Great documentation

### Why DaisyUI?
- ✅ Rich components
- ✅ Built-in themes
- ✅ Tailwind-based
- ✅ Easy customization
- ✅ Responsive defaults

### Why CDN?
- ✅ Zero build step
- ✅ Fast deployment
- ✅ Browser caching
- ✅ Global availability
- ✅ Simple updates

### Why Client-Side Filtering?
- ✅ Instant updates
- ✅ No API overhead
- ✅ Works offline
- ✅ Less complexity
- ✅ Better UX

## Future Architecture Considerations

### If Scaling Needed
1. Switch to server-side API
2. Add authentication layer
3. Implement pagination API
4. Use database queries for filtering
5. Add caching layer (Redis)

### If Features Grow
1. Code splitting (dynamic imports)
2. Service worker (PWA)
3. State management library (if state becomes complex)
4. Build step (for optimization)
5. TypeScript (for type safety)

### If Performance Issues
1. Virtual scrolling for long lists
2. Lazy loading images
3. Request debouncing
4. Memoization
5. Web workers for filtering

## Monitoring & Maintenance

### What to Monitor
- Page load times
- API response times
- Error rates
- User interactions
- Browser compatibility

### Regular Maintenance
- Update CDN versions
- Review security advisories
- Test new browser versions
- Update documentation
- Respond to user feedback

## Conclusion

The architecture is:
- ✅ Simple and maintainable
- ✅ Fast and responsive
- ✅ Scalable and extensible
- ✅ Well-documented
- ✅ Production-ready
