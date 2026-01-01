"""Job posting volume trends analysis."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.scrape_database import Job, JobCheck
from datetime import datetime
from collections import defaultdict


class PostingTrendsAnalysis(BaseAnalysis):
    """Job posting volume over time."""
    
    @property
    def analysis_id(self):
        return 'posting-trends'
    
    @property
    def title(self):
        return 'Job Posting Volume Trends'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        granularity = self.config.GRANULARITY
        
        # Get all jobs with creation dates
        jobs = self.scrape_db.query(Job).all()
        
        if not jobs:
            return {'error': 'No jobs data available'}
        
        # Bucket by time period
        periods = self._bucket_by_period(jobs, granularity)
        
        # Compute statistics per period
        trend_data = []
        for period, period_jobs in sorted(periods.items()):
            new_jobs = len(period_jobs)
            
            # Count jobs that closed in this period
            closed_jobs = self._count_closed_in_period(period_jobs, period)
            active_jobs = new_jobs - closed_jobs
            
            trend_data.append({
                'period': period,
                'new_jobs': new_jobs,
                'closed_jobs': closed_jobs,
                'net_change': active_jobs
            })
        
        return {
            'granularity': granularity,
            'trends': trend_data
        }
    
    def _bucket_by_period(self, jobs, granularity):
        """Group jobs by time period."""
        periods = defaultdict(list)
        
        for job in jobs:
            if not job.created_at:
                continue
            
            period_key = Aggregator.get_period_key(job.created_at, granularity)
            periods[period_key].append(job)
        
        return periods
    
    def _count_closed_in_period(self, jobs, period):
        """Count how many jobs closed in this period."""
        count = 0
        for job in jobs:
            # Check job_checks to find when job died
            if not job.checks:
                continue
            
            # Get the first failed check (http_status != 200)
            for check in Aggregator.sort_checks_by_date(job.checks):
                if check.http_status and check.http_status != 200:
                    check_period = Aggregator.get_period_key(check.check_date, self.config.GRANULARITY)
                    if check_period == period:
                        count += 1
                    break
        
        return count
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['line_chart', 'area_chart', 'bar_chart'],
            'recommended_chart': 'line_chart'
        }
