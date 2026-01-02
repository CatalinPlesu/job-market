"""Salary evolution trends analysis."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import JobDetail
from src.scrape_database import Job
from collections import defaultdict


class SalaryTrendsAnalysis(BaseAnalysis):
    """Salary evolution over time."""
    
    @property
    def analysis_id(self):
        return 'salary-trends'
    
    @property
    def title(self):
        return 'Salary Evolution Over Time'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        granularity = self.config.GRANULARITY
        
        # Get all jobs with salary data
        jobs_data = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None)
        ).all()
        
        if not jobs_data:
            return {'error': 'No salary data available'}
        
        # Map job_url to JobDetail
        job_detail_map = {jd.job_url: jd for jd in jobs_data}
        
        # Get corresponding Job records from scrape.db for timestamps
        jobs_scrape = self.scrape_db.query(Job).filter(
            Job.job_url.in_(job_detail_map.keys())
        ).all()
        
        # Filter out bulk import to avoid bias
        filtered_jobs = self._filter_bulk_import(jobs_scrape)
        if not filtered_jobs:
            return {'error': 'No valid job data after filtering bulk import'}
        
        # Bucket by time period
        periods = defaultdict(list)
        
        for job in filtered_jobs:
            if not job.created_at or job.job_url not in job_detail_map:
                continue
            
            job_detail = job_detail_map[job.job_url]
            salary = Aggregator.get_average_salary(job_detail)
            
            if not salary:
                continue
            
            period_key = Aggregator.get_period_key(job.created_at, granularity)
            periods[period_key].append(salary)
        
        # Compute statistics per period
        trend_data = []
        for period, salaries in sorted(periods.items()):
            if len(salaries) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['period'] = period
                trend_data.append(stats)
        
        return {
            'granularity': granularity,
            'salary_trends': trend_data,
            'data_quality': {
                'total_jobs_before_filtering': len(jobs_scrape),
                'jobs_after_filtering': len(filtered_jobs),
                'filtering_applied': len(filtered_jobs) != len(jobs_scrape)
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
            'chart_types': ['line_chart', 'area_chart'],
            'recommended_chart': 'line_chart'
        }
