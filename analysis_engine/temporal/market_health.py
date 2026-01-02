"""Market health and job duration analyses."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.scrape_database import Job, JobCheck
from src.data_database import JobDetail
from datetime import datetime, timedelta
from collections import defaultdict


class JobDurationAnalysis(BaseAnalysis):
    """Job duration (time to fill) analysis."""
    
    @property
    def analysis_id(self):
        return 'job-duration'
    
    @property
    def title(self):
        return 'Job Duration Analysis (Time to Fill)'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        # Get all jobs with checks
        jobs = self.scrape_db.query(Job).all()
        
        durations = []
        long_running = []  # Jobs open for >90 days
        
        for job in jobs:
            if not job.created_at or not job.checks:
                continue
            
            # Find when job closed (first non-200 status)
            closed_date = None
            for check in Aggregator.sort_checks_by_date(job.checks):
                if check.http_status and check.http_status != 200:
                    closed_date = check.check_date
                    break
            
            if closed_date:
                # Job closed
                # Ensure both are dates for subtraction
                closed_as_date = closed_date if isinstance(closed_date, datetime) else datetime.combine(closed_date, datetime.min.time())
                created_as_date = job.created_at if isinstance(job.created_at, datetime) else datetime.combine(job.created_at, datetime.min.time())
                duration_days = (closed_as_date.date() - created_as_date.date()).days
                durations.append(duration_days)
                
                if duration_days > 90:
                    long_running.append({
                        'job_title': job.job_title,
                        'company': job.company_name,
                        'duration_days': duration_days
                    })
            else:
                # Job still open - calculate current duration using generation timestamp
                created_as_date = job.created_at if isinstance(job.created_at, datetime) else datetime.combine(job.created_at, datetime.min.time())
                current_duration = (self.generated_at.date() - created_as_date.date()).days
                if current_duration > 90:
                    long_running.append({
                        'job_title': job.job_title,
                        'company': job.company_name,
                        'duration_days': current_duration,
                        'status': 'still_open'
                    })
        
        if not durations:
            return {'error': 'No job duration data available'}
        
        # Compute statistics
        duration_stats = Aggregator.compute_stats(durations)
        
        # Bucket durations
        duration_ranges = Aggregator.bucket_by_range(
            durations,
            [(0, 7), (7, 14), (14, 30), (30, 60), (60, 90), (90, float('inf'))]
        )
        
        return {
            'duration_stats': duration_stats,
            'duration_distribution': duration_ranges,
            'long_running_jobs': long_running[:50]  # Top 50
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['histogram', 'box_plot', 'table'],
            'recommended_chart': 'histogram'
        }


class MarketHealthAnalysis(BaseAnalysis):
    """Market health indicators over time."""
    
    @property
    def analysis_id(self):
        return 'market-health'
    
    @property
    def title(self):
        return 'Market Health Indicators'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        granularity = self.config.GRANULARITY
        
        # Get all jobs
        jobs = self.scrape_db.query(Job).all()
        
        if not jobs:
            return {'error': 'No jobs data available'}
        
        # Filter out bulk import to avoid bias in market health trends
        filtered_jobs = self._filter_bulk_import(jobs)
        if not filtered_jobs:
            return {'error': 'No valid job data after filtering bulk import'}
        
        # Track active/closed jobs per period
        periods = defaultdict(lambda: {'new': 0, 'closed': 0, 'active': 0})
        
        for job in filtered_jobs:
            if not job.created_at:
                continue
            
            # Count as new in creation period
            created_period = Aggregator.get_period_key(job.created_at, granularity)
            periods[created_period]['new'] += 1
            
            # Check if/when job closed
            closed = False
            closed_date = None
            
            if job.checks:
                for check in Aggregator.sort_checks_by_date(job.checks):
                    if check.http_status and check.http_status != 200:
                        closed = True
                        closed_date = check.check_date
                        break
            
            if closed and closed_date:
                closed_period = Aggregator.get_period_key(closed_date, granularity)
                periods[closed_period]['closed'] += 1
        
        # Calculate cumulative active jobs
        cumulative_active = 0
        trend_data = []
        
        for period in sorted(periods.keys()):
            data = periods[period]
            cumulative_active += data['new'] - data['closed']
            
            trend_data.append({
                'period': period,
                'new_jobs': data['new'],
                'closed_jobs': data['closed'],
                'net_change': data['new'] - data['closed'],
                'cumulative_active': max(0, cumulative_active)
            })
        
        # Calculate growth rate
        for i in range(1, len(trend_data)):
            prev = trend_data[i-1]['cumulative_active']
            curr = trend_data[i]['cumulative_active']
            if prev > 0:
                trend_data[i]['growth_rate'] = round(((curr - prev) / prev) * 100, 2)
            else:
                trend_data[i]['growth_rate'] = 0
        
        return {
            'granularity': granularity,
            'market_trends': trend_data,
            'data_quality': {
                'total_jobs_before_filtering': len(jobs),
                'jobs_after_filtering': len(filtered_jobs),
                'filtering_applied': len(filtered_jobs) != len(jobs)
            }
        }
    
    def _filter_bulk_import(self, jobs):
        """Filter out bulk import jobs to avoid bias in trends."""
        if not jobs:
            return []
        
        # Count jobs by date
        date_counts = {}
        for job in jobs:
            if job.created_at:
                date_key = job.created_at.date().isoformat()
                date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        if not date_counts:
            return jobs
        
        # Identify bulk import date
        bulk_import_date = max(date_counts.items(), key=lambda x: x[1])[0]
        total_jobs = len(jobs)
        bulk_job_count = date_counts[bulk_import_date]
        
        # Only filter if bulk import represents a significant portion
        bulk_threshold = 0.8  # 80% threshold
        
        if bulk_job_count > total_jobs * bulk_threshold:
            # Filter out bulk import date
            filtered_jobs = []
            for job in jobs:
                if job.created_at:
                    job_date = job.created_at.date().isoformat()
                    if job_date != bulk_import_date:
                        filtered_jobs.append(job)
                else:
                    filtered_jobs.append(job)
            return filtered_jobs
        
        return jobs
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['line_chart', 'area_chart', 'stacked_area'],
            'recommended_chart': 'line_chart'
        }
