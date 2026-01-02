# Box Plot and Multi-Column Chart Support

## Overview

This document describes the box plot and multi-column chart support added to address issues with statistical visualization and multi-column query plotting.

## Problems Addressed

### Problem 1: No Pure Statistical Representation
**Issue**: The system lacked a way to generate pure statistical visualizations like box-and-whisker plots that show quartiles, median, and distribution.

**Solution**: Added Box & Whisker Plot chart type that automatically computes and displays:
- Minimum value
- 1st Quartile (Q1, 25th percentile)
- Median (Q2, 50th percentile)
- 3rd Quartile (Q3, 75th percentile)
- Maximum value
- Outliers (when applicable)

### Problem 2: Multi-Column Queries Plot Wrong Data
**Issue**: When SQL queries returned multiple columns, only the first numeric column was plotted, which could be the wrong data.

**Solution**: Implemented column selection UI that allows users to:
- Choose which column to use for labels (X-axis)
- Select which column(s) to use for values (Y-axis)
- Plot multiple value columns as separate series on the same chart

## New Features

### 1. Box & Whisker Plot Chart Type

**Location**: Chart Type dropdown → "Box & Whisker Plot (Statistical)"

**Purpose**: Pure statistical visualization showing data distribution

**How It Works**:
- Automatically computes quartiles for all numeric columns
- Displays box (Q1 to Q3) with median line
- Shows whiskers (min to max)
- Each numeric column gets its own box plot for comparison

**Example Query**:
```sql
-- Compare salary distributions across industries
SELECT 
    i.name as industry,
    jd.min_salary,
    jd.max_salary
FROM job_details jd
JOIN industries i ON jd.industry_id = i.id
WHERE jd.min_salary IS NOT NULL
```

**Chart Type**: Select "Box & Whisker Plot (Statistical)"

**Result**: Shows box plots comparing min_salary and max_salary distributions

### 2. Column Selection UI

**Location**: Appears below Chart Type after query execution

**Components**:

#### Label Column Selector
- **Purpose**: Choose which column to use for X-axis labels
- **Default**: Auto-detects first string column
- **Options**: All columns from query results
- **Setting**: "Auto-detect" or select specific column

#### Value Column(s) Selector
- **Purpose**: Choose which numeric column(s) to plot on Y-axis
- **Default**: Auto-detects all numeric columns (except 'id')
- **Options**: All columns from query results
- **Multi-Select**: Hold Ctrl/Cmd to select multiple
- **Setting**: Leave empty for auto-detect, or select 1+ columns

### 3. Multi-Series Charts

**What It Does**: When multiple value columns are selected, creates a chart with multiple data series

**Example**:
```sql
SELECT 
    sl.name as seniority,
    AVG(jd.min_salary) as avg_min,
    AVG(jd.max_salary) as avg_max,
    COUNT(*) as job_count
FROM job_details jd
JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
WHERE jd.min_salary IS NOT NULL
GROUP BY sl.name
```

**Column Selection**:
- Label Column: seniority
- Value Columns: avg_min, avg_max, job_count (select all 3)

**Result**: Bar/Line chart with 3 series showing all metrics together

### 4. Improved Auto-Detection

**Previous Behavior**:
- Found first non-numeric column for labels
- Found first numeric column for values
- Ignored other columns

**New Behavior**:
- Finds first string column for labels (or first column if none)
- Finds ALL numeric columns for values (except 'id')
- Allows manual override via column selectors
- Better handling of edge cases

## Usage Examples

### Example 1: Salary Distribution Box Plot

**Goal**: Visualize salary distribution with quartiles

**Query**:
```sql
SELECT min_salary
FROM job_details
WHERE min_salary IS NOT NULL
LIMIT 1000
```

**Steps**:
1. Execute query
2. Select "Box & Whisker Plot (Statistical)"
3. View distribution with quartiles, median, outliers

### Example 2: Compare Multiple Metrics

**Goal**: Compare min and max salaries across seniority levels

**Query**:
```sql
SELECT 
    sl.name as level,
    AVG(jd.min_salary) as avg_min_salary,
    AVG(jd.max_salary) as avg_max_salary
FROM job_details jd
JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
WHERE jd.min_salary IS NOT NULL
GROUP BY sl.name
ORDER BY avg_max_salary DESC
```

**Steps**:
1. Execute query
2. Column Selection appears
3. Label Column: level (already selected)
4. Value Columns: Select both avg_min_salary and avg_max_salary
5. Chart Type: Bar or Line
6. View dual-series chart comparing min and max

### Example 3: Industry Salary Box Plots

**Goal**: Compare salary distributions across industries

**Query**:
```sql
SELECT 
    i.name as industry,
    jd.min_salary
FROM job_details jd
JOIN industries i ON jd.industry_id = i.id
WHERE jd.min_salary IS NOT NULL
ORDER BY jd.min_salary DESC
LIMIT 500
```

