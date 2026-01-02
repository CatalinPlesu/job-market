# Custom Analysis Builder Guide

The Moldova Job Market platform now includes a powerful **Custom Analysis Builder** that allows you to create custom SQL queries and visualize results with Chart.js directly in the browser.

## Features

### 🚀 No Backend Required
- All analysis runs client-side using **SQL.js** (SQLite in the browser)
- Query the full job database directly from your browser
- Real-time results with instant visualization

### 📊 Multiple Chart Types
- **Bar Chart**: Compare values across categories
- **Line Chart**: Show trends over time
- **Doughnut Chart**: Display proportional distributions
- **Pie Chart**: Show percentage breakdowns

### 💾 Persistent Storage
- Save your custom queries to browser localStorage
- Queries persist across sessions
- Load and rerun saved analyses anytime

### 📚 15+ Predefined Analyses
Ready-to-use queries covering:
- **Temporal**: Job postings over time
- **Skills**: Top skills, skill combinations, skills by salary
- **Salary**: Distribution, by seniority, by function, vs experience
- **Distribution**: Industries, locations, remote work, experience requirements
- **Benefits**: Most offered employee benefits
- **Companies**: Top companies hiring

## Database Structure

### Main Tables

#### `job_details`
Main table containing all job postings with the following key columns:
- `id`: Unique job identifier
- `posting_date`: When the job was posted (DATE)
- `job_title`, `company_name`: Original text fields
- `job_description`: Full job description text
- `job_url`: Link to original posting
- `site`: Source website
- Salary: `min_salary`, `max_salary`, `salary_currency_id`, `salary_period_id`
- Experience: `experience_years` (INTEGER)
- Foreign keys to lookup tables (see below)

#### Lookup Tables (One-to-Many)
Normalized reference data tables:
- `titles` - Standardized job titles
- `companies` - Company names
- `cities`, `regions`, `countries` - Geographic data
- `job_functions` - Job categories (Engineering, Sales, etc.)
- `seniority_levels` - Junior, Mid, Senior, etc.
- `industries` - Industry sectors
- `departments` - Organizational departments
- `employment_types` - Full-time, Part-time, Contract
- `contract_types` - Permanent, Fixed-term, etc.
- `work_schedules` - Schedule patterns
- `remote_work_options` - On-site, Hybrid, Remote
- `company_sizes` - Small, Medium, Large, etc.
- `education_levels` - Required education

All lookup tables have:
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT) - The readable value

#### Skills & Benefits (Many-to-Many)
These tables use junction tables for many-to-many relationships:

**Skill Tables:**
- `hard_skills` - Technical skills (e.g., Python, JavaScript)
- `soft_skills` - Interpersonal skills (e.g., Communication, Leadership)
- Junction tables: `job_details_hard_skills`, `job_details_soft_skills`

**Other Many-to-Many:**
- `benefits` → `job_details_benefits`
- `certifications` → `job_details_certifications`
- `licenses` → `job_details_licenses`

All many-to-many tables use columns:
- `name` or `description` (TEXT) - The value
- Junction tables have: `job_details_id`, `{table}_id`

## Query Patterns

### Basic Aggregation
```sql
-- Count jobs by city
SELECT c.name, COUNT(*) as count
FROM job_details jd
JOIN cities c ON jd.city_id = c.id
GROUP BY c.name
ORDER BY count DESC
LIMIT 20
```

### Salary Analysis
```sql
-- Average salary by seniority level
SELECT 
    sl.name as seniority_level,
    COUNT(*) as job_count,
    ROUND(AVG(jd.min_salary)) as avg_min_salary,
    ROUND(AVG(jd.max_salary)) as avg_max_salary
FROM job_details jd
JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
WHERE jd.min_salary IS NOT NULL
GROUP BY sl.name
ORDER BY avg_max_salary DESC
```

### Many-to-Many Joins
```sql
-- Top skills with job counts
SELECT 
    hs.name as skill,
    COUNT(DISTINCT jd.id) as job_count,
    ROUND(COUNT(DISTINCT jd.id) * 100.0 / (SELECT COUNT(*) FROM job_details), 2) as percentage
FROM hard_skills hs
JOIN job_details_hard_skills jhs ON hs.id = jhs.hard_skills_id
JOIN job_details jd ON jhs.job_details_id = jd.id
GROUP BY hs.name
ORDER BY job_count DESC
LIMIT 20
```

