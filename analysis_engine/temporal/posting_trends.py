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
        
        # Filter out the initial bulk import date to avoid bias
        # We'll identify the bulk import date as the date with the highest job count
        date_counts = {}
        for job in jobs:
            if job.created_at:
                date_key = job.created_at.date().isoformat()
                date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        if not date_counts:
            return {'error': 'No valid job creation dates found'}
        
        # Identify bulk import date (highest count)
        bulk_import_date = max(date_counts.items(), key=lambda x: x[1])[0]
        bulk_import_threshold = date_counts[bulk_import_date] * 0.5  # If bulk date has more than 50% of total jobs
        
        # Only filter if bulk import is significant
        filter_bulk = date_counts[bulk_import_date] > len(jobs) * 0.8  # 80% threshold
        
        # Bucket by time period
        periods = self._bucket_by_period(jobs, granularity, filter_bulk_import=filter_bulk)
        
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
            'trends': trend_data,
            'bulk_import_date': bulk_import_date if filter_bulk else None,
            'filtering_applied': filter_bulk
        }
    
    def _bucket_by_period(self, jobs, granularity, filter_bulk_import=False):
        """Group jobs by time period."""
        periods = defaultdict(list)
        
        # Identify bulk import date if filtering is enabled
        if filter_bulk_import:
            date_counts = {}
            for job in jobs:
                if job.created_at:
                    date_key = job.created_at.date().isoformat()
                    date_counts[date_key] = date_counts.get(date_key, 0) + 1
            
            if date_counts:
                bulk_import_date = max(date_counts.items(), key=lambda x: x[1])[0]
            else:
                bulk_import_date = None
        else:
            bulk_import_date = None
        
        for job in jobs:
            if not job.created_at:
                continue
            
            # Skip bulk import date if filtering is enabled
            if filter_bulk_import and bulk_import_date:
                job_date = job.created_at.date().isoformat()
                if job_date == bulk_import_date:
                    continue  # Skip jobs from bulk import date
            
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
