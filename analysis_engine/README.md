# Analysis Engine

Statistical analysis and trend computation for job market data.

## Overview

The analysis engine computes ~20 meaningful statistics and trends from job market data, supporting both static snapshots and time-series analysis.

## Features

- **Static Analyses**: Current market snapshots (salary distributions, skill demand, etc.)
- **Temporal Analyses**: Trends over time (salary evolution, posting volume, etc.)
- **Hierarchy Analysis**: Drill-down from job functions to specializations to seniority levels
- **Graceful Error Handling**: Handles missing data without crashes
- **JSON Export**: All results exported as JSON files for frontend consumption

## Usage

### Command Line

```bash
# Generate all analyses with defaults
python -m analysis_engine --output pages/api/analysis

# Customize parameters
python -m analysis_engine \
    --output /path/to/output \
    --granularity monthly \
    --min-sample-size 10 \
    --top-n-skills 20 \
    --top-n-companies 50
```

### Python API

```python
from analysis_engine.generator import AnalysisGenerator
from analysis_engine.config import AnalysisConfig

# Configure
config = AnalysisConfig()
config.GRANULARITY = 'monthly'
config.MIN_SAMPLE_SIZE = 10

# Generate
generator = AnalysisGenerator('pages/api/analysis', config)
generator.generate_all()
```

## Analyses Generated

### Static Analyses (14)

1. **salary-overview.json** - Overall salary statistics
2. **salary-by-function.json** - Salary by job function
3. **salary-by-seniority.json** - Salary by seniority level
4. **salary-by-location.json** - Salary by location (city)
5. **salary-by-company-size.json** - Salary by company size
6. **salary-by-education.json** - Salary by education level
7. **skills-demand.json** - Top in-demand skills
8. **skills-salary.json** - Skills to salary correlation
9. **skill-combinations.json** - Common skill combinations
10. **employment-types.json** - Employment types distribution
11. **remote-work.json** - Remote work availability
12. **benefits.json** - Most common benefits
13. **requirements.json** - Job requirements overview
14. **top-companies.json** - Top hiring companies

### Temporal Analyses (6)

15. **posting-trends.json** - Job posting volume trends
16. **salary-trends.json** - Salary evolution over time
17. **skills-trends.json** - Skills demand trends
18. **remote-work-trends.json** - Remote work adoption trends
19. **job-duration.json** - Job duration analysis (time to fill)
20. **market-health.json** - Market health indicators

### Hierarchy Analysis (1)

21. **salary-by-hierarchy.json** - Salary by job hierarchy (drill-down)

## Output Structure

All analyses produce JSON files with the following structure:

```json
{
  "version": "1.0",
  "analysis_id": "salary-overview",
  "title": "Overall Salary Analysis",
  "generated_at": "2026-01-01T12:00:00Z",
  "type": "static",
  "data": {
    // Analysis-specific data
  },
  "visualization_hints": {
    "chart_types": ["histogram", "box_plot"],
    "recommended_chart": "histogram"
  }
}
```

The `index.json` file lists all available analyses:

```json
{
  "version": "1.0",
  "generated_at": "2026-01-01T12:00:00Z",
  "total_analyses": 21,
  "analyses": [
    {
      "id": "salary-overview",
      "title": "Overall Salary Analysis",
      "type": "static",
      "file": "salary-overview.json"
    },
    // ... more analyses
  ]
}
```

## Configuration

The `AnalysisConfig` class provides configuration options:

```python
class AnalysisConfig:
    # Temporal settings
    GRANULARITY = 'monthly'  # daily, weekly, monthly
    MIN_DATA_POINTS = 3  # Minimum periods for trend analysis
    
    # Aggregation thresholds
    MIN_SAMPLE_SIZE = 10  # Minimum jobs for category analysis
    TOP_N_SKILLS = 20
    TOP_N_COMPANIES = 50
    
    # Hierarchy levels
    HIERARCHY = ['job_function', 'specialization', 'seniority_level']
    
    # Outlier detection
    SALARY_OUTLIER_THRESHOLD = 3.0  # Standard deviations
```

## Database Requirements

The analysis engine requires access to two databases:

1. **scrape.db** - Raw scraped data
   - `jobs` table - Job records with timestamps
   - `job_checks` table - Status checks for temporal analysis

2. **data.db** - LLM-processed data
   - `job_details` table - Structured job information
   - Lookup tables (job_functions, seniority_levels, etc.)
   - Association tables (job_hard_skills, job_benefits, etc.)

## Performance

- Handles 10,000+ jobs efficiently
- Generation completes in <5 minutes for typical datasets
- Outlier detection prevents skewed results
- Gracefully handles missing data

## Error Handling

The engine handles various error conditions:

- **Insufficient data**: Returns error with count
- **Missing fields**: Skips null values gracefully
- **Database errors**: Logs and continues with other analyses
- **Individual analysis failures**: Don't stop entire generation

## Architecture

```
analysis_engine/
├── __init__.py           # Module initialization
├── __main__.py           # CLI entry point
├── config.py             # Configuration
├── base.py               # Base analysis class
├── aggregator.py         # Common utilities
├── generator.py          # Main orchestrator
├── hierarchy.py          # Hierarchy analysis
├── static/               # Static analyses
│   ├── salary.py         # Salary analyses
│   ├── skills.py         # Skills analyses
│   ├── employment.py     # Employment analyses
│   └── companies.py      # Company analyses
└── temporal/             # Temporal analyses
    ├── posting_trends.py
    ├── salary_trends.py
    ├── skills_trends.py
    ├── remote_trends.py
    └── market_health.py
```

## Development

### Adding New Analyses

1. Create analysis class extending `BaseAnalysis`
2. Implement required properties and `compute()` method
3. Add to `generator.py` analyses list
4. Test with sample data

Example:

```python
from analysis_engine.base import BaseAnalysis

class MyAnalysis(BaseAnalysis):
    @property
    def analysis_id(self):
        return 'my-analysis'
    
    @property
    def title(self):
        return 'My Analysis Title'
    
    def compute(self):
        # Your analysis logic
        return {'data': 'result'}
```

### Testing

```bash
# Test with local databases
python -m analysis_engine --output /tmp/test-output

# Verify JSON structure
cat /tmp/test-output/index.json
cat /tmp/test-output/salary-overview.json
```

## Dependencies

- SQLAlchemy (database access)
- Python 3.12+
- Standard library (json, collections, statistics, datetime)

## References

- **Specification**: `planning/github-pages-pseudo-api/05-analysis-system.md`
- **Requirements**: `ANALYTICS_SPEC.md`
- **Database models**: `src/scrape_database.py`, `src/data_database.py`
