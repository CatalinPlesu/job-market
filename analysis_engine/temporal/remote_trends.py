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
        
        # Filter out bulk import to avoid bias
        filtered_jobs = self._filter_bulk_import(jobs_scrape)
        if not filtered_jobs:
            return {'error': 'No valid job data after filtering bulk import'}
        
        # Bucket by time period
        periods = defaultdict(Counter)
        
        for job in filtered_jobs:
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
            'remote_trends': trend_data,
            'data_quality': {
                'total_jobs_before_filtering': len(jobs_scrape),
                'jobs_after_filtering': len(filtered_jobs),
                'filtering_applied': len(filtered_jobs) != len(jobs_scrape)
            }
        }
    
    def _get_remote_work(self, job):
        """Get remote work option name."""
        if job.remote_work_id:
            remote = self.data_db.query(RemoteWorkOptions).filter_by(id=job.remote_work_id).first()
            return remote.name if remote else None
        return None
    
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
            'chart_types': ['stacked_area', 'line_chart', 'stacked_bar'],
            'recommended_chart': 'stacked_area'
        }
