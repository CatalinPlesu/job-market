# Analysis System Specification

## Document Purpose
This specification defines the analysis engine that computes ~20 meaningful statistics and trends from job market data, supporting both static snapshots and temporal analysis across the job hierarchy.

## System Responsibilities

### Core Functions
1. Compute static analyses (current market snapshot)
2. Generate temporal analyses (trends over time)
3. Support dynamic hierarchy analysis (domain → specialization → seniority)
4. Aggregate data efficiently for visualization
5. Handle missing data gracefully
6. Export analysis results as JSON

### Out of Scope
- Database schema modifications
- Data visualization (handled by frontend)
- Real-time analysis (batch processing only)
- Predictive modeling (future enhancement)

## Input Requirements

### Database Access
**Tables from `data.db`:**
- `job_details` - Main job information with timestamps
- All lookup tables (job_functions, seniority_levels, etc.)
- Relationship tables (job_hard_skills, job_soft_skills, etc.)

**Tables from `scrape.db`:**
- `jobs` - Original job records with created_at, updated_at
- `job_checks` - Status checks to determine when jobs closed

**Critical Timestamp Fields:**
- `jobs.created_at` - When job first scraped (for posting trends)
- `jobs.updated_at` - Last update (for activity tracking)
- `job_checks.check_date` - When job status checked
- `job_checks.http_status` - 200 = alive, 404 = dead
- `job_details.posting_date` - Original posting date from ad
- `job_details.processed_at` - When LLM processed the job

