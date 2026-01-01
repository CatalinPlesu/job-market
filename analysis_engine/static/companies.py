"""Company-related analyses."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import JobDetail, Companies
from collections import Counter


class TopCompaniesAnalysis(BaseAnalysis):
    """Top hiring companies analysis."""
    
    @property
    def analysis_id(self):
        return 'top-companies'
    
    @property
    def title(self):
        return 'Top Hiring Companies'
    
    def compute(self):
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.company_name_id.isnot(None)
        ).all()
        
        if not jobs:
            return {'error': 'No company data available'}
        
        # Count jobs per company
        company_counts = Counter()
        for job in jobs:
            company = self._get_company(job)
            if company:
                company_counts[company] += 1
        
        # Get top N companies
        top_companies = company_counts.most_common(self.config.TOP_N_COMPANIES)
        
        results = []
        total_jobs = len(jobs)
        
        for company_name, count in top_companies:
            results.append({
                'company': company_name,
                'job_count': count,
                'percentage': round((count / total_jobs) * 100, 2) if total_jobs > 0 else 0
            })
        
        return {
            'top_companies': results,
            'total_jobs': total_jobs,
            'total_companies': len(company_counts)
        }
    
    def _get_company(self, job):
        """Get company name."""
        if job.company_name_id:
            company = self.data_db.query(Companies).filter_by(id=job.company_name_id).first()
            return company.name if company else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'horizontal_bar', 'table'],
            'recommended_chart': 'horizontal_bar'
        }
