"""Employment type and work arrangement analyses."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import (
    JobDetail, EmploymentTypes, RemoteWorkOptions, 
    Benefits, job_benefits
)
from collections import Counter


class EmploymentTypesAnalysis(BaseAnalysis):
    """Employment types distribution analysis."""
    
    @property
    def analysis_id(self):
        return 'employment-types'
    
    @property
    def title(self):
        return 'Employment Types Distribution'
    
    def compute(self):
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.employment_type_id.isnot(None)
        ).all()
        
        if not jobs:
            return {'error': 'No employment type data available'}
        
        # Group by employment type
        grouped = Aggregator.group_by(jobs, lambda j: self._get_employment_type(j))
        
        results = []
        total = len(jobs)
        
        for emp_type, type_jobs in grouped.items():
            results.append({
                'employment_type': emp_type,
                'count': len(type_jobs),
                'percentage': round((len(type_jobs) / total) * 100, 2) if total > 0 else 0
            })
        
        # Sort by count descending
        results.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'employment_types': results,
            'total_jobs': total
        }
    
    def _get_employment_type(self, job):
        """Get employment type name."""
        if job.employment_type_id:
            emp_type = self.data_db.query(EmploymentTypes).filter_by(id=job.employment_type_id).first()
            return emp_type.name if emp_type else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['pie_chart', 'bar_chart', 'donut_chart'],
            'recommended_chart': 'pie_chart'
        }


class RemoteWorkAnalysis(BaseAnalysis):
    """Remote work availability analysis."""
    
    @property
    def analysis_id(self):
        return 'remote-work'
    
    @property
    def title(self):
        return 'Remote Work Availability'
    
    def compute(self):
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.remote_work_id.isnot(None)
        ).all()
        
        if not jobs:
            return {'error': 'No remote work data available'}
        
        # Group by remote work option
        grouped = Aggregator.group_by(jobs, lambda j: self._get_remote_work(j))
        
        results = []
        total = len(jobs)
        
        for remote_option, option_jobs in grouped.items():
            results.append({
                'remote_option': remote_option,
                'count': len(option_jobs),
                'percentage': round((len(option_jobs) / total) * 100, 2) if total > 0 else 0
            })
        
        # Sort by count descending
        results.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'remote_options': results,
            'total_jobs': total
        }
    
    def _get_remote_work(self, job):
        """Get remote work option name."""
        if job.remote_work_id:
            remote = self.data_db.query(RemoteWorkOptions).filter_by(id=job.remote_work_id).first()
            return remote.name if remote else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['pie_chart', 'bar_chart', 'donut_chart'],
            'recommended_chart': 'pie_chart'
        }


class BenefitsAnalysis(BaseAnalysis):
    """Benefits analysis."""
    
    @property
    def analysis_id(self):
        return 'benefits'
    
    @property
    def title(self):
        return 'Most Common Benefits'
    
    def compute(self):
        # Count benefits across all jobs
        benefit_counts = Counter()
        
        jobs = self.data_db.query(JobDetail).all()
        
        for job in jobs:
            # Get benefits for this job through association table
            benefits = self.data_db.query(Benefits).join(
                job_benefits
            ).filter(
                job_benefits.c.job_details_id == job.id
            ).all()
            
            for benefit in benefits:
                benefit_counts[benefit.description] += 1
        
        if not benefit_counts:
            return {'error': 'No benefits data available'}
        
        # Get top benefits
        top_benefits = benefit_counts.most_common(20)
        
        results = []
        total_jobs = len(jobs)
        
        for benefit_desc, count in top_benefits:
            results.append({
                'benefit': benefit_desc,
                'count': count,
                'percentage': round((count / total_jobs) * 100, 2) if total_jobs > 0 else 0
            })
        
        return {
            'top_benefits': results,
            'total_jobs': total_jobs
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'horizontal_bar'],
            'recommended_chart': 'horizontal_bar'
        }


class RequirementsAnalysis(BaseAnalysis):
    """Job requirements overview analysis."""
    
    @property
    def analysis_id(self):
        return 'requirements'
    
    @property
    def title(self):
        return 'Job Requirements Overview'
    
    def compute(self):
        from src.data_database import EducationLevels
        
        jobs = self.data_db.query(JobDetail).all()
        
        if not jobs:
            return {'error': 'No jobs data available'}
        
        # Education requirements
        edu_counts = Counter()
        for job in jobs:
            if job.required_education_id:
                edu = self.data_db.query(EducationLevels).filter_by(id=job.required_education_id).first()
                if edu:
                    edu_counts[edu.name] += 1
        
        edu_results = []
        for edu_name, count in edu_counts.most_common():
            edu_results.append({
                'education_level': edu_name,
                'count': count,
                'percentage': round((count / len(jobs)) * 100, 2)
            })
        
        # Experience requirements
        experience_jobs = [j for j in jobs if j.experience_years is not None]
        experience_ranges = Aggregator.bucket_by_range(
            [float(j.experience_years) for j in experience_jobs],
            [(0, 1), (1, 3), (3, 5), (5, 10), (10, float('inf'))]
        )
        
        return {
            'education_requirements': edu_results,
            'experience_requirements': experience_ranges,
            'total_jobs': len(jobs),
            'jobs_with_experience_req': len(experience_jobs)
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['stacked_bar', 'pie_chart', 'table'],
            'recommended_chart': 'stacked_bar'
        }
