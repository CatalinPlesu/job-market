# Advanced Analysis Features

## Overview

This document describes the advanced features added to the Custom Analysis Builder in response to user feedback.

## Features Added

### 1. AI Prompt Template (Copyable)

**Location**: Custom Query Builder header - "📋 Copy AI Prompt" button

**Purpose**: Provides users with a complete template to paste into AI tools (ChatGPT, Claude, etc.) for help writing queries.

**Contents**:
- Complete database structure (tables, columns, relationships)
- Query pattern examples (top items, salary stats, time series)
- Visualization setup instructions
- Data adapter function examples
- Custom Chart.js configuration examples

**Usage**:
1. Click "Copy AI Prompt" button
2. Paste into your AI assistant
3. Describe what you want to analyze
4. AI generates SQL query + optional configuration

### 2. Statistical Computations

**Location**: Results section - "📊 Statistical Analysis" (collapsible, open by default)

**Computed Statistics** (for each numeric column):
- **Count**: Number of non-null values
- **Mean**: Average value
- **Median**: Middle value (50th percentile)
- **Mode**: Most frequent value
- **Standard Deviation**: Measure of spread
- **Min/Max**: Range of values
- **Percentiles**: 25th, 50th, 75th, 90th, 95th, 99th

**Features**:
- Automatic detection of numeric columns
- Visual grid display of all statistics
- Toggle to enable/disable computations (Advanced Configuration)
- Useful for understanding data distributions

**Example Use Cases**:
- Analyze salary distributions (mean vs median shows skew)
- Identify outliers (compare max to 99th percentile)
- Understand market spread (std dev shows variability)

### 3. Extended Chart Types

**Previous**: 4 chart types (bar, line, doughnut, pie)

**Now**: 8 chart types
- **Bar**: Compare discrete categories
- **Line**: Show trends over time
- **Doughnut**: Proportional distributions
- **Pie**: Percentage breakdowns
- **Scatter**: X-Y relationships (NEW)
- **Bubble**: 3D data (x, y, size) (NEW)
- **Radar**: Multi-dimensional comparisons (NEW)
- **Polar Area**: Circular bar chart (NEW)

**Usage**: Select from dropdown in Custom Query Builder

### 4. Data Adapter Function

**Location**: Advanced Configuration → Data Adapter (JS Function)

**Purpose**: Transform query results before visualization

**Example**:
```javascript
// Input: [{name: "Python", count: 150}, {name: "JavaScript", count: 120}]
// Transform to different structure
return data.map(row => ({ 
    label: row.name, 
    value: row.count,
    color: row.count > 100 ? 'green' : 'blue'
}));
```

**Use Cases**:
- Rename columns for better chart labels
- Calculate derived values
- Filter or sort data
- Add computed fields

**Function Signature**:
- Parameter: `data` (array of query result objects)
- Return: transformed data array

### 5. Custom Chart Configuration

**Location**: Advanced Configuration → Custom Chart Config (JSON)

**Purpose**: Override auto-generated chart config with full Chart.js control

**Example**:
```json
{
  "type": "bar",
  "data": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [{
      "label": "Sales",
      "data": [10000, 15000, 20000, 18000],
      "backgroundColor": "rgba(99, 102, 241, 0.7)"
    }]
  },
  "options": {
    "scales": {
      "y": {
        "beginAtZero": true,
        "title": {
          "display": true,
          "text": "Revenue (MDL)"
        }
      }
    },
    "plugins": {
      "title": {
        "display": true,
        "text": "Quarterly Revenue"
      }
    }
  }
}
```

**Use Cases**:
- Custom colors and styling
- Multiple datasets on one chart
- Advanced Chart.js features (annotations, zoom, etc.)
- Precise control over axes, legends, tooltips

