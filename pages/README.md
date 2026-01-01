# Moldova Job Market - Frontend SPA

A single-page application (SPA) built with **Mithril.js** for browsing and filtering Moldova's job market data.

## 🎯 Features

- **32+ Filter Dimensions**: Comprehensive filtering across all job attributes
- **Hierarchical Filtering**: Industry → Department → Job Family → Specialization cascade
- **Instant Updates**: Filters apply in real-time with debouncing
- **URL State Management**: All filters reflected in URL for bookmarking/sharing
- **Multi-select Filters**: Skills, languages, certifications, and more
- **Range Filters**: Salary and experience years
- **Job Detail View**: Parsed (structured) and raw (original) data tabs
- **Mobile Responsive**: DaisyUI components with Tailwind CSS
- **Theme Support**: DaisyUI theming with semantic colors

## 🏗️ Architecture

### Technology Stack
- **Framework**: Mithril.js 2.2.2 (CDN)
- **Styling**: DaisyUI 4.12.14 + Tailwind CSS (CDN)
- **Utilities**: Lodash 4.17.21 (CDN)
- **Build**: None required - pure CDN approach
- **Hosting**: GitHub Pages compatible

### Component Structure

```
pages/
├── index.html                  # Main HTML entry point
├── js/
│   ├── main.js                # App initialization and state management
│   ├── components/            # Mithril components (modular)
│   │   ├── Header.js         # Site header with stats and search
│   │   ├── FilterPanel.js    # Comprehensive filter sidebar
│   │   ├── JobList.js        # Job cards grid with loading states
│   │   ├── JobCard.js        # Individual job card component
│   │   ├── JobDetail.js      # Job detail modal with tabs
│   │   └── Pagination.js     # Pagination controls
│   └── core/                  # Framework-agnostic modules
│       ├── api.js            # API client for data fetching
│       └── filters.js        # Filter logic and utilities
└── api/                       # Mock/generated JSON data
    ├── jobs/
    │   ├── index.json        # Metadata
    │   └── page-*.json       # Paginated jobs
    └── lookups/              # Reference data
        └── *.json
```

## 🚀 Quick Start

### Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/CatalinPlesu/job-market.git
   cd job-market/pages
   ```

2. **Start a local server**
   ```bash
   python3 -m http.server 8080
   ```
   
   Or use Node.js:
   ```bash
   npx http-server -p 8080
   ```

3. **Open browser**
   ```
   http://localhost:8080
   ```

### Production Build

No build step required! Simply:
1. Generate API data using Python backend
2. Deploy `pages/` directory to GitHub Pages
3. All assets load from CDN

## 📋 Filter Capabilities

### Job Classification (6 filters)
- Industry → Department → Job Family → Specialization (hierarchical)
- Job Function
- Seniority Level

### Requirements (8 filters)
- Required Education
- Experience Years (range: min/max)
- Hard Skills (multi-select)
- Soft Skills (multi-select)
- Certifications (multi-select)
- Licenses (multi-select)

### Work Arrangement (8 filters)
- Employment Type
- Contract Type
- Work Schedule
- Shift Details
- Remote Work
- Travel Required

### Location (3 filters)
- Country
- Region
- City

### Company Information (3 filters)
- Company Size
- Companies (multi-select with search)

### Salary (5 filters)
- Salary Range (MDL): min/max values
- Has Salary (boolean)
- Salary Currency
- Salary Period

### Benefits & Perks (4 filters)
- Benefits (multi-select)
- Work Environment (multi-select)
- Professional Development (multi-select)
- Work Life Balance (multi-select)

### Work Conditions (3 filters)
- Physical Requirements (multi-select)
- Work Conditions (multi-select)
- Special Requirements (multi-select)

## 🎨 UI Components

### DaisyUI Theming
All components use semantic DaisyUI classes for automatic theme support:
- `btn-primary`, `btn-secondary`, `btn-ghost`
- `card`, `card-body`
- `badge`, `badge-primary`, `badge-ghost`
- `input`, `select`, `checkbox`
- `modal`, `tabs`
- Theme switching via `data-theme` attribute

### Color Palette
Uses DaisyUI semantic colors:
- Primary: Job actions, active filters
- Success: Salary information
- Warning: Alerts and notifications
- Error: Error states
- Base: Content and backgrounds

## 🔌 API Integration

### Endpoints

**Jobs**
- `GET /api/jobs/index.json` - Metadata (total count, pages)
- `GET /api/jobs/page-{N}.json` - Paginated job listings

**Lookups**
- `GET /api/lookups/{type}.json` - Reference data
  - industries, departments, job_families, specializations
  - cities, regions, countries
  - seniority_levels, employment_types, remote_work_options
  - And 20+ more lookup types

### Data Flow
1. **Initialization**: Load metadata and all lookup tables
2. **Job Loading**: Fetch all job pages (client-side filtering)
3. **Filtering**: Apply filters in-memory with instant updates
4. **Pagination**: Client-side pagination of filtered results
5. **URL Sync**: Bidirectional sync between filters and URL

## 📱 Mobile Responsiveness

- Mobile-first design with DaisyUI
- Collapsible filter sidebar on mobile
- Responsive grid layout (1 column → 2 columns → 4 columns)
- Touch-friendly controls
- Optimized for phones and tablets

## 🧪 Testing

### Manual Testing
1. Start local server
2. Verify all filters work
3. Test hierarchical filtering cascade
4. Check URL state management
5. Test job detail modal
6. Verify mobile responsiveness

### Browser Compatibility
- Chrome/Edge (Chromium)
- Firefox
- Safari
- Mobile browsers

## 🔄 Migration from Vue.js

This project was migrated from Vue.js 3 to Mithril.js. Key changes:

- **Replaced**: Vue.js → Mithril.js
- **Added**: DaisyUI for theming
- **Kept**: Core filtering logic (framework-agnostic)
- **Kept**: API client (framework-agnostic)
- **Improved**: Component modularity (separate files)

Old Vue.js files are backed up as:
- `index-vue-backup.html`
- `js/main-vue-backup.js`

## 📦 Dependencies (CDN)

All dependencies loaded from CDN (no npm required):

```html
<!-- DaisyUI + Tailwind CSS -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.14/dist/full.min.css" />
<script src="https://cdn.tailwindcss.com"></script>

<!-- Mithril.js -->
<script src="https://unpkg.com/mithril@2.2.2/mithril.js"></script>

<!-- Lodash -->
<script src="https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js"></script>
```

## 🤝 Contributing

### Adding New Components
1. Create new file in `js/components/`
2. Export Mithril component
3. Import in `main.js`
4. Use DaisyUI classes for styling

### Adding New Filters
1. Add filter to `createDefaultFilters()` in `filters.js`
2. Add filter logic to `filterJobs()` in `filters.js`
3. Add filter UI to `FilterPanel.js`
4. Add lookup endpoint in `api.js` if needed

## 📝 License

This project is part of the Moldova Job Market scraper and analysis system.

## 🔗 Related

- **Backend**: Python scraper with LLM-powered data extraction
- **Database**: Dual database system (raw + processed)
- **Analysis**: Job market analytics and trends
- **Deployment**: GitHub Pages with static JSON API

## 📧 Contact

For questions or issues, please open a GitHub issue.
