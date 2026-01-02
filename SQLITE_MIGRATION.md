# SQLite Database Migration Guide

This document explains the migration from JSON-based API to SQLite database loaded client-side.

## Overview

The frontend now loads the SQLite database directly in the browser using SQL.js (WebAssembly) and performs all queries client-side. This provides:

- **Instant filtering and sorting** - No network requests needed
- **Reduced server bandwidth** - Single database file vs multiple JSON files
- **More flexible querying** - Full SQL capabilities in the browser
- **Better scalability** - No need to pre-generate paginated JSON files

## Changes Made

### Frontend Architecture

1. **Database Loading** (`DatabaseManager`)
   - Loads `data.db` from `/api/data.db` on application startup
   - Uses SQL.js from CDN (cdnjs.cloudflare.com)
   - Caches database in browser memory
   - Handles loading states and errors

2. **SQL Query Interface** (`dbApi`)
   - `getJobs()` - Fetch jobs with filtering, sorting, pagination
   - `getMetadata()` - Get filter options and counts
   - `formatJob()` - Format database rows to match JSON API structure
   - Helper functions for related data (skills, benefits, etc.)

3. **Updated Components**
   - `HomePage` - Loads database metadata
   - `JobsPage` - Uses SQL queries for pagination and filtering
   - `JobDetailPage` - Queries individual jobs by ID
   - `FilterPanel` - Simplified to use metadata directly

### Key Improvements

- **Debounced Inputs**: Salary and experience filters wait 500ms before querying
- **SQL-Based Filtering**: All filters converted to WHERE clauses
- **SQL-Based Sorting**: Uses ORDER BY for instant sorting
- **SQL-Based Search**: Full-text search using LIKE queries
- **Metadata-Driven Filters**: Filter options loaded from database metadata

## Deployment Instructions

### Step 1: Copy Database

Copy the processed database to the frontend API directory:

```bash
cp databases/data.db frontend/api/
```

### Step 2: Test Locally

Start a local web server to test:

```bash
cd frontend
python -m http.server 8000
# or
npx http-server
```

Open http://localhost:8000 and verify:
- Database loads without errors
- Jobs list displays
- Filters work
- Sorting works
- Pagination works
- Job details pages load

### Step 3: Deploy

Deploy the frontend directory to your static hosting:

**GitHub Pages:**
```bash
# Commit frontend with database
git add frontend/
git commit -m "Deploy with SQLite database"
git push
```

**Netlify/Vercel:**
- Upload the `frontend/` directory
- Ensure `data.db` is included
- Set build command to none (static site)

## Performance Considerations

### Database Size

- Current approach works well for databases up to ~10MB
- For larger databases:
  - Enable HTTP cache headers (Cache-Control, ETag)
  - Use service workers for offline support
  - Consider splitting into multiple databases

### Browser Compatibility

- Works in all modern browsers
- Requires WebAssembly support (all modern browsers)
- SQL.js loaded from CDN (~500KB WASM file)

### Initial Load Time

- Database download time depends on size and connection
- ~5MB database = ~2-5 seconds on average connection
- After initial load, all queries are instant
- Browser may cache the database file

## Backward Compatibility

The old JSON API generation code (`json_generator/`) is preserved but no longer used by the frontend. You can:

1. **Keep it** - For backward compatibility or alternative clients
2. **Deprecate it** - Mark as deprecated in documentation
3. **Remove it** - If no longer needed

## Troubleshooting

### Database Not Loading

**Error**: "Failed to load database: 404"
- **Solution**: Ensure `data.db` is in `frontend/api/`
- Check file permissions
- Verify correct path in deployment

### WASM Loading Failed

**Error**: "Failed to load WASM"
- **Solution**: Check CDN is accessible
- Network may block cdnjs.cloudflare.com
- Try different CDN or local hosting

### Queries Too Slow

**Issue**: Filters/search feel slow
- **Solution**: Database may be too large
- Consider adding database indexes
- Check browser dev tools for performance

### Out of Memory

**Issue**: Browser crashes or becomes unresponsive
- **Solution**: Database is too large for browser
- Reduce database size
- Split into multiple databases
- Use server-side filtering instead

## Future Enhancements

Possible improvements for future consideration:

1. **IndexedDB Caching** - Cache database in IndexedDB for faster subsequent loads
2. **Service Workers** - Enable offline support
3. **Incremental Loading** - Load database in chunks for better UX
4. **Database Indexes** - Add indexes to SQLite for faster queries
5. **Compression** - Compress database file (gzip/brotli)
6. **Delta Updates** - Only download changed data
7. **Web Workers** - Run queries in background thread

## Migration Checklist

- [x] SQL.js added to index.html
- [x] DatabaseManager implemented
- [x] dbApi query interface created
- [x] HomePage converted to SQL
- [x] JobsPage converted to SQL
- [x] JobDetailPage converted to SQL
- [x] FilterPanel simplified
- [x] Documentation updated
- [ ] Database copied to frontend/api/
- [ ] Local testing completed
- [ ] Deployed to production
- [ ] Old JSON API deprecated (optional)

## Support

For issues or questions:
1. Check browser console for error messages
2. Verify database file is accessible
3. Test with a smaller database first
4. Review SQL.js documentation: https://sql.js.org/