**Steps**:
1. Execute query
2. Chart Type: Box & Whisker Plot
3. Each industry gets a box showing salary distribution
4. Compare medians and ranges visually

### Example 4: Time Series with Multiple Metrics

**Goal**: Track job postings and companies over time

**Query**:
```sql
SELECT 
    DATE(posting_date) as date,
    COUNT(*) as job_count,
    COUNT(DISTINCT company_name_id) as company_count
FROM job_details
WHERE posting_date >= date('now', '-90 days')
GROUP BY DATE(posting_date)
ORDER BY date
```

**Steps**:
1. Execute query
2. Label Column: date
3. Value Columns: Select both job_count and company_count
4. Chart Type: Line
5. View dual-line chart showing both metrics over time

## Technical Details

### Box Plot Implementation

**Library**: chartjs-chart-boxplot v4.2.5 (via CDN)

**Data Structure**:
```javascript
{
  x: 'column_name',
  min: minimum_value,
  q1: 25th_percentile,
  median: 50th_percentile,
  q3: 75th_percentile,
  max: maximum_value,
  outliers: []
}
```

**Computation**:
- Values sorted numerically
- Percentiles calculated via linear interpolation
- Each numeric column becomes a separate box

### Column Selection Storage

**State Management**:
- `labelColumn`: String or null (null = auto-detect)
- `valueColumns`: Array of strings (empty = auto-detect)
- Stored in `CustomAnalysisState.currentQuery`

**Persistence**:
- Saved with query when using "Save Query"
- Restored when loading saved query
- Persists across page refreshes via localStorage

### Auto-Detection Algorithm

**Label Column**:
1. Use manually selected column if set
2. Else find first string column
3. Else use first column

**Value Columns**:
1. Use manually selected columns if set
2. Else find all numeric columns
3. Exclude 'id' column
4. Exclude label column
5. If none found, use second column

## Tips

### When to Use Box Plots
- Comparing distributions across categories
- Showing salary ranges with quartiles
- Identifying outliers in data
- Statistical analysis of continuous variables

### When to Use Multi-Series Charts
- Comparing related metrics (min vs max)
- Time series with multiple trends
- Before/after comparisons
- Multiple dimensions of same category

### Column Selection Best Practices
- Leave on "Auto-detect" for simple queries
- Manually select when query has many columns
- Select multiple value columns for comparison
- Use descriptive column names in SQL (AS clause)

### Query Design for Box Plots
- Return raw values, not aggregates
- Include enough data points (50+ recommended)
- Filter outliers in SQL if needed
- Group by category for comparison

### Query Design for Multi-Series
- Use consistent units for value columns
- Name columns descriptively
- Order by most important metric
- Limit results for readability

## Limitations

### Box Plot Limitations
- Requires Chart.js boxplot plugin (included via CDN)
- Best with 50+ data points per category
- May be slow with very large datasets (>10k rows)
- Outliers not currently shown (can be added)

### Column Selection Limitations
- Manual selection required after each query execution
- Not saved as part of query initially (must re-save)
- Multi-select UI may be unfamiliar to some users
- No column type validation (can select non-numeric for values)

## Future Enhancements

Potential improvements:
- Violin plots (distribution shape visualization)
- Histogram with configurable bins
- Outlier detection and highlighting
- Statistical test results (t-test, ANOVA)
- Save column selections with queries automatically
- Column type indicators in selectors
- Preview of selected columns
- Drag-and-drop column mapping
- Multiple chart views for same query

## Troubleshooting

### Box Plot Not Showing
- **Issue**: Chart appears empty
- **Fix**: Ensure query returns numeric values, not aggregates
- **Example**: Use `SELECT salary` not `SELECT AVG(salary)`

### Wrong Data Being Plotted
- **Issue**: Chart shows unexpected columns
- **Fix**: Use Column Selection UI to manually choose columns
- **Tip**: Check "Auto-detect" is selecting correct columns

### Multi-Select Not Working
- **Issue**: Can only select one value column
- **Fix**: Hold Ctrl (Windows/Linux) or Cmd (Mac) while clicking
- **Alternative**: Click first item, then Shift+Click last item for range

### Box Plot Shows Flat Lines
- **Issue**: All quartiles are the same value
- **Fix**: Data has no variance (all values identical)
- **Solution**: Check data quality or add WHERE clauses to filter

## References

- [Chart.js Documentation](https://www.chartjs.org/)
- [Chart.js Box Plot Plugin](https://github.com/sgratzl/chartjs-chart-boxplot)
- [Box Plot Explanation](https://en.wikipedia.org/wiki/Box_plot)
- [SQL Query Optimization](https://www.sqlite.org/optoverview.html)