### Time Series
```sql
-- Job postings over last 90 days
SELECT 
    DATE(posting_date) as date,
    COUNT(*) as job_count
FROM job_details
WHERE posting_date >= date('now', '-90 days')
GROUP BY DATE(posting_date)
ORDER BY date DESC
```

### Creating Buckets
```sql
-- Salary distribution in ranges
SELECT 
    CASE 
        WHEN min_salary < 10000 THEN '< 10k'
        WHEN min_salary < 20000 THEN '10k-20k'
        WHEN min_salary < 30000 THEN '20k-30k'
        WHEN min_salary < 40000 THEN '30k-40k'
        ELSE '40k+'
    END as salary_range,
    COUNT(*) as job_count
FROM job_details
WHERE min_salary IS NOT NULL
GROUP BY salary_range
```

## Best Practices

### Performance Tips
1. **LIMIT your results**: Use `LIMIT 10-20` for chart readability
2. **Use DISTINCT carefully**: When joining many-to-many, use `COUNT(DISTINCT jd.id)`
3. **Filter NULLs**: Add `WHERE field IS NOT NULL` for salary/experience analysis
4. **Index usage**: Lookup table JOINs are already indexed

### Query Writing Tips
1. **Readable names**: Always JOIN lookup tables to get readable names instead of IDs
2. **Meaningful aliases**: Use descriptive aliases (e.g., `job_count`, `avg_salary`)
3. **Percentages**: Calculate percentages using subqueries for context
4. **Order matters**: Sort results by the most important column (usually count or value)

### Chart Selection
- **Bar Chart**: Best for comparing discrete categories (skills, companies, cities)
- **Line Chart**: Ideal for time series data (trends over days/weeks/months)
- **Doughnut/Pie**: Good for showing proportional distributions (< 10 categories)

## Example Use Cases

### Market Insights
- Which skills are most in demand?
- How do salaries vary by location or seniority?
- Which companies are hiring the most?
- What's the distribution of remote vs on-site jobs?

### Career Planning
- What salary can I expect with X years of experience?
- Which skills should I learn to maximize salary?
- What benefits do companies typically offer?
- How do different industries compare in terms of opportunities?

### Trend Analysis
- Are job postings increasing or decreasing?
- Which skills are becoming more popular?
- How have salaries changed over time?
- Is remote work becoming more common?

## Tips for Custom Queries

1. **Start with predefined analyses**: They provide good examples and patterns
2. **Test incrementally**: Build your query step by step, testing each part
3. **Check data quality**: Look at a few raw rows first to understand the data
4. **Handle NULLs**: Many fields can be NULL, always check your WHERE conditions
5. **Save useful queries**: Use the "Save Query" button to keep your best analyses
6. **Document your queries**: Add meaningful names and descriptions

## SQL.js Differences from Regular SQLite

SQL.js is SQLite compiled to WebAssembly, so most SQLite features work. However:
- No persistent writes (database is read-only in browser)
- No server-side functions or extensions
- Date functions work but use SQLite syntax (not server-specific)
- Performance is good but not as fast as server-side SQLite

## Getting Help

### Database Structure
Click the "Database Structure & Query Help" collapsible section in the Analysis Builder page for:
- Complete table list
- Field descriptions
- Example queries
- Query patterns

### Troubleshooting
- **"No such table"**: Check table names in the database structure docs
- **"Ambiguous column"**: Use table aliases (e.g., `jd.id` instead of `id`)
- **No results**: Check your WHERE conditions and JOINs
- **Too many results**: Add a LIMIT clause

## Contributing Predefined Analyses

If you create a useful analysis, consider contributing it! The predefined analyses are defined in `/frontend/app.js` in the `PredefinedAnalyses` array. Each analysis needs:
- `name`: Short, descriptive title
- `description`: What insights it provides
- `sql`: The SQL query
- `chartType`: 'bar', 'line', 'doughnut', or 'pie'
- `category`: 'skills', 'salary', 'temporal', 'distribution', etc.