**Reference**: [Chart.js Documentation](https://www.chartjs.org/docs/latest/)

## Workflow Examples

### Example 1: Salary Distribution Analysis

**Goal**: Understand salary ranges with statistical insights

**Steps**:
1. Write SQL query:
```sql
SELECT min_salary
FROM job_details
WHERE min_salary IS NOT NULL
```

2. Enable statistics (checked by default)
3. Select chart type: "Bar" or "Line"
4. Execute query
5. View results:
   - Chart shows distribution
   - Statistics show mean, median, std dev
   - Percentiles reveal salary brackets

### Example 2: Custom Visualization with AI Help

**Goal**: Create complex analysis using AI

**Steps**:
1. Click "Copy AI Prompt"
2. Paste into ChatGPT/Claude
3. Request: "Create a query to show top 10 skills by average salary, with a bubble chart where bubble size = job count"
4. AI provides:
   - SQL query
   - Data adapter function
   - Custom chart config
5. Paste into Custom Query Builder
6. Execute and view results

### Example 3: Time Series with Percentiles

**Goal**: Track salary evolution with quartiles

**Steps**:
1. Query:
```sql
SELECT 
    DATE(posting_date) as date,
    AVG(min_salary) as avg_salary,
    MIN(min_salary) as min_salary,
    MAX(min_salary) as max_salary
FROM job_details
WHERE posting_date >= date('now', '-180 days')
  AND min_salary IS NOT NULL
GROUP BY DATE(posting_date)
ORDER BY date
```

2. Chart type: "Line"
3. Data adapter (optional):
```javascript
// Create multiple series for min/avg/max
return {
  labels: data.map(r => r.date),
  datasets: [
    { label: 'Average', data: data.map(r => r.avg_salary) },
    { label: 'Min', data: data.map(r => r.min_salary) },
    { label: 'Max', data: data.map(r => r.max_salary) }
  ]
};
```

4. View trend lines with range bands

## Advanced Configuration Section

**Visibility**: Collapsible section in Custom Query Builder

**Fields**:
1. **Data Adapter** (textarea)
   - JS function body
   - Receives `data` parameter
   - Returns transformed data

2. **Custom Chart Config** (textarea)
   - JSON configuration
   - Follows Chart.js schema
   - Overrides auto-generation

3. **Show Statistical Analysis** (toggle)
   - Enable/disable statistics computation
   - Checked by default
   - Affects all numeric columns

## Tips

### For Better Charts
- Limit query results (LIMIT 10-20) for readability
- Use descriptive column names (will appear in charts)
- Order by the metric you want to highlight

### For Statistics
- Query should return numeric columns
- NULL values are filtered out automatically
- Statistics computed per column independently

### Using AI
- Be specific about what you want to analyze
- Mention if you need custom colors/styling
- Ask for data adapter if transformation needed
- Request Chart.js config for advanced features

### Data Adapter Patterns
```javascript
// Filter data
return data.filter(row => row.count > 10);

// Sort data
return data.sort((a, b) => b.value - a.value);

// Add computed field
return data.map(row => ({
    ...row,
    percentage: (row.count / total) * 100
}));

// Group data
const grouped = {};
data.forEach(row => {
    if (!grouped[row.category]) grouped[row.category] = [];
    grouped[row.category].push(row);
});
return Object.entries(grouped);
```

## Technical Details

### Statistics Algorithm
- Uses standard statistical formulas
- Percentiles computed via linear interpolation
- Mode uses frequency counting
- All values rounded to 2 decimal places for display

### Chart Rendering
1. Check for custom config → use if valid JSON
2. Apply data adapter if provided
3. Auto-generate config from data structure
4. Create Chart.js instance
5. Destroy previous chart on re-render

### Error Handling
- Invalid SQL: Shows error message
- Invalid data adapter: Logs error, uses original data
- Invalid chart config: Falls back to auto-generation
- Empty results: No chart, shows message

## Future Enhancements

Potential additions:
- Export statistics as CSV
- Multiple chart types for same data
- Chart templates library
- Data adapter code examples
- Interactive chart editor
- Statistical tests (t-test, chi-square, etc.)
- Correlation analysis
- Distribution fitting

## Support

For questions or issues:
- Check AI prompt template for query examples
- Review Chart.js documentation for config options
- Test with simple queries first
- Use statistics to validate data quality
