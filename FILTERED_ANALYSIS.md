# Filtered Analysis Page

## Overview

The Filtered Analysis Page is a new analysis feature that uses **OR logic** for filtering, unlike the main Jobs page which uses AND logic. This allows users to analyze jobs that match ANY of the selected filters rather than ALL of them.

## Features

### 1. OR-Based Filtering
- Jobs matching **ANY** selected filter are included in the analysis
- Multiple filters can be applied across different categories
- Example: Select "Remote Work" OR "Chisinau" OR "Senior Level" to analyze all jobs matching any of these criteria

### 2. Namespace-Style Filter Display
- Active filters are displayed in a clear, removable format: `field_name == "value"`
- Easy to see which filters are applied
- Click any filter badge to remove it
- Example: `job_function == "Software Development"`, `city == "Chisinau"`

### 3. No Item Counts in Filter Dropdown
- Unlike the Jobs page filter panel, this page doesn't show counts next to filter options
- Keeps the interface cleaner and focuses on analysis rather than browsing
- Filters are still validated to ensure they have jobs

### 4. Predefined High-Quality Analyses

Ten carefully crafted analyses are available:

1. **Tech Hub Analysis** - Jobs in major tech cities OR requiring key tech skills
2. **Remote vs Office Distribution** - Compare fully remote, hybrid, and office-based positions
3. **Top Job Functions Analysis** - Most common job functions
4. **Seniority Level Distribution** - Breakdown by seniority with salary info
5. **Industry Comparison** - Opportunities across different industries
6. **Geographic Distribution** - Job opportunities by location
7. **Employment Type Analysis** - Full-time, part-time, contract distribution
8. **Company Size Preferences** - Opportunities by company size
9. **Education Requirements** - Distribution of education requirements
10. **Top Hiring Companies** - Companies with most job openings

## How to Use

### Accessing the Page
1. Navigate to the **Analysis** dropdown in the main navigation
2. Select **Filtered Analysis**
3. Or directly visit: `#!/analysis-filtered`

### Building Your Analysis
1. **Select Filters**: Use the left sidebar to select filters from various categories:
   - Job Details (title, seniority, industry, etc.)
   - Requirements (education, skills, certifications)
   - Work Arrangement (employment type, remote work, schedule)
   - Location (city, region, country)
   - Company (name, size)
   - Benefits & Culture

2. **View Active Filters**: Selected filters appear as namespace-style tags in the main area
   - Format: `category == "value"`
   - Click the X to remove a filter
   - "Clear All" button to reset

3. **Run Analysis**: 
   - Click "Run Analysis with Filters" button
   - Or select one of the 10 predefined analyses
   - Filters will be applied using OR logic

4. **View Results**:
   - Charts visualize the filtered data
   - View the SQL query used
   - See the raw data table

## Technical Details

### OR Logic Implementation
The page builds SQL WHERE clauses using OR conditions:
- Multiple values in the same field: `field = 'value1' OR field = 'value2'`
- Multiple fields: `(field1 = 'x') OR (field2 = 'y')`
- Many-to-many relationships handled via subqueries

### Filter Structure
Filters are stored as:
```javascript
{
  fieldName: [
    { value: "filterValue", label: "Field Label" },
    ...
  ]
}
```

### SQL Query Modification
The base SQL queries are modified dynamically:
1. Extract base query from predefined analysis
2. Build WHERE clause with OR conditions from active filters
3. Inject WHERE clause into appropriate position
4. Execute modified query with parameters

## Comparison with Jobs Page

| Feature | Jobs Page | Filtered Analysis Page |
|---------|-----------|----------------------|
| Filter Logic | AND (must match ALL) | OR (match ANY) |
| Item Counts | Shown in dropdowns | Hidden |
| Purpose | Browse/Find specific jobs | Analyze trends across criteria |
| Filter Display | Dropdown selections | Namespace tags |
| Navigation | Pagination | Analysis results |

## Use Cases

1. **Market Comparison**: Analyze "Remote Work" OR "Hybrid" to see remote work trends
2. **Multi-City Analysis**: Select multiple cities to compare job markets
3. **Skill Demand**: Analyze jobs requiring "Python" OR "JavaScript" OR "Java"
4. **Career Path Exploration**: Compare "Junior" OR "Mid-level" OR "Senior" positions
5. **Industry Insights**: Analyze "IT" OR "Finance" OR "Healthcare" industries

## Future Enhancements

Potential improvements for future versions:
- Save custom filter combinations
- Export analysis results
- Compare multiple filter sets side-by-side
- Time-based filtering for trend analysis
- More chart types (scatter plots, heat maps)
