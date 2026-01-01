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
        
        # Bucket by time period
        periods = defaultdict(list)
        
        for job in jobs_scrape:
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
            'salary_trends': trend_data
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['line_chart', 'area_chart'],
            'recommended_chart': 'line_chart'
        }
