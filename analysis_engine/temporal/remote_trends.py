"""Remote work adoption trends analysis."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import JobDetail, RemoteWorkOptions
from src.scrape_database import Job
from collections import defaultdict, Counter


class RemoteTrendsAnalysis(BaseAnalysis):
    """Remote work adoption trends over time."""
    
    @property
    def analysis_id(self):
        return 'remote-work-trends'
    
    @property
    def title(self):
        return 'Remote Work Adoption Trends'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        granularity = self.config.GRANULARITY
        
        # Get all jobs with remote work data
        jobs_data = self.data_db.query(JobDetail).filter(
            JobDetail.remote_work_id.isnot(None)
        ).all()
        
        if not jobs_data:
            return {'error': 'No remote work data available'}
        
        # Map job_url to JobDetail
        job_detail_map = {jd.job_url: jd for jd in jobs_data}
        
        # Get corresponding Job records from scrape.db for timestamps
        jobs_scrape = self.scrape_db.query(Job).filter(
            Job.job_url.in_(job_detail_map.keys())
        ).all()
        
        # Bucket by time period
        periods = defaultdict(Counter)
        
        for job in jobs_scrape:
            if not job.created_at or job.job_url not in job_detail_map:
                continue
            
            job_detail = job_detail_map[job.job_url]
            remote_option = self._get_remote_work(job_detail)
            
            if not remote_option:
                continue
            
            period_key = Aggregator.get_period_key(job.created_at, granularity)
            periods[period_key][remote_option] += 1
        
        if not periods:
            return {'error': 'No remote work trend data available'}
        
        # Build trend data
        trend_data = []
        
        for period, remote_counts in sorted(periods.items()):
            total = sum(remote_counts.values())
            
            period_data = {
                'period': period,
                'total_jobs': total
            }
            
            for remote_option, count in remote_counts.items():
                period_data[remote_option] = {
                    'count': count,
                    'percentage': round((count / total) * 100, 2) if total > 0 else 0
                }
            
            trend_data.append(period_data)
        
        return {
            'granularity': granularity,
            'remote_trends': trend_data
        }
    
    def _get_remote_work(self, job):
        """Get remote work option name."""
        if job.remote_work_id:
            remote = self.data_db.query(RemoteWorkOptions).filter_by(id=job.remote_work_id).first()
            return remote.name if remote else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['stacked_area', 'line_chart', 'stacked_bar'],
            'recommended_chart': 'stacked_area'
        }