### Configuration
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
    
    # Cache settings
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # seconds
```

## Proposed Analyses (~20 Categories)

### Static Analyses (Snapshot)

#### 1. Overall Salary Overview
- **Metrics:** Count, average, median, min, max, percentiles (25th, 75th)
- **Breakdown:** By currency, by period (hourly/monthly/yearly)
- **Distribution:** Salary ranges with counts
- **Output:** `/api/analysis/salary-overview.json`

#### 2. Salary by Job Function
- **Metrics:** Average, median salary per function
- **Ranking:** Top 10 highest-paying functions
- **Sample sizes:** Number of jobs per function
- **Output:** `/api/analysis/salary-by-function.json`

#### 3. Salary by Seniority Level
- **Metrics:** Average salary progression (entry → executive)
- **Comparison:** Overlay multiple functions
- **Growth rate:** % increase between levels
- **Output:** `/api/analysis/salary-by-seniority.json`

#### 4. Salary by Location
- **Metrics:** Average salary by city/region
- **Comparison:** Urban vs rural
- **Cost-of-living adjusted (future)**
- **Output:** `/api/analysis/salary-by-location.json`

#### 5. Salary by Company Size
- **Metrics:** Average compensation by company size
- **Comparison:** Startup → Enterprise
- **Output:** `/api/analysis/salary-by-company-size.json`

#### 6. Salary by Education Level
- **Metrics:** ROI of education
- **Correlation:** Education level vs salary
- **Output:** `/api/analysis/salary-by-education.json`

#### 7. Top In-Demand Skills
- **Metrics:** Top 20 skills by frequency
- **Breakdown:** By job function, by seniority
- **Growth rate:** Skill popularity change
- **Output:** `/api/analysis/skills-demand.json`

#### 8. Skills to Salary Correlation
- **Metrics:** Average salary for jobs requiring each skill
- **Ranking:** Highest-value skills
- **Visualization hint:** Bubble chart (frequency vs salary)
- **Output:** `/api/analysis/skills-salary.json`

#### 9. Skill Combinations
- **Metrics:** Common skill pairs/triplets
- **Salary impact:** Does combining skills increase pay?
- **Visualization hint:** Network graph
- **Output:** `/api/analysis/skill-combinations.json`

#### 10. Employment Types Distribution
- **Metrics:** Full-time, part-time, contract, etc.
- **Breakdown:** By job function, industry
- **Output:** `/api/analysis/employment-types.json`

#### 11. Remote Work Availability
- **Metrics:** % remote, hybrid, on-site
- **Breakdown:** By job function, seniority, company size
- **Output:** `/api/analysis/remote-work.json`

#### 12. Benefits Analysis
- **Metrics:** Most common benefits by frequency
- **Breakdown:** By company size, industry
- **Salary correlation:** Do higher salaries offer more benefits?
- **Output:** `/api/analysis/benefits.json`

#### 13. Job Requirements Overview
- **Metrics:** Education, experience, certifications required
- **Distribution:** Years of experience required
- **Language requirements:** Most common languages
- **Output:** `/api/analysis/requirements.json`

#### 14. Top Hiring Companies
- **Metrics:** Companies with most active postings
- **Growth indicators:** Rapidly expanding companies
- **Output:** `/api/analysis/top-companies.json`

### Temporal Analyses (Trends)

#### 15. Job Posting Volume Trends
- **Metrics:** New jobs posted per period
- **Breakdown:** By job function, location, industry
- **Indicators:** Market heating/cooling
- **Output:** `/api/analysis/posting-trends.json`

#### 16. Salary Evolution Over Time
- **Metrics:** Average/median salary by period
- **Breakdown:** By job function, seniority
- **Growth rate:** % change period-over-period
- **Output:** `/api/analysis/salary-trends.json`

#### 17. Skills Demand Trends
- **Metrics:** Skill frequency over time
- **Emerging skills:** Rapid growth (>50% QoQ)
- **Declining skills:** Rapid decline (<-20% QoQ)
- **Output:** `/api/analysis/skills-trends.json`

#### 18. Remote Work Adoption Trends
- **Metrics:** % remote work over time
- **Breakdown:** By industry, job function
- **Acceleration:** Rate of change
- **Output:** `/api/analysis/remote-work-trends.json`

#### 19. Job Duration Analysis (Time to Fill)
- **Metrics:** Average days jobs stay open
- **Breakdown:** By function, seniority, salary range
- **Unfillable positions:** Jobs open >90 days
- **Output:** `/api/analysis/job-duration.json`

#### 20. Market Health Indicators
- **Metrics:** Active vs expired jobs ratio
- **Velocity:** New postings vs closures
- **Growth rate:** Net job growth
- **Seasonality:** Monthly patterns
- **Output:** `/api/analysis/market-health.json`

### Dynamic Hierarchy Analysis

#### 21. Salary by Hierarchy
- **Structure:** Job Function → Specialization → Seniority
- **Drill-down:** Compute at each level dynamically
- **Metrics:** Count, average, median at each node
- **Output:** `/api/analysis/salary-by-hierarchy.json`

## Implementation Approach

### Module Structure
```
json_generator/analysis/
├── __init__.py
├── base.py                 # Base analysis class
├── static/
│   ├── __init__.py
│   ├── salary.py           # Salary analyses (#1-6)
│   ├── skills.py           # Skills analyses (#7-9)
│   ├── employment.py       # Employment & benefits (#10-13)
│   └── companies.py        # Company analyses (#14)
├── temporal/
│   ├── __init__.py
│   ├── posting_trends.py   # Posting volume trends (#15)
│   ├── salary_trends.py    # Salary evolution (#16)
│   ├── skills_trends.py    # Skills demand trends (#17)
│   ├── remote_trends.py    # Remote work trends (#18)
│   └── market_health.py    # Market indicators (#19-20)
├── hierarchy.py            # Dynamic hierarchy analysis (#21)
└── aggregator.py           # Common aggregation utilities
```

### Base Analysis Class

```python
# json_generator/analysis/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class BaseAnalysis(ABC):
    """Base class for all analyses."""
    
    def __init__(self, db_session, config):
        self.db = db_session
        self.config = config
        self.generated_at = datetime.utcnow()
    
    @property
    @abstractmethod
    def analysis_id(self) -> str:
        """Unique identifier for this analysis."""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Human-readable title."""
        pass
    
    @property
    def is_temporal(self) -> bool:
        """Whether this analysis includes time series data."""
        return False
    
    @abstractmethod
    def compute(self) -> Dict[str, Any]:
        """
        Compute the analysis.
        Returns: Dictionary with analysis results.
        """
        pass
    
    def to_json(self) -> Dict[str, Any]:
        """
        Convert analysis to JSON format.
        Includes metadata and results.
        """
        data = self.compute()
        
        return {
            'version': '1.0',
            'analysis_id': self.analysis_id,
            'generated_at': self.generated_at.isoformat() + 'Z',
            'type': 'temporal' if self.is_temporal else 'static',
            'data': data,
            'visualization_hints': self.get_visualization_hints()
        }
    
    def get_visualization_hints(self) -> Dict[str, Any]:
        """
        Suggest visualization approaches for frontend.
        Override in subclasses for custom hints.
        """
        return {
            'chart_types': ['table'],
            'recommended_chart': 'table'
        }
```

### Example: Salary Overview Analysis

```python
# json_generator/analysis/static/salary.py

from ..base import BaseAnalysis
from sqlalchemy import func
from statistics import median, quantiles

class SalaryOverviewAnalysis(BaseAnalysis):
    
    @property
    def analysis_id(self):
        return 'salary-overview'
    
    @property
    def title(self):
        return 'Overall Salary Analysis'
    
    def compute(self):
        # Query jobs with salary data
        jobs = self.db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data'}
        
        # Overall statistics
        salaries = [
            (job.min_salary + job.max_salary) / 2 
            if job.max_salary else job.min_salary
            for job in jobs
        ]
        
        overall = {
            'count': len(salaries),
            'average': sum(salaries) / len(salaries),
            'median': median(salaries),
            'min': min(salaries),
            'max': max(salaries),
            'currency': 'MDL',  # Assuming normalized to MDL
            'period': 'month'
        }
        
        # By currency
        by_currency = self._aggregate_by_currency(jobs)
        
        # Distribution
        distribution = self._compute_distribution(salaries)
        
        return {
            'overall': overall,
            'by_currency': by_currency,
            'distribution': distribution
        }
    
    def _aggregate_by_currency(self, jobs):
        """Group by currency and compute stats."""
        from collections import defaultdict
        
        currency_groups = defaultdict(list)
        for job in jobs:
            currency = job.salary_currency.code if job.salary_currency else 'MDL'
            avg_salary = (
                (job.min_salary + job.max_salary) / 2 
                if job.max_salary else job.min_salary
            )
            currency_groups[currency].append(avg_salary)
        
        result = []
        for currency, salaries in currency_groups.items():
            if len(salaries) >= self.config.MIN_SAMPLE_SIZE:
                q = quantiles(salaries, n=4)  # Quartiles
                result.append({
                    'currency': currency,
                    'count': len(salaries),
                    'average': sum(salaries) / len(salaries),
                    'median': median(salaries),
                    'percentile_25': q[0],
                    'percentile_75': q[2]
                })
        
        return result
    
    def _compute_distribution(self, salaries):
        """Compute salary distribution in ranges."""
        ranges = [
            (0, 10000),
            (10000, 20000),
            (20000, 30000),
            (30000, 50000),
            (50000, float('inf'))
        ]
        
        distribution = []
        total = len(salaries)
        
        for min_val, max_val in ranges:
            count = sum(1 for s in salaries if min_val <= s < max_val)
            if count > 0:
                distribution.append({
                    'range': f'{min_val}-{max_val}' if max_val != float('inf') else f'{min_val}+',
                    'count': count,
                    'percentage': (count / total) * 100
                })
        
        return distribution
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['histogram', 'box_plot', 'bar_chart'],
            'recommended_chart': 'histogram'
        }
```

### Example: Job Posting Trends (Temporal)

```python
# json_generator/analysis/temporal/posting_trends.py

from ..base import BaseAnalysis
from datetime import datetime, timedelta
from collections import defaultdict

class PostingTrendsAnalysis(BaseAnalysis):
    
    @property
    def analysis_id(self):
        return 'posting-trends'
    
    @property
    def title(self):
        return 'Job Posting Volume Over Time'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        granularity = self.config.GRANULARITY
        
        # Get all jobs with creation dates
        jobs = self.db.query(Job).all()
        
        # Bucket by time period
        periods = self._bucket_by_period(jobs, granularity)
        
        # Compute statistics per period
        trend_data = []
        for period, period_jobs in sorted(periods.items()):
            new_jobs = len(period_jobs)
            closed_jobs = self._count_closed_in_period(period_jobs, period)
            active_jobs = new_jobs - closed_jobs
            
            trend_data.append({
                'date': period,
                'count': active_jobs,
                'new': new_jobs,
                'closed': closed_jobs
            })
        
        return {
            'granularity': granularity,
            'job_posting_volume': trend_data
        }
    
    def _bucket_by_period(self, jobs, granularity):
        """Group jobs by time period."""
        periods = defaultdict(list)
        
        for job in jobs:
            if not job.created_at:
                continue
            
            period_key = self._get_period_key(job.created_at, granularity)
            periods[period_key].append(job)
        
        return periods
    
    def _get_period_key(self, dt, granularity):
        """Convert datetime to period key."""
        if granularity == 'monthly':
            return dt.strftime('%Y-%m')
        elif granularity == 'weekly':
            return dt.strftime('%Y-W%U')
        else:  # daily
            return dt.strftime('%Y-%m-%d')
    
    def _count_closed_in_period(self, jobs, period):
        """Count how many jobs closed in this period."""
        count = 0
        for job in jobs:
            # Check job_checks to find when job died
            latest_check = max(job.checks, key=lambda c: c.check_date, default=None)
            if latest_check and latest_check.http_status != 200:
                check_period = self._get_period_key(
                    latest_check.check_date, 
                    self.config.GRANULARITY
                )
                if check_period == period:
                    count += 1
        
        return count
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['line_chart', 'area_chart'],
            'recommended_chart': 'line_chart'
        }
```

### Example: Dynamic Hierarchy Analysis

```python
# json_generator/analysis/hierarchy.py

from .base import BaseAnalysis
from collections import defaultdict
from statistics import median

class SalaryHierarchyAnalysis(BaseAnalysis):
    
    @property
    def analysis_id(self):
        return 'salary-by-hierarchy'
    
    @property
    def title(self):
        return 'Salary Analysis by Job Hierarchy'
    
    def compute(self):
        jobs = self.db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None)
        ).all()
        
        levels = self.config.HIERARCHY  # ['job_function', 'specialization', 'seniority_level']
        
        tree = self._build_hierarchy_tree(jobs, levels)
        
        return {
            'hierarchy_levels': levels,
            'job_function': tree
        }
    
    def _build_hierarchy_tree(self, jobs, levels, current_level=0):
        """Recursively build hierarchy tree with salary stats."""
        if current_level >= len(levels):
            return None
        
        level_field = levels[current_level]
        grouped = self._group_by_field(jobs, level_field)
        
        result = []
        for value, value_jobs in grouped.items():
            if not value or len(value_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            node = {
                'name': value,
                'count': len(value_jobs),
                'average_salary': self._compute_average_salary(value_jobs),
                'median_salary': self._compute_median_salary(value_jobs),
                'salary_range': {
                    'min': self._compute_min_salary(value_jobs),
                    'max': self._compute_max_salary(value_jobs)
                }
            }
            
            # Recurse to next level
            if current_level < len(levels) - 1:
                next_level_key = levels[current_level + 1] + 's'  # pluralize
                subtree = self._build_hierarchy_tree(
                    value_jobs, 
                    levels, 
                    current_level + 1
                )
                if subtree:
                    node[next_level_key] = subtree
            
            result.append(node)
        
        return result
    
    def _group_by_field(self, jobs, field):
        """Group jobs by a field (job_function, specialization, etc.)."""
        grouped = defaultdict(list)
        
        for job in jobs:
            value = self._get_field_value(job, field)
            if value:
                grouped[value].append(job)
        
        return grouped
    
    def _get_field_value(self, job, field):
        """Get the value of a field from job, handling foreign keys."""
        # Handle foreign key relationships
        if field == 'job_function':
            return job.job_function.name if job.job_function else None
        elif field == 'specialization':
            return job.specialization.name if job.specialization else None
        elif field == 'seniority_level':
            return job.seniority_level.name if job.seniority_level else None
        return getattr(job, field, None)
    
    def _compute_average_salary(self, jobs):
        """Compute average salary from jobs."""
        salaries = [
            (job.min_salary + job.max_salary) / 2 
            if job.max_salary else job.min_salary
            for job in jobs if job.min_salary
        ]
        return sum(salaries) / len(salaries) if salaries else None
    
    def _compute_median_salary(self, jobs):
        """Compute median salary from jobs."""
        salaries = [
            (job.min_salary + job.max_salary) / 2 
            if job.max_salary else job.min_salary
            for job in jobs if job.min_salary
        ]
        return median(salaries) if salaries else None
    
    def _compute_min_salary(self, jobs):
        """Compute minimum salary from jobs."""
        salaries = [job.min_salary for job in jobs if job.min_salary]
        return min(salaries) if salaries else None
    
    def _compute_max_salary(self, jobs):
        """Compute maximum salary from jobs."""
        salaries = [job.max_salary for job in jobs if job.max_salary]
        return max(salaries) if salaries else None
```

### Aggregation Utilities

```python
# json_generator/analysis/aggregator.py

from collections import defaultdict
from statistics import mean, median
from typing import List, Dict, Any

class Aggregator:
    """Common aggregation utilities for analyses."""
    
    @staticmethod
    def group_by(items, key_func):
        """Group items by a key function."""
        groups = defaultdict(list)
        for item in items:
            key = key_func(item)
            if key:
                groups[key].append(item)
        return dict(groups)
    
    @staticmethod
    def compute_stats(values: List[float]) -> Dict[str, float]:
        """Compute common statistics for a list of values."""
        if not values:
            return {}
        
        return {
            'count': len(values),
            'sum': sum(values),
            'average': mean(values),
            'median': median(values),
            'min': min(values),
            'max': max(values)
        }
    
    @staticmethod
    def remove_outliers(values: List[float], threshold: float = 3.0) -> List[float]:
        """Remove outliers using z-score method."""
        if len(values) < 3:
            return values
        
        avg = mean(values)
        std = (sum((x - avg) ** 2 for x in values) / len(values)) ** 0.5
        
        if std == 0:
            return values
        
        return [
            v for v in values 
            if abs((v - avg) / std) <= threshold
        ]
    
    @staticmethod
    def bucket_by_range(values: List[float], ranges: List[tuple]) -> Dict[str, int]:
        """Bucket values into ranges."""
        buckets = {}
        
        for min_val, max_val in ranges:
            label = f'{min_val}-{max_val}' if max_val != float('inf') else f'{min_val}+'
            buckets[label] = sum(1 for v in values if min_val <= v < max_val)
        
        return buckets
```

## Testing Strategy

### Unit Tests
```python
# tests/test_analysis_salary.py

import pytest
from json_generator.analysis.static.salary import SalaryOverviewAnalysis

def test_salary_overview_basic():
    # Create test data
    jobs = [
        create_job(min_salary=10000, max_salary=15000),
        create_job(min_salary=12000, max_salary=18000),
        create_job(min_salary=20000, max_salary=25000),
    ]
    
    analysis = SalaryOverviewAnalysis(mock_db, config)
    result = analysis.compute()
    
    assert result['overall']['count'] == 3
    assert 'average' in result['overall']
    assert 'median' in result['overall']

def test_insufficient_data():
    jobs = [create_job(min_salary=10000)]
    
    analysis = SalaryOverviewAnalysis(mock_db, config)
    result = analysis.compute()
    
    assert 'error' in result
```

### Integration Tests
```python
# tests/test_analysis_integration.py

def test_all_analyses_generate_valid_json():
    """Ensure all analyses produce valid JSON."""
    analyses = [
        SalaryOverviewAnalysis,
        PostingTrendsAnalysis,
        SkillsDemandAnalysis,
        # ... all analyses
    ]
    
    for AnalysisClass in analyses:
        analysis = AnalysisClass(db_session, config)
        result = analysis.to_json()
        
        assert 'version' in result
        assert 'analysis_id' in result
        assert 'data' in result
        
        # Validate JSON serialization
        import json
        json_str = json.dumps(result)
        assert json_str  # Can be serialized
```

## Performance Considerations

### Optimization Strategies

1. **Database Query Optimization**
```python
# Eager load relationships
jobs = db.query(JobDetail).options(
    joinedload(JobDetail.job_function),
    joinedload(JobDetail.seniority_level),
    joinedload(JobDetail.specialization)
).all()
```

2. **Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_salary_stats_cached(cache_key):
    # Expensive computation
    pass
```

3. **Parallel Processing**
```python
from concurrent.futures import ThreadPoolExecutor

def generate_all_analyses(db_session, config):
    """Generate all analyses in parallel."""
    analyses = [
        SalaryOverviewAnalysis(db_session, config),
        PostingTrendsAnalysis(db_session, config),
        # ... all analyses
    ]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(a.to_json) for a in analyses]
        results = [f.result() for f in futures]
    
    return results
```

## Success Criteria

- [ ] All 20+ analyses implemented
- [ ] Each analysis produces valid JSON
- [ ] Temporal analyses include time series data
- [ ] Hierarchy analysis supports drill-down
- [ ] Handle missing data gracefully (no crashes)
- [ ] Generation completes in <5 minutes for 10,000 jobs
- [ ] Outlier detection prevents skewed results
- [ ] Test coverage >80%
- [ ] Documentation for each analysis type

## Integration Points

### Upstream: Databases
- **Contract:** SQLAlchemy models
- **Testing:** Use test databases with sample data

### Downstream: JSON API Files
- **Contract:** JSON schema from JSON generation spec
- **Testing:** Validate JSON structure

### Deployment: Called by JSON Generator
- **Interface:** Python module
- **Error handling:** Graceful fallbacks for missing data

## Open Questions for Implementer

1. How to handle gaps in temporal data (months with no jobs)?
2. Should we normalize salaries to single currency (MDL)?
3. Cache analysis results or recompute daily?
4. What to do if <10 jobs in a category (hide or show anyway)?
5. Include confidence intervals for salary estimates?

## References

- Database schemas: `src/scrape_database.py`, `src/data_database.py`
- Analytics requirements: `ANALYTICS_SPEC.md`
- JSON generation: `02-json-api-generation.md`
- Architecture: `01-architecture-strategy.md`
