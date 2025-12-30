# Job Market Scraper - Development and Testing Guide

This guide provides comprehensive instructions for developing, testing, and debugging the Node.js backend and frontend filtering system.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Setting Up Development Environment](#setting-up-development-environment)
3. [Running the Node.js Server](#running-the-nodejs-server)
4. [Testing the Frontend](#testing-the-frontend)
5. [Debugging Tools and Methods](#debugging-tools-and-methods)
6. [Filter Logic Implementation](#filter-logic-implementation)
7. [API Endpoints](#api-endpoints)
8. [Development Workflow](#development-workflow)
9. [Performance Optimization](#performance-optimization)
10. [Common Issues and Solutions](#common-issues-and-solutions)

## System Architecture

### Overview
The system consists of two main components:

1. **Python Backend** (`main.py` + `src/` modules)
   - Job scraping from multiple sites
   - LLM data processing
   - Database management
   - Static file generation

2. **Node.js Frontend Server** (`server.mjs`)
   - Serves static files
   - Provides API endpoints
   - Handles filtering logic
   - Client-side filtering for MVP

### Data Flow
```
Python Backend → Static JSON Files → Node.js Server → Frontend Filtering → User Interface
```

### File Structure
```
/home/catalin/dev/job-market/
├── src/                          # Python scraping modules
├── pages/                        # Frontend files
│   ├── index.html               # Main UI
│   ├── api/                     # Static JSON data
│   │   ├── jobs/               # Job listings (page-1.json, page-2.json, etc.)
│   │   └── lookups/            # Filter options
│   └── js/
│       ├── main.js             # Vue.js component
│       ├── api.js              # API client (browser)
│       ├── filters.js          # Filter logic (browser)
│       └── core/
│           ├── api.js          # API logic (Node.js + browser)
│           └── filters.js      # Filter logic (Node.js + browser)
├── server.mjs                  # Node.js server
└── debug-*.html               # Debug pages
```

## Setting Up Development Environment

### Prerequisites
1. **Node.js**: Version 18 or higher
2. **Python**: Version 3.10 or higher (for the scraping backend)
3. **Basic web server**: For testing static files

### Installation

#### 1. Node.js Setup
```bash
# Check Node.js version
node --version
# Should be 18+

# Install dependencies (if any package.json exists)
npm install
```

#### 2. Python Setup
```bash
# Navigate to project root
cd /home/catalin/dev/job-market

# Install Python dependencies
pip install -r requirements.txt
# OR if no requirements.txt exists:
pip install rich openai python-dotenv requests beautifulsoup4 aiohttp ipykernel matplotlib pandas jinja2 sqlalchemy
```

#### 3. Generate Test Data
```bash
# Run the Python backend to generate static files
python main.py

# Or run specific modules
python -m src.scrape_jobs_list  # Stage 1: URL collection
python -m src.scrape_job_details  # Stage 2: Detail extraction
python -m src.structure_data_with_llm  # Stage 3: Data processing
python -m src.generate_html_page_fixed  # Generate static files
```

## Running the Node.js Server

### Basic Server Operation
```bash
# Start the Node.js server
node server.mjs

# Server will start on http://localhost:3000
# API available at http://localhost:3000/api
```

### Server Configuration
The server is configured in `server.mjs`:
- **Port**: 3000 (configurable via PORT environment variable)
- **Static files**: Serves from `pages/` directory
- **CORS**: Enabled for all origins
- **Data loading**: Automatically loads static JSON files

### Environment Variables
```bash
# Set custom port
PORT=8000 node server.mjs

# Set custom data directory (if implemented)
DATA_DIR=/custom/path node server.mjs
```

### Server Features
- **Static file serving**: HTML, CSS, JS, JSON files
- **API endpoints**: Jobs, lookups, metadata, filtering
- **Health checks**: `/api/health` endpoint
- **Auto-loading**: Loads all static data on startup

## Testing the Frontend

### 1. Basic Testing
```bash
# Start server
node server.mjs

# Open browser to test main page
open http://localhost:3000
```

### 2. API Testing
Test API endpoints directly:
```bash
# Test health check
curl http://localhost:3000/api/health

# Test metadata
curl http://localhost:3000/api/jobs/index.json

# Test jobs
curl http://localhost:3000/api/jobs/page-1.json

# Test lookups
curl http://localhost:3000/api/lookups/industries.json
```

### 3. Filter Testing
Use the provided debug pages:
```bash
# Interactive filter testing
open http://localhost:3000/debug-filters.html

# Logic testing with buttons
open http://localhost:3000/logic-debug.html

# Console debugging scripts
open http://localhost:3000/simple-test.html
```

### 4. Comprehensive Testing
```bash
# Test all filter combinations
open http://localhost:3000/test-filtering.html

# Test API endpoints
open http://localhost:3000/test-api.html

# Test data structure
open http://localhost:3000/test-data.html
```

## Debugging Tools and Methods

### 1. Debug Pages
The system includes several debug pages for testing:

#### `debug-filters.html`
- Interactive filter testing
- Real-time console logging
- Test all filter types
- Validate filter combinations

#### `logic-debug.html`
- Filter logic testing with buttons
- Step-by-step validation
- Immediate feedback on filter results

#### Console Debug Scripts
- `console-debug.js`: Basic filtering test
- `comprehensive-debug.js`: Detailed analysis
- `vue-debug.js`: Vue component simulation
- `component-test.js`: Tests current Vue behavior

### 2. Browser Developer Tools
```javascript
// Test filtering in browser console
// Open http://localhost:3000 and open Developer Tools

// Test basic filtering
console.log('Testing filters...');
const filters = {
    search: 'developer',
    industry: '',
    department: '',
    // ... other filters
};

// Test API calls
fetch('/api/jobs?page=1&search=developer')
    .then(r => r.json())
    .then(data => console.log(data));

// Test filter manager
if (window.FilterManager) {
    console.log('FilterManager available');
    console.log('Current filters:', window.FilterManager.filters);
}
```

### 3. Server-Side Debugging
```bash
# Check server logs
node server.mjs 2>&1 | grep -E "(Error|Loading|Loaded)"

# Test server endpoints
curl -v http://localhost:3000/api/jobs/index.json
```

### 4. Python Backend Debugging
```bash
# Enable debug mode in Python
export DEBUG=true
python main.py

# Test individual modules
python -c "from src.scrape_database import ScrapeSessionLocal, Job; db = ScrapeSessionLocal(); print(f'Database has {db.query(Job).count()} jobs'); db.close()"
```

## Filter Logic Implementation

### Core Filter Logic
The filtering logic is implemented in two identical modules:

1. **Node.js Version**: `pages/js/core/filters.js`
2. **Browser Version**: `pages/js/core/api.js`

### Filter Types Supported
1. **Search**: Title, company, skills (hard/soft)
2. **Hierarchical**: Industry → Department → Job Family → Specialization
3. **Job Details**: Function, seniority level, education
4. **Skills**: Hard skills, soft skills, certifications, licenses (multi-select)
5. **Work Arrangement**: Employment type, contract type, schedule, remote work
6. **Location**: Country, region, city
7. **Company**: Size, company names (multi-select)
8. **Salary**: Min/max, currency, period, has_salary flag
9. **Benefits**: Benefits, work environment, professional development, work-life balance
10. **Work Conditions**: Physical requirements, work conditions, special requirements

### Filter Implementation Details

#### Client-Side Filtering (Current MVP)
```javascript
// Load all jobs (300 jobs) into memory
// Apply all filters using filterJobs() method
// Paginate results client-side
// Update UI with filtered results
```

#### Server-Side API (Future Optimization)
```javascript
// API endpoints support server-side filtering
// Filter parameters passed as query parameters
// Server applies filters and returns paginated results
// Reduces client-side processing for large datasets
```

### Filter Performance
- **Current**: Loads all 300 jobs, filters in memory
- **Performance**: Fast for small datasets (< 1000 jobs)
- **Memory**: ~5-10MB for job data
- **Future**: Server-side filtering for scalability

## API Endpoints

### Job Endpoints
- `GET /api/jobs/index.json` - Metadata (total jobs, pages, timestamps)
- `GET /api/jobs/page-{n}.json` - Jobs for specific page (100 jobs per page)
- `GET /api/jobs?page={n}&filter1=value1&filter2=value2` - Filtered jobs with pagination

### Lookup Endpoints
- `GET /api/lookups/{type}.json` - Filter options for specific type
- `GET /api/lookups` - All lookup types

### System Endpoints
- `GET /api/health` - Health check and statistics
- `GET /api/filters/metadata` - Filter metadata for UI
- `GET /api/filters/stats` - Filter statistics

### Response Format
```json
{
  "jobs": [...],
  "page": 1,
  "totalPages": 5,
  "totalJobs": 450
}
```

## Development Workflow

### 1. Making Changes to Filter Logic
```bash
# Edit filter logic in both files:
# - pages/js/core/filters.js (Node.js version)
# - pages/js/core/api.js (Browser version)

# Test changes
node server.mjs
open http://localhost:3000/debug-filters.html
```

### 2. Adding New Filter Types
```javascript
// 1. Add filter to FilterManager class
// 2. Add filter to Vue.js component
// 3. Add filter to HTML template
// 4. Add filter to lookup data (if needed)
// 5. Test thoroughly
```

### 3. Updating Static Data
```bash
# Generate new data with Python backend
python main.py

# Verify data structure
ls pages/api/jobs/
ls pages/api/lookups/
```

### 4. Testing Changes
```bash
# 1. Start server
node server.mjs

# 2. Test in browser
open http://localhost:3000

# 3. Use debug pages
open http://localhost:3000/debug-filters.html

# 4. Test API manually
curl "http://localhost:3000/api/jobs?page=1&search=developer"
```

## Performance Optimization

### Current Performance (MVP)
- **Data Size**: ~300 jobs
- **Memory Usage**: ~5-10MB
- **Load Time**: < 1 second
- **Filter Time**: < 100ms

### Future Optimizations
1. **Server-Side Filtering**: Move filtering to server for large datasets
2. **Lazy Loading**: Load jobs on demand
3. **Caching**: Cache filtered results
4. **Indexing**: Database indexing for faster queries
5. **Pagination**: Server-side pagination for better performance

### Performance Monitoring
```javascript
// Add performance monitoring
console.time('filtering');
const filteredJobs = filterManager.filterJobs(allJobs, filters);
console.timeEnd('filtering');

console.time('pagination');
const result = filterManager.paginateJobs(filteredJobs, page);
console.timeEnd('pagination');
```

## Common Issues and Solutions

### Issue 1: Filters Not Working
**Symptoms**: Filters update URL but don't change displayed jobs
**Solutions**:
1. Check that filter logic is implemented in both files
2. Verify filter names match between frontend and backend
3. Test with debug pages
4. Check browser console for errors

### Issue 2: Server Won't Start
**Symptoms**: `node server.mjs` fails with errors
**Solutions**:
1. Check Node.js version: `node --version`
2. Verify file permissions
3. Check for syntax errors in server.mjs
4. Ensure required modules are available

### Issue 3: Data Not Loading
**Symptoms**: Jobs don't appear, loading spinner continues
**Solutions**:
1. Verify static files exist in `pages/api/jobs/`
2. Check server console for error messages
3. Test API endpoints directly with curl
4. Verify data format matches expected structure

### Issue 4: Filter Combinations Don't Work
**Symptoms**: Multiple filters applied but results don't match expectations
**Solutions**:
1. Test filters individually first
2. Use debug pages to test combinations
3. Check filter logic for AND/OR logic issues
4. Verify data structure matches filter expectations

### Issue 5: Performance Issues
**Symptoms**: Slow loading, laggy filtering
**Solutions**:
1. Check data size - may need server-side filtering
2. Monitor memory usage
3. Add performance logging
4. Consider lazy loading for large datasets

## Advanced Development

### Adding New Features
1. **New Filter Types**:
   - Add to FilterManager class
   - Update Vue.js component
   - Add to HTML template
   - Add lookup data if needed

2. **New API Endpoints**:
   - Add to server.mjs routes
   - Implement in FilterManager class
   - Update frontend API client

3. **New UI Components**:
   - Add to Vue.js component
   - Update HTML template
   - Add CSS styles if needed

### Code Organization
- **Core Logic**: `pages/js/core/` - Shared between Node.js and browser
- **Browser Logic**: `pages/js/` - Browser-specific code
- **Server Logic**: `server.mjs` - Node.js server code
- **Static Data**: `pages/api/` - JSON data files

### Testing Strategy
1. **Unit Tests**: Test individual filter functions
2. **Integration Tests**: Test filter combinations
3. **Manual Tests**: Use debug pages for comprehensive testing
4. **Performance Tests**: Monitor loading and filtering times

### Deployment Considerations
1. **Static Files**: Ensure all JSON files are deployed
2. **Server Configuration**: Set appropriate port and CORS settings
3. **Performance**: Consider server-side filtering for production
4. **Monitoring**: Add logging and health checks

This guide provides a comprehensive overview of the development and testing process for the Job Market Scraper system. Use the debug pages and console tools extensively to ensure proper functionality during development.