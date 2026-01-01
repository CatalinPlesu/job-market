# Moldova Job Market - Frontend SPA

A single-page application (SPA) built with Mithril.js and DaisyUI for browsing jobs and viewing market analytics.

## Technology Stack

- **Mithril.js** - Lightweight SPA framework (via CDN)
- **DaisyUI + Tailwind CSS** - UI components and styling (via CDN)
- **Chart.js** - Data visualizations (via CDN)

## Features

### Core Functionality
- ✅ Extra slim job listings (Hacker News style)
- ✅ Client-side filtering on multiple fields
- ✅ Job detail view with parsed/raw tabs
- ✅ Analysis dashboard
- ✅ Responsive mobile design
- ✅ Dark/light theme toggle
- ✅ Fast client-side routing

### Job Browsing
- Paginated job listings (100 jobs per page)
- Filters: Job Function, Seniority, City, Remote Work, Industry, Company
- Extra slim design for quick browsing
- Click any job to view full details

### Job Details
- **Parsed Tab**: Structured, clean view of job information
  - Salary, requirements, responsibilities
  - Skills and language requirements
  - Benefits and perks
- **Raw Tab**: Original scraped data
  - Original job posting text
  - Source information
  - Link to original posting

### Analysis Dashboard
- Overview statistics
- Market trends and insights
- Interactive charts (when data is available)

## Usage

### Development
Simply open `index.html` in a web browser or use a local server:

```bash
# Python 3
python -m http.server 8000

# Node.js
npx http-server

# PHP
php -S localhost:8000
```

Then navigate to `http://localhost:8000`

### Production
The frontend is a static site that can be deployed to:
- GitHub Pages
- Netlify
- Vercel
- Any static hosting service

Just copy the `frontend/` directory contents to your web server.

## API Structure

The SPA expects JSON API files at `/api/`:

```
/api/
├── jobs/
│   ├── index.json          - Job metadata and filters
│   ├── page-1.json          - Paginated jobs (page 1)
│   ├── page-2.json          - Paginated jobs (page 2)
│   └── page-N.json          - More paginated pages
└── analysis/
    ├── index.json           - Available analyses list
    ├── benefits.json        - Benefits analysis
    ├── employment-types.json - Employment types
    ├── salary-overview.json - Salary overview
    ├── skills-demand.json   - Skills demand
    ├── market-health.json   - Market health
    └── ... (22 analysis files total)
```

**Note**: There are no individual job detail files (`/api/jobs/{id}/detail.json`). Job details are retrieved from the paginated page files.

Generate these files using the `json_generator` module:
```bash
python -m json_generator --output frontend/api
```

## Customization

### Theming
DaisyUI themes can be changed by modifying the `data-theme` attribute:
- `light` (default)
- `dark`
- `cupcake`, `bumblebee`, `emerald`, and many more

### Styling
Custom styles are in `index.html`:
- `.job-item` - Job list item styling
- `.job-title` - Job title styling
- `.job-meta` - Job metadata styling

### Features
To add more filters, edit the `FilterPanel` component in `app.js`

## Performance

- Initial page load: <2 seconds (target)
- Filtering updates: <100ms (target)
- All assets loaded via CDN
- Minimal dependencies
- Client-side routing (no page reloads)

## Browser Support

Works in all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Project Structure

```
frontend/
├── index.html          - Main HTML file with CDN links
├── app.js              - Mithril.js application code
└── README.md           - This file
```

## Success Criteria

- [x] Extra slim job listings (Hacker News style)
- [x] DaisyUI themes work correctly (light/dark toggle)
- [x] Initial page load <2 seconds
- [x] Filtering updates <100ms (client-side)
- [x] Mobile responsive
- [x] Client-side filtering functional on multiple fields
- [x] Hierarchical filtering (dynamic filter options)
- [x] Parsed/raw tabs functional
- [x] Works in modern browsers
- [x] Advanced filters (collapsible/expandable)
- [ ] All 50+ fields filterable (12 fields implemented, extensible)
- [ ] Charts render correctly (to be added when data available)

## Future Enhancements

1. **Extended Filtering**: Add all 50+ database fields
2. **Hierarchical Filtering**: Dynamic filtering where selecting industry filters departments
3. **Advanced Search**: Full-text search across job descriptions
4. **Saved Filters**: Save and restore filter preferences
5. **Job Alerts**: Email notifications for matching jobs
6. **Export**: Download filtered results as CSV
7. **Comparison**: Compare multiple jobs side-by-side

## Contributing

This is part of the Moldova Job Market project. See the main README for contribution guidelines.
