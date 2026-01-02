"""Skills demand trends analysis."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import JobDetail, HardSkills, job_hard_skills
from src.scrape_database import Job
from collections import defaultdict, Counter


class SkillsTrendsAnalysis(BaseAnalysis):
    """Skills demand trends over time."""
    
    @property
    def analysis_id(self):
        return 'skills-trends'
    
    @property
    def title(self):
        return 'Skills Demand Trends Over Time'
    
    @property
    def is_temporal(self):
        return True
    
    def compute(self):
        granularity = self.config.GRANULARITY
        
        # Get all jobs
        jobs_data = self.data_db.query(JobDetail).all()
        
        if not jobs_data:
            return {'error': 'No jobs data available'}
        
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
        
        # Bucket skills by time period
        periods = defaultdict(Counter)
        
        for job in filtered_jobs:
            if not job.created_at or job.job_url not in job_detail_map:
                continue
            
            job_detail = job_detail_map[job.job_url]
            period_key = Aggregator.get_period_key(job.created_at, granularity)
            
            # Get skills for this job
            skills = self.data_db.query(HardSkills).join(
                job_hard_skills
            ).filter(
                job_hard_skills.c.job_details_id == job_detail.id
            ).all()
            
            for skill in skills:
                periods[period_key][skill.name] += 1
        
        if not periods:
            return {'error': 'No skills trend data available'}
        
        # Find top skills across all periods
        all_skills = Counter()
        for period_skills in periods.values():
            all_skills.update(period_skills)
        
        top_skill_names = [skill for skill, _ in all_skills.most_common(10)]
        
        # Build trend data for top skills
        trends = {skill: [] for skill in top_skill_names}
        
        for period, period_skills in sorted(periods.items()):
            total_jobs = sum(period_skills.values())
            
            for skill_name in top_skill_names:
                count = period_skills.get(skill_name, 0)
                trends[skill_name].append({
                    'period': period,
                    'count': count,
                    'percentage': round((count / total_jobs) * 100, 2) if total_jobs > 0 else 0
                })
        
        return {
            'granularity': granularity,
            'skill_trends': trends,
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
            'chart_types': ['line_chart', 'multi_line_chart'],
            'recommended_chart': 'multi_line_chart'
        }
